import logging
from importlib.metadata import PackageNotFoundError, version

from biokb_wfo.db.manager import DbManager, get_session, import_data

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from biokb_wfo.rdf.neo4j_importer import Neo4jImporter, import_ttls
from biokb_wfo.rdf.turtle import TurtleCreator, create_ttls

try:
    __version__ = version("biokb_wfo")
except PackageNotFoundError:
    # Package is not installed (e.g., during local development)
    __version__ = "unknown"

__all__ = [
    "DbManager",
    "import_data",
    "get_session",
    "Neo4jImporter",
    "import_ttls",
    "TurtleCreator",
    "create_ttls",
]
