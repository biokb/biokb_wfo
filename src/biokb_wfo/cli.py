import logging
import os
from typing import Optional

import click
from sqlalchemy import create_engine

from biokb_wfo import __version__
from biokb_wfo.constants import DB_DEFAULT_CONNECTION_STR, NEO4J_URI, NEO4J_USER
from biokb_wfo.db.manager import DbManager
from biokb_wfo.rdf.neo4j_importer import Neo4jImporter
from biokb_wfo.rdf.turtle import TurtleCreator


def setup_logging(ctx, param, value):
    # Only set up logging if the user actually asks for it
    if value == 1:
        logging.getLogger("biokb_ipni").setLevel(logging.INFO)
    elif value >= 2:
        logging.getLogger("biokb_ipni").setLevel(logging.DEBUG)

    # We must add a handler so the logs actually print to the screen
    if value > 0:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logging.getLogger("fetcher").addHandler(ch)

    return value


@click.group()
@click.version_option(__version__)
@click.option("-v", count=True, callback=setup_logging, expose_value=False)
def main():
    """Import in RDBMS, create turtle files and import into Neo4J.

    Please follow the steps:\n
    1. Import data using `import-data` command.\n
    2. Create TTL files using `create-ttls` command.\n
    3. Import TTL files into Neo4j using `import-neo4j` command.\n
    """
    pass


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
    default=DB_DEFAULT_CONNECTION_STR,
    help=f"SQLAlchemy engine URL [default: {DB_DEFAULT_CONNECTION_STR}]",
)
def import_data(force_download: bool, delete_files: bool, connection_string: str):
    """Import data."""
    engine = create_engine(connection_string)
    DbManager(engine=engine).import_data(
        force_download=force_download, delete_files=delete_files
    )
    click.echo(f"Data imported successfully to {connection_string}")


@main.command("create-ttls")
@click.option(
    "-c",
    "--connection-string",
    type=str,
    default=DB_DEFAULT_CONNECTION_STR,
    help=f"SQLAlchemy engine URL [default: {DB_DEFAULT_CONNECTION_STR}]",
)
def create_ttls(connection_string: str):
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


if __name__ == "__main__":
    main()
