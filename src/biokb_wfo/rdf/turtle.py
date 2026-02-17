"""Module to create RDF turtle files from the imported data."""

import logging
import os.path
import shutil
from typing import Optional

from rdflib import RDF, XSD, Graph, Literal
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from biokb_wfo.constants import (
    BASIC_NODE_LABEL,
    DB_DEFAULT_CONNECTION_STR,
    EXPORT_FOLDER,
)
from biokb_wfo.db import models
from biokb_wfo.rdf import namespaces as ns

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)


def get_empty_graph() -> Graph:
    """Return an empty RDFlib.Graph with all needed namespaces"""
    graph = Graph()
    graph.bind("w", ns.WFO_NS)
    graph.bind("n", ns.NODE_NS)
    graph.bind("r", ns.REL_NS)
    graph.bind("xs", XSD)
    return graph


class TurtleCreator:
    """Turtle creator class."""

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        """Init TurtleCreator

        If engine=None tries to get the settings from config ini file

        If export_to_folder=None takes the default path.

        Args:
            engine (Engine | None, optional): SQLAlchemy class. Defaults to None.
            export_to_folder (str | None, optional): _description_. Defaults to None.
        """
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine = engine if engine else create_engine(str(connection_str))
        self.Session = sessionmaker(bind=self.__engine)
        self.__ttls_folder = EXPORT_FOLDER

    def _set_ttls_folder(self, export_to_folder: str) -> None:
        """Sets the export folder path.

        This is mainly for testing purposes.
        """
        self.__ttls_folder = export_to_folder

    def create_ttls(self) -> str:
        """Create all turtle files.

        Returns:
            str: path zipped file with ttls.
        """
        os.makedirs(self.__ttls_folder, exist_ok=True)
        self.create_nodes_ttl()
        return self.__create_zip_from_all_ttls()

    def __create_zip_from_all_ttls(self) -> str:
        """Create a zipped file from all turtle file and return the path.

        Returns:
            str: path to zipped file
        """
        path_to_zip_file = shutil.make_archive(
            base_name=self.__ttls_folder, format="zip", root_dir=self.__ttls_folder
        )
        logger.info(f"Zipped ttls create in {path_to_zip_file}")
        shutil.rmtree(self.__ttls_folder)
        return path_to_zip_file

    def create_nodes_ttl(self) -> str:
        """Create a turtle file with all nodes."""
        ttl_path = os.path.join(self.__ttls_folder, "nodes.ttl")
        logger.info("Create nodes ttl")
        graph = get_empty_graph()

        with self.Session() as session:
            taxa = (
                session.query(
                    models.Name.id,
                    models.Name.full_name,
                    models.Name.rank,
                    models.Name.parent_id,
                    models.Name.ipni,
                )
                .where(
                    models.Name.status == "valid",
                    models.Name.parent_id.isnot(None),
                    models.Name.rank.isnot(None),
                )
                .all()
            )
            for taxon in tqdm(taxa):
                taxon_uri = ns.WFO_NS[str(taxon.id).zfill(10)]
                graph.add((taxon_uri, RDF.type, ns.NODE_NS[taxon.rank.capitalize()]))
                graph.add((taxon_uri, RDF.type, ns.NODE_NS[BASIC_NODE_LABEL]))

                graph.add(
                    (
                        taxon_uri,
                        ns.REL_NS["name"],
                        Literal(taxon.full_name, datatype=XSD.string),
                    )
                )
                graph.add(
                    (
                        taxon_uri,
                        ns.REL_NS["rank"],
                        Literal(taxon.rank, datatype=XSD.string),
                    )
                )
                if taxon.parent_id:
                    parent_uri = ns.WFO_NS[str(taxon.parent_id).zfill(10)]
                    graph.add((taxon_uri, ns.REL_NS["HAS_PARENT"], parent_uri))
                if taxon.ipni:
                    ipni_uri = ns.IPNI_NS[str(taxon.ipni)]
                    graph.add(
                        (
                            taxon_uri,
                            ns.REL_NS["SAME_AS"],
                            ipni_uri,
                        )
                    )

        graph.serialize(ttl_path, format="turtle")
        return ttl_path


def create_ttls(
    engine: Optional[Engine] = None,
    export_to_folder: Optional[str] = None,
) -> str:
    """Create all turtle files.

    If engine=None tries to get the settings from config ini file

    If export_to_folder=None takes the default path.

    Args:
        engine (Engine | None, optional): SQLAlchemy class. Defaults to None.
        export_to_folder (str | None, optional): Folder to export ttl files.
            Defaults to None.

    Returns:
        str: path zipped file with ttls.
    """
    ttl_creator = TurtleCreator(engine=engine)
    if export_to_folder:
        ttl_creator._set_ttls_folder(export_to_folder)
    return ttl_creator.create_ttls()
