"""Test module for CLI commands using simplified test data."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine, select

from biokb_wfo.cli import create_ttls, import_data, import_neo4j, main, run_server
from biokb_wfo.db.models import Base, Name


@pytest.fixture
def test_data_folder():
    """Return path to test data folder."""
    return str(Path(__file__).parent / "data")


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        conn_str = f"sqlite:///{db_path}"
        yield conn_str, tmpdir


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestImportDataCommand:
    """Test import-data CLI command."""

    def test_import_data_basic(self, runner, temp_db, test_data_folder):
        """Test basic import-data command."""
        conn_str, tmpdir = temp_db

        # Patch the DbManager to use test data folder
        with patch("biokb_wfo.cli.DbManager") as mock_manager:
            mock_instance = MagicMock()
            mock_instance.import_data.return_value = {"name": 10}
            mock_manager.return_value = mock_instance

            result = runner.invoke(
                import_data,
                ["-c", conn_str],
            )

            assert result.exit_code == 0
            assert "Data imported successfully" in result.output
            mock_instance.import_data.assert_called_once()

    def test_import_data_with_force_download(self, runner, temp_db):
        """Test import-data with force-download flag."""
        conn_str, tmpdir = temp_db

        with patch("biokb_wfo.cli.DbManager") as mock_manager:
            mock_instance = MagicMock()
            mock_instance.import_data.return_value = {"name": 10}
            mock_manager.return_value = mock_instance

            result = runner.invoke(
                import_data,
                ["-c", conn_str, "-f"],
            )

            assert result.exit_code == 0
            # Verify force_download was True
            call_args = mock_instance.import_data.call_args
            assert call_args[1]["force_download"] is True

    def test_import_data_with_delete_files(self, runner, temp_db):
        """Test import-data with delete-files flag."""
        conn_str, tmpdir = temp_db

        with patch("biokb_wfo.cli.DbManager") as mock_manager:
            mock_instance = MagicMock()
            mock_instance.import_data.return_value = {"name": 10}
            mock_manager.return_value = mock_instance

            result = runner.invoke(
                import_data,
                ["-c", conn_str, "-d"],
            )

            assert result.exit_code == 0
            # Verify delete_files was True
            call_args = mock_instance.import_data.call_args
            assert call_args[1]["delete_files"] is True


class TestCreateTtlsCommand:
    """Test create-ttls CLI command."""

    def test_create_ttls_basic(self, runner, temp_db):
        """Test basic create-ttls command."""
        conn_str, tmpdir = temp_db

        with patch("biokb_wfo.cli.TurtleCreator") as mock_creator:
            mock_instance = MagicMock()
            mock_instance.create_ttls.return_value = "/path/to/ttls.zip"
            mock_creator.return_value = mock_instance

            result = runner.invoke(
                create_ttls,
                ["-c", conn_str],
            )

            assert result.exit_code == 0
            assert "Path to the zip file" in result.output
            assert "/path/to/ttls.zip" in result.output
            mock_instance.create_ttls.assert_called_once()

    def test_create_ttls_with_custom_connection(self, runner):
        """Test create-ttls with custom connection string."""
        custom_conn = "sqlite:///custom.db"

        with patch("biokb_wfo.cli.TurtleCreator") as mock_creator:
            mock_instance = MagicMock()
            mock_instance.create_ttls.return_value = "/path/to/ttls.zip"
            mock_creator.return_value = mock_instance

            result = runner.invoke(
                create_ttls,
                ["-c", custom_conn],
            )

            assert result.exit_code == 0
            # Verify the engine was created with custom connection
            call_args = mock_creator.call_args[0]
            assert str(call_args[0].url) == custom_conn


class TestImportNeo4jCommand:
    """Test import-neo4j CLI command."""

    def test_import_neo4j_with_password_prompt(self, runner):
        """Test import-neo4j with password prompt."""
        with patch("biokb_wfo.cli.Neo4jImporter") as mock_importer:
            mock_instance = MagicMock()
            mock_importer.return_value = mock_instance

            result = runner.invoke(
                import_neo4j,
                input="test_password\n",
            )

            assert result.exit_code == 0
            # Verify Neo4jImporter was called with password
            call_args = mock_importer.call_args[1]
            assert call_args["neo4j_pwd"] == "test_password"
            mock_instance.import_ttls.assert_called_once()

    def test_import_neo4j_with_password_flag(self, runner):
        """Test import-neo4j with password provided via flag."""
        with patch("biokb_wfo.cli.Neo4jImporter") as mock_importer:
            mock_instance = MagicMock()
            mock_importer.return_value = mock_instance

            result = runner.invoke(
                import_neo4j,
                ["-p", "test_password"],
            )

            assert result.exit_code == 0
            assert "not recommended" in result.output
            call_args = mock_importer.call_args[1]
            assert call_args["neo4j_pwd"] == "test_password"

    def test_import_neo4j_custom_uri_and_user(self, runner):
        """Test import-neo4j with custom URI and user."""
        custom_uri = "bolt://custom:7687"
        custom_user = "custom_user"

        with patch("biokb_wfo.cli.Neo4jImporter") as mock_importer:
            mock_instance = MagicMock()
            mock_importer.return_value = mock_instance

            result = runner.invoke(
                import_neo4j,
                ["-i", custom_uri, "-u", custom_user, "-p", "test_password"],
            )

            assert result.exit_code == 0
            call_args = mock_importer.call_args[1]
            assert call_args["neo4j_uri"] == custom_uri
            assert call_args["neo4j_user"] == custom_user


class TestRunServerCommand:
    """Test run-server CLI command."""

    def test_run_server_basic(self, runner):
        """Test basic run-server command."""
        with patch("biokb_wfo.cli.run_api") as mock_run_api:
            # Simulate KeyboardInterrupt to exit the server
            mock_run_api.side_effect = KeyboardInterrupt()

            result = runner.invoke(
                run_server,
                [],
                catch_exceptions=True,
            )

            # The command should have attempted to start the server
            assert "API server running at" in result.output
            mock_run_api.assert_called_once()

    def test_run_server_custom_host_and_port(self, runner):
        """Test run-server with custom host and port."""
        with patch("biokb_wfo.cli.run_api") as mock_run_api:
            mock_run_api.side_effect = KeyboardInterrupt()

            result = runner.invoke(
                run_server,
                ["-h", "localhost", "-P", "9000"],
                catch_exceptions=True,
            )

            assert "localhost:9000" in result.output
            call_args = mock_run_api.call_args[1]
            assert call_args["host"] == "localhost"
            assert call_args["port"] == 9000

    def test_run_server_custom_credentials(self, runner):
        """Test run-server with custom username and password."""
        with patch("biokb_wfo.cli.run_api") as mock_run_api:
            mock_run_api.side_effect = KeyboardInterrupt()

            runner.invoke(
                run_server,
                ["-u", "testuser", "-p", "testpass"],
                catch_exceptions=True,
            )

            # Verify environment variables were set
            assert os.environ.get("API_USER") == "testuser"
            assert os.environ.get("API_PASSWORD") == "testpass"

    def test_run_server_displays_127_for_all_interfaces(self, runner):
        """Test that 0.0.0.0 is displayed as 127.0.0.1."""
        with patch("biokb_wfo.cli.run_api") as mock_run_api:
            mock_run_api.side_effect = KeyboardInterrupt()

            result = runner.invoke(
                run_server,
                ["-h", "0.0.0.0"],
                catch_exceptions=True,
            )

            # 0.0.0.0 should be displayed as 127.0.0.1 to user
            assert "127.0.0.1:8000" in result.output


class TestMainCommand:
    """Test main CLI entry point."""

    def test_main_help(self, runner):
        """Test main command help."""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Import in RDBMS" in result.output
        assert "import-data" in result.output
        assert "create-ttls" in result.output
        assert "import-neo4j" in result.output
        assert "run-server" in result.output

    def test_main_version(self, runner):
        """Test main command version."""
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        # Version should be displayed

    def test_main_subcommands_available(self, runner):
        """Test that all subcommands are registered."""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "import-data" in result.output
        assert "create-ttls" in result.output
        assert "import-neo4j" in result.output
        assert "run-server" in result.output


class TestIntegrationWithTestData:
    """Integration tests using actual test data."""

    def test_full_import_workflow(self, runner, temp_db, test_data_folder):
        """Test complete import workflow with real test data."""
        conn_str, tmpdir = temp_db

        # Create engine and setup database
        engine = create_engine(conn_str)
        Base.metadata.create_all(engine)

        # Patch DATA_FOLDER to use test data
        with patch("biokb_wfo.db.manager.DATA_FOLDER", test_data_folder):
            result = runner.invoke(
                import_data,
                ["-c", conn_str],
            )

        # Check that import succeeded
        assert result.exit_code == 0

        # Verify data was imported
        from sqlalchemy.orm import Session

        with Session(engine) as session:
            names = session.execute(select(Name)).scalars().all()
            assert len(names) == 10  # Our simplified data has 10 entries

            # Verify specific entries
            rosa_canina = session.execute(
                select(Name).where(Name.name == "Rosa canina")
            ).scalar_one_or_none()
            assert rosa_canina is not None
            assert rosa_canina.rank == "species"

    def test_logging_verbose_mode(self, runner, temp_db):
        """Test that verbose logging works."""
        conn_str, tmpdir = temp_db

        with patch("biokb_wfo.cli.DbManager") as mock_manager:
            mock_instance = MagicMock()
            mock_instance.import_data.return_value = {"name": 10}
            mock_manager.return_value = mock_instance

            # Test with -v flag
            result = runner.invoke(
                main,
                ["-v", "import-data", "-c", conn_str],
            )

            assert result.exit_code == 0

    def test_double_verbose_mode(self, runner, temp_db):
        """Test that double verbose (-vv) enables debug logging."""
        conn_str, tmpdir = temp_db

        with patch("biokb_wfo.cli.DbManager") as mock_manager:
            mock_instance = MagicMock()
            mock_instance.import_data.return_value = {"name": 10}
            mock_manager.return_value = mock_instance

            # Test with -vv flag
            result = runner.invoke(
                main,
                ["-vv", "import-data", "-c", conn_str],
            )

            assert result.exit_code == 0
