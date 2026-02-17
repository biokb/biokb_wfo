"""Test module for DbManager using simplified test data."""

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select

from biokb_wfo.db.manager import DbManager
from biokb_wfo.db.models import (
    Base,
    Code,
    Family,
    Genus,
    Kingdom,
    Name,
    Phylum,
    Species,
    Variety,
)


@pytest.fixture
def test_data_folder():
    """Return path to test data folder."""
    return str(Path(__file__).parent / "data")


@pytest.fixture
def test_engine():
    """Create a temporary SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)

    # Clean up - dispose engine after tests complete
    engine.dispose()


@pytest.fixture
def db_manager(test_engine, test_data_folder):
    """Create DbManager with test data folder."""
    manager = DbManager(engine=test_engine)
    manager._set_data_folder(test_data_folder)
    return manager


class TestDbManager:
    """Test DbManager functionality."""

    def test_import_data_from_test_file(self, db_manager, test_engine):
        """Test importing data from simplified test file."""
        # Import data using the test data
        result = db_manager.import_data(force_download=False, delete_files=False)

        # Verify counts
        assert "name" in result
        assert result["name"] == 10  # We have 10 entries in simplified data

        # Verify taxonomic hierarchy tables were created
        assert "code" in result
        assert "kingdom" in result
        assert "phylum" in result
        assert "family" in result
        assert "genus" in result
        assert "species" in result
        assert "variety" in result

    def test_place_in_data_insertion(self, db_manager, test_engine):
        """Test that PLACE_IN_FIELDS data is correctly inserted."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            # Check code table
            codes = session.execute(select(Code)).scalars().all()
            assert len(codes) == 1
            assert codes[0].name == "ICN"

            # Check kingdom table
            kingdoms = session.execute(select(Kingdom)).scalars().all()
            assert len(kingdoms) == 1
            assert kingdoms[0].name == "Plantae"

            # Check phylum table
            phylums = session.execute(select(Phylum)).scalars().all()
            assert len(phylums) == 1
            assert phylums[0].name == "Tracheophyta"

            # Check family table
            families = session.execute(select(Family)).scalars().all()
            assert len(families) == 1
            assert families[0].name == "Rosaceae"

            # Check genus table
            genera = session.execute(select(Genus)).scalars().all()
            assert len(genera) == 1
            assert genera[0].name == "Rosa"

            # Check species table
            species_list = session.execute(select(Species)).scalars().all()
            assert len(species_list) >= 3  # Rosa canina, Rosa rugosa, Rosa alba

            # Check variety table
            varieties = session.execute(select(Variety)).scalars().all()
            assert len(varieties) == 1
            assert varieties[0].name == "Rosa canina var. dumalis"

    def test_name_data_insertion(self, db_manager, test_engine):
        """Test that name data is correctly inserted with proper relationships."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            # Get all names
            names = session.execute(select(Name)).scalars().all()
            assert len(names) == 10

            # Check specific name: Rosa canina
            rosa_canina = session.execute(
                select(Name).where(Name.name == "Rosa canina")
            ).scalar_one()

            assert rosa_canina.full_name_plain == "Rosa canina L."
            assert rosa_canina.rank == "species"
            assert rosa_canina.status == "valid"
            assert rosa_canina.role == "accepted"
            assert rosa_canina.genus_string == "Rosa"
            assert rosa_canina.species_string == "canina"
            assert rosa_canina.year == 1753
            assert rosa_canina.ipni == "720955-1"

            # Check parent relationship
            assert rosa_canina.parent_id == "4000012345"

            # Check foreign key relationships
            assert rosa_canina.kingdom_id is not None
            assert rosa_canina.phylum_id is not None
            assert rosa_canina.family_id is not None
            assert rosa_canina.genus_id is not None
            assert rosa_canina.species_id is not None

    def test_synonym_insertion(self, db_manager, test_engine):
        """Test that synonyms are correctly identified."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            # Rosa alba is a synonym
            rosa_alba = session.execute(
                select(Name).where(Name.name == "Rosa alba")
            ).scalar_one()

            assert rosa_alba.role == "synonym"
            assert rosa_alba.status == "invalid"

    def test_variety_insertion(self, db_manager, test_engine):
        """Test that varieties are correctly inserted."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            # Rosa canina var. dumalis is a variety
            variety = session.execute(
                select(Name).where(Name.name == "Rosa canina var. dumalis")
            ).scalar_one()

            assert variety.rank == "variety"
            assert variety.role == "accepted"
            assert variety.parent_id == "123456"  # Parent is Rosa canina

    def test_hierarchical_structure(self, db_manager, test_engine):
        """Test that the taxonomic hierarchy is properly maintained."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            # Check the hierarchy: Code -> Kingdom -> Phylum -> Class
            # -> Family -> Genus -> Species

            # Get ICN (code)
            code = session.execute(select(Name).where(Name.rank == "code")).scalar_one()
            assert code.name == "ICN"

            # Get Plantae (kingdom)
            kingdom = session.execute(
                select(Name).where(Name.rank == "kingdom")
            ).scalar_one()
            assert kingdom.name == "Plantae"
            assert kingdom.parent_id == "9971000003"  # Parent is ICN

            # Get Family
            family = session.execute(
                select(Name).where(Name.rank == "family")
            ).scalar_one()
            assert family.name == "Rosaceae"

            # Get Genus
            genus = session.execute(
                select(Name).where(Name.rank == "genus")
            ).scalar_one()
            assert genus.name == "Rosa"
            assert genus.parent_id == "7000000488"  # Parent is Rosaceae

    def test_cache_ids(self, db_manager, test_engine):
        """Test that cache_ids are properly populated."""
        db_manager.import_data(force_download=False, delete_files=False)

        # Check that cache_ids were populated
        assert "code" in db_manager.cache_ids
        assert "kingdom" in db_manager.cache_ids
        assert "phylum" in db_manager.cache_ids
        assert "family" in db_manager.cache_ids
        assert "genus" in db_manager.cache_ids

        # Verify specific entries
        assert "ICN" in db_manager.cache_ids["code"]
        assert "Plantae" in db_manager.cache_ids["kingdom"]
        assert "Rosaceae" in db_manager.cache_ids["family"]
        assert "Rosa" in db_manager.cache_ids["genus"]

    def test_reset_database(self, db_manager, test_engine):
        """Test that database reset works correctly."""
        # Import data first time
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            count1 = session.execute(select(Name)).scalars().all()
            assert len(count1) > 0

        # Import again (should reset and re-import)
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            count2 = session.execute(select(Name)).scalars().all()
            assert len(count2) == len(count1)

    def test_session_property(self, db_manager):
        """Test that session property returns a valid session."""
        session = db_manager.session
        assert session is not None
        session.close()

    def test_ipni_extraction(self, db_manager, test_engine):
        """Test that IPNI IDs are correctly extracted."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            rosa_canina = session.execute(
                select(Name).where(Name.name == "Rosa canina")
            ).scalar_one()

            # IPNI should be extracted from urn:lsid:ipni.org:names:720955-1
            assert rosa_canina.ipni == "720955-1"

    def test_parent_id_extraction(self, db_manager, test_engine):
        """Test that parent IDs are correctly extracted."""
        db_manager.import_data(force_download=False, delete_files=False)

        with db_manager.session as session:
            names = session.execute(select(Name)).scalars().all()

            # Check that parent_id is properly extracted (wfo- prefix removed)
            for name in names:
                if name.parent_id:
                    # parent_id should be numeric string without 'wfo-' prefix
                    assert name.parent_id.isdigit()
