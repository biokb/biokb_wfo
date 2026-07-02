import logging
import os
from logging import Logger
from typing import Optional

import click
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from biokb_wfo import __version__
from biokb_wfo.api.main import run_api
from biokb_wfo.constants import DB_DEFAULT_CONNECTION_STR, NEO4J_URI, NEO4J_USER
from biokb_wfo.db.manager import DbManager
from biokb_wfo.rdf.neo4j_importer import Neo4jImporter
from biokb_wfo.rdf.turtle import TurtleCreator

logger: Logger = logging.getLogger("biokb_wfo")


def _setup_default_cli_logging() -> None:
    package_logger = logging.getLogger("biokb_wfo")

    has_cli_handler = any(
        getattr(handler, "_biokb_cli_handler", False)
        for handler in package_logger.handlers
    )
    if not has_cli_handler:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        )
        setattr(stream_handler, "_biokb_cli_handler", True)
        package_logger.addHandler(stream_handler)

    package_logger.setLevel(logging.INFO)
    package_logger.propagate = False


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Import in RDBMS, create turtle files and import into Neo4J.

    Please follow the steps:\n
    1. Import data using `import-data` command.\n
    2. Create TTL files using `create-ttls` command.\n
    3. Import TTL files into Neo4j using `import-neo4j` command.\n
    """
    _setup_default_cli_logging()


@main.command("import-data")
@click.option(
    "-f",
    "--force-download",
    is_flag=True,
    type=bool,
    default=False,
    help="Force re-download of the source file [default: False]",
)
@click.option(
    "-d",
    "--delete-files",
    is_flag=True,
    type=bool,
    default=False,
    help="Delete downloaded source files after import [default: False]",
)
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=None,
    help="SQLAlchemy engine URL",
)
@click.option(
    "-e",
    "--env",
    type=str,
    default=None,
    help="Environment file to load for configuration (default: None)",
)
def import_data(
    force_download: bool,
    delete_files: bool,
    connection_string: str | None,
    env: Optional[str] = None,
) -> None:
    """Import data."""
    if env:
        if connection_string:
            logger.warning(
                "Both environment file and connection string provided. Environment have priority."
            )
        if not os.path.exists(env):
            logger.error("Environment file %s not found.", env)
            return
        load_dotenv(env, override=True)
        connection_string = os.getenv("CONNECTION_STR")
        if connection_string is None:
            logger.warning(
                "CONNECTION_STR environment variable not found. Using default connection string."
            )

    engine: Engine | None = (
        create_engine(connection_string) if connection_string else None
    )
    DbManager(engine=engine).import_data(
        force_download=force_download, delete_files=delete_files
    )


@main.command("create-ttls")
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=DB_DEFAULT_CONNECTION_STR,
    help=f"SQLAlchemy engine URL [default: {DB_DEFAULT_CONNECTION_STR}]",
)
def create_ttls(connection_string: str) -> None:
    """Create TTL files from local database."""
    path_to_zip = TurtleCreator(create_engine(connection_string)).create_ttls()
    click.echo(
        f"Path to the zip file containing all generated Turtle files. {path_to_zip}"
    )


neo4j_uri = os.getenv("NEO4J_URI", NEO4J_URI)
neo4j_user = os.getenv("NEO4J_USER", NEO4J_USER)


@main.command("import-neo4j")
@click.option(
    "--uri",
    "-i",
    default=neo4j_uri,
    help=f'Neo4j database URI [default:"{neo4j_uri}"]',
)
@click.option(
    "--user", "-u", default=neo4j_user, help=f'Neo4j username [default="{neo4j_user}"]'
)
@click.option("--password", "-p", default=None, help="Neo4j password")
def import_neo4j(uri: str, user: str, password: Optional[str]) -> None:
    """Import TTL files into Neo4j database."""
    if password is None:
        password = click.prompt(
            "Please enter the Neo4j password (input will be hidden)", hide_input=True
        )
    else:
        click.echo(
            "It is not recommended to provide the Neo4j password via command line."
        )
    Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password).import_ttls()


@main.command("run-server")
@click.option(
    "--host", "-h", default="0.0.0.0", help="API server host [default: 0.0.0.0]"
)
@click.option("--port", "-P", default=8000, help="API server port [default: 8000]")
@click.option("--user", "-u", default="admin", help="API username [default=admin]")
@click.option("--password", "-p", default="admin", help="API password [default: admin]")
def run_server(host: str, port: int, user: str, password: str) -> None:
    """Run the API server.

    Args:
        host (str): API server host
        port (int): API server port
        user (str): API username
        password (str): API password
    """
    # set env variables for API authentication
    os.environ["API_USER"] = user
    os.environ["API_PASSWORD"] = password
    host_shown = "127.0.0.1" if host == "0.0.0.0" else host
    click.echo(f"API server running at http://{host_shown}:{port}/docs#/")
    run_api(host=host, port=port)


if __name__ == "__main__":
    main()
