import os
from pathlib import Path

# standard for all biokb projects, but individual set
PROJECT_NAME = "wfo"
BASIC_NODE_LABEL = "DbWfo"
# standard for all biokb projects
ORGANIZATION = "biokb"
HOME = str(Path.home())
BIOKB_FOLDER = os.getenv("BIOKB_FOLDER", os.path.join(HOME, f".{ORGANIZATION}"))
PROJECT_FOLDER = os.path.join(BIOKB_FOLDER, PROJECT_NAME)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
EXPORT_FOLDER = os.path.join(DATA_FOLDER, "ttls")
ZIPPED_TTLS_PATH = os.path.join(DATA_FOLDER, "ttls.zip")
SQLITE_PATH = os.path.join(BIOKB_FOLDER, f"{ORGANIZATION}.db")
DB_DEFAULT_CONNECTION_STR = "sqlite:///" + SQLITE_PATH
NEO4J_PASSWORD = "neo4j_password"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")  # where to store log files
TABLE_PREFIX = f"{PROJECT_NAME}_"
os.makedirs(DATA_FOLDER, exist_ok=True)

# not standard for all biokb projects

BASE_URI = "https://biokb.scai.fraunhofer.de/wfo"

BASE_URL_DOWNLOAD = (
    "https://zenodo.org/records/18007552/files/plant_list_2025-12.json.zip?download=1"
)

BIOKB_URI = "https://biokb.scai.fraunhofer.de"

PLACE_IN_FIELDS: dict[str, str] = {
    "placed_in_class_s": "classification",
    "placed_in_code_s": "code",
    "placed_in_family_s": "family",
    "placed_in_form_s": "form",
    "placed_in_genus_s": "genus",
    "placed_in_kingdom_s": "kingdom",
    "placed_in_order_s": "order",
    "placed_in_phylum_s": "phylum",
    "placed_in_prole_s": "prole",
    "placed_in_section_s": "section",
    "placed_in_series_s": "series",
    "placed_in_species_s": "species",
    "placed_in_subclass_s": "subclass",
    "placed_in_subfamily_s": "subfamily",
    "placed_in_subform_s": "subform",
    "placed_in_subgenus_s": "subgenus",
    "placed_in_subkingdom_s": "subkingdom",
    "placed_in_suborder_s": "suborder",
    "placed_in_subsection_s": "subsection",
    "placed_in_subseries_s": "subseries",
    "placed_in_subspecies_s": "subspecies",
    "placed_in_subtribe_s": "subtribe",
    "placed_in_subvariety_s": "subvariety",
    "placed_in_superorder_s": "superorder",
    "placed_in_supertribe_s": "supertribe",
    "placed_in_tribe_s": "tribe",
    "placed_in_variety_s": "variety",
}

COLUMN_MAPPINGS = {
    "citation_micro_s": "citation",
    "full_name_string_alpha_s": "full_name",
    "full_name_string_no_authors_plain_s": "full_name_no_authors",
    "full_name_string_plain_s": "full_name_plain",
    "genus_string_s": "genus_string",
    "hybrid_taxon_b": "hybrid_taxon",
    "ipni_preferred_id_s": "ipni",
    "name_string_s": "name",
    "nomenclatural_status_s": "status",
    "parent_id_s": "parent_id_temp",
    "publication_year_i": "year",
    "rank_s": "rank",
    "role_s": "role",
    "species_string_s": "species_string",
    "wfo_id_s": "id",
}
