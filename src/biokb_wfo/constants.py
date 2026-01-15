import os
from pathlib import Path

# standard for all biokb projects, but individual set
PROJECT_NAME = "wfo"
BASIC_NODE_LABEL = "DbWfo"
# standard for all biokb projects
ORGANIZATION = "biokb"
LIBRARY_NAME = f"{ORGANIZATION}_{PROJECT_NAME}"
HOME = str(Path.home())
BIOKB_FOLDER = os.path.join(HOME, f".{ORGANIZATION}")
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

BASE_URL_DOWNLOAD = (
    "https://zenodo.org/records/18007552/files/plant_list_2025-12.json.zip?download=1"
)

# files on ftp server in FTP_DIR
CHEMICAL_DATA_FILE = "chemical_data.tsv.gz"
COMMENT_FILE = "comments.tsv.gz"
COMPOUND_FILE = "compounds.tsv.gz"
DATABASE_ACCESSION_FILE = "database_accession.tsv.gz"
NAME_FILE = "names.tsv.gz"
REFERENCE_FILE = "reference.tsv.gz"
RELATION_FILE = "relation.tsv.gz"
STRUCTURE_FILE = "structures.tsv.gz"
STATUS_FILE = "status.tsv.gz"
SOURCE_FILE = "source.tsv.gz"
RELATION_TYPE_FILE = "relation_type.tsv.gz"
CHEBI_URI = "http://purl.obolibrary.org/obo/CHEBI_"
BIOKB_URI = "https://biokb.scai.fraunhofer.de"
BASE_URI = f"{BIOKB_URI}/chebi"
