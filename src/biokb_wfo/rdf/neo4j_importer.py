import logging
import os
import zipfile
from typing import LiteralString, cast

from neo4j import Driver, GraphDatabase
from rdflib import Graph
from rdflib_neo4j import (  # type: ignore
    HANDLE_VOCAB_URI_STRATEGY,
    Neo4jStore,
    Neo4jStoreConfig,
)
from tqdm import tqdm

from biokb_wfo.constants import (
    BASIC_NODE_LABEL,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    ZIPPED_TTLS_PATH,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger(name=__name__)


class Neo4jImporter:

    def __init__(
        self,
        neo4j_uri: str | None = None,
        neo4j_user: str | None = None,
        neo4j_pwd: str | None = None,
    ) -> None:
        """Initialize Neo4jImporter with connection to Neo4j.
        Args:
            neo4j_uri (str | None): URI of the Neo4j database.
            neo4j_user (str | None): Username for Neo4j.
            neo4j_pwd (str | None): Password for Neo4j.
            driver (Driver | None): Neo4j Driver instance. If provided,
                                    it will be used instead of creating a new one.
        """
        self.neo4j_uri = neo4j_uri if neo4j_uri else os.getenv("NEO4J_URI", NEO4J_URI)
        self.neo4j_user = (
            neo4j_user if neo4j_user else os.getenv("NEO4J_USER", NEO4J_USER)
        )
        self.neo4j_pwd = (
            neo4j_pwd if neo4j_pwd else os.getenv("NEO4J_PASSWORD", NEO4J_PASSWORD)
        )
        self.driver: Driver = GraphDatabase.driver(
            self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_pwd)
        )
        self.__zipped_ttls_path = ZIPPED_TTLS_PATH
        self.driver.verify_connectivity()

    def _delete_nodes_with_label(self, node_label: str = BASIC_NODE_LABEL) -> None:
        """Delete an existing graph in Neo4J.

        Args:
            node_label (str): The label of the nodes to delete.
        """
        logger.info("Delete an existing graph in Neo4J with node label %s.", node_label)
        with self.driver.session() as session:
            cypher: str = f"""MATCH (n:{node_label})
                CALL (n) {{
                WITH n
                DETACH DELETE n
                }} IN TRANSACTIONS OF 1000 ROWS;"""
            cypher = cast(LiteralString, cypher)  # type: ignore
            session.run(cypher)

    def _set_test_driver(self, driver: Driver) -> None:
        """Overwrite the Neo4j driver. Mainly for testing purposes.

        Args:
            driver (Driver): The Neo4j Driver instance to set.
        """
        self.driver = driver

    def _set_test_zipped_ttls_path(self, path: str) -> None:
        """Overwrite the zipped ttls path. Mainly for testing purposes.

        Args:
            path (str): The path to the zipped turtle files.
        """
        self.__zipped_ttls_path = path

    def __import_turtle_files_from_zip(self) -> None:
        """Import turtle files from a zip file into Neo4J.
        Args:
            neo4j_db (Graph): The Neo4J Graph database connection.
        """
        if not self.__zipped_ttls_path.endswith(".zip"):
            raise ValueError("The provided file is not a zip file.")
        if not os.path.exists(self.__zipped_ttls_path):
            raise FileNotFoundError(
                f"The file {self.__zipped_ttls_path} does not exist."
            )

        neo4j_db = self.__get_neo4j_db()
        with zipfile.ZipFile(self.__zipped_ttls_path, "r") as z:
            turtle_file_names = [x for x in z.namelist() if x.endswith(".ttl")]
            with tqdm(turtle_file_names) as pbar:
                for turtle_file_name in pbar:
                    pbar.set_description(f"Processing {turtle_file_name}")
                    with z.open(turtle_file_name) as file_io:
                        neo4j_db.parse(file_io, format="ttl")
                        neo4j_db.commit()
        neo4j_db.close()

    def __get_neo4j_db(self) -> Graph:
        """Get the Neo4j Graph database connection."""
        with self.driver.session() as session:
            cypher = (
                "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS "
                "FOR (r:Resource) REQUIRE r.uri IS UNIQUE"
            )
            session.run(cypher)

        auth_data = {
            "uri": self.neo4j_uri,
            "database": "neo4j",
            "user": self.neo4j_user,
            "pwd": self.neo4j_pwd,
        }

        config = Neo4jStoreConfig(
            auth_data=auth_data,
            custom_prefixes={},
            handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
            batching=True,
        )

        neo4j_db = Graph(store=Neo4jStore(config=config))
        return neo4j_db

    def import_ttls(self, delete_existing_graph: bool = True) -> bool:
        """Import all turtle file in Neo4J from zipped turtle files.

        Args:
            delete_existing_graph (bool): delete existing graph before import.
        Returns:
            bool: True if import is successful."""
        logger.info("Start importing all turtle file in Neo4J.")

        if delete_existing_graph:
            self._delete_nodes_with_label()

        self.__import_turtle_files_from_zip()

        return True


def import_ttls(
    neo4j_uri: str | None = None,
    neo4j_user: str | None = None,
    neo4j_pwd: str | None = None,
    delete_existing_graph: bool = True,
) -> bool:
    """Import data into Neo4J from zipped turtle files.

    Args:
        neo4j_uri (str | None): URI of the Neo4j database.
        neo4j_user (str | None): Username for Neo4j.
        neo4j_pwd (str | None): Password for Neo4j.
        delete_existing_graph (bool): delete existing graph before import.
    Returns:
        bool: True if import is successful.
    """
    importer = Neo4jImporter(
        neo4j_uri=neo4j_uri, neo4j_user=neo4j_user, neo4j_pwd=neo4j_pwd
    )
    result: bool = importer.import_ttls(delete_existing_graph=delete_existing_graph)
    return result
