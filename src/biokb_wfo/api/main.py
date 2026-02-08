import logging
import os
import re
import secrets
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from select import select
from typing import Annotated, AsyncGenerator, Generator

import jellyfish
import Levenshtein
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Engine, create_engine, or_
from sqlalchemy.orm import Session

from biokb_wfo.api import schemas
from biokb_wfo.api.query_tools import SASearchResults, build_dynamic_query
from biokb_wfo.api.tags import Tag
from biokb_wfo.constants import (
    DB_DEFAULT_CONNECTION_STR,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    ZIPPED_TTLS_PATH,
)
from biokb_wfo.db import manager, models

# from biokb_wfo.rdf.neo4j_importer import Neo4jImporter
# from biokb_wfo.rdf.turtle import TurtleCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)

USERNAME: str = os.environ.get("API_USERNAME", "admin")
PASSWORD: str = os.environ.get("API_PASSWORD", "admin")


def get_engine() -> Engine:
    conn_url = os.environ.get("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
    engine: Engine = create_engine(conn_url)
    return engine


def get_session() -> Generator[Session, None, None]:
    engine: Engine = get_engine()
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize app resources on startup and cleanup on shutdown."""
    engine = get_engine()
    manager.DbManager(engine)
    yield
    # Clean up resources if needed
    pass


description = (
    "A RESTful API for BioKB-WFO. This is not an official WFO API."
    " Please refer to [EBI for official WFO services](https://www.ebi.ac.uk/chebi/)"
)

app = FastAPI(
    title="RESTful API for BioKB-WFO.",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(
        app="biokb_wfo.api.main:app",
        host=host,
        port=port,
        log_level="warning",
    )


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
) -> None:
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# tag: Database Management
# ========================


@app.post(
    path="/import_data/",
    response_model=dict[str, int],
    tags=[Tag.DBMANAGE],
)
async def import_data(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_download: bool = Query(
        False,
        description=(
            "Whether to re-download data files even if they already exist,"
            " ensuring the newest version."
        ),
    ),
    delete_files: bool = Query(
        False,
        description=(
            "Whether to delete the downloaded files"
            " after importing them into the database."
        ),
    ),
) -> dict[str, int]:
    """Download data (if not exists) and load in database.

    Can take up to 15 minutes to complete.
    """
    try:
        dbm = manager.DbManager()
        result = dbm.import_data(
            force_download=force_download, delete_files=delete_files
        )
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data. {e}",
        ) from e
    return result


# @app.get("/export_ttls/", tags=[Tag.DBMANAGE])
# async def get_report(
#     credentials: HTTPBasicCredentials = Depends(verify_credentials),
#     force_create: bool = Query(
#         False,
#         description="Whether to re-generate the TTL files even if they already exist.",
#     ),
# ) -> FileResponse:

#     file_path = ZIPPED_TTLS_PATH
#     if not os.path.exists(file_path) or force_create:
#         try:
#             TurtleCreator().create_ttls()
#         except Exception as e:
#             logger.error(f"Error generating TTL files: {e}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Error generating TTL files. Data already imported?",
#             ) from e
#     return FileResponse(
#         path=file_path, filename="chebi_ttls.zip", media_type="application/zip"
#     )


# @app.get("/import_neo4j/", tags=[Tag.DBMANAGE])
# async def import_neo4j(
#     credentials: HTTPBasicCredentials = Depends(verify_credentials),
#     uri: str | None = Query(
#         NEO4J_URI,
#         description="The Neo4j URI. If not provided, "
#         "the default from environment variable is used.",
#     ),
#     user: str | None = Query(
#         NEO4J_USER,
#         description="The Neo4j user. If not provided,"
#         " the default from environment variable is used.",
#     ),
#     password: str | None = Query(
#         NEO4J_PASSWORD,
#         description="The Neo4j password. If not provided,"
#         " the default from environment variable is used.",
#     ),
# ) -> dict[str, str]:
#     """Import RDF turtle files in Neo4j."""
#     try:
#         if not os.path.exists(ZIPPED_TTLS_PATH):
#             raise HTTPException(
#                 status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
#                 detail=(
#                     "Zipped TTL files not found. Please "
#                     "generate them first using /export_ttls/ endpoint."
#                 ),
#             )
#         importer = Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password)
#         importer.import_ttls()
#     except Exception as e:
#         logger.error(f"Error importing data into Neo4j: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error importing data into Neo4j: {e}",
#         ) from e
#     return {"status": "Neo4j import completed successfully."}


# tag: Name
# ========================


@app.get("/names/", response_model=schemas.NameSearchResults, tags=[Tag.NAME])
async def search_names(
    search: schemas.NameSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search compounds.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Name,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get(
    "/names/find_similar",
    response_model=list[schemas.SimilarNameSearchResult],
    tags=[Tag.NAME],
)
async def names_find_similar(
    session: Session = Depends(get_session),
    search_for_name: str = Query(
        ..., description="Name to search for", example="acHila meliflium"
    ),
):
    """Fuzzy search for similar names using LEVENSHTEIN algorithm."""

    columns = (
        models.Plant.name,
        models.Plant.name_alpha,
        models.Plant.name_plain,
        models.Plant.genus,
        models.Plant.family,
        models.Plant.placed_in_genus,
        models.Plant.wfo_id,
    )

    search_for_name = re.sub(r"\s+", " ", search_for_name.strip())
    name_splitted = [x.strip() for x in search_for_name.split(" ")]

    stmt = session.query(*columns)

    # First, check for exact match
    # If an exact match is found, return it immediately.
    exact_results = session.execute(
        stmt.where(models.Plant.name_alpha.like(search_for_name))
    ).all()
    if exact_results:
        return_values = []
        for exact_result in exact_results:
            return_values.append(
                schemas.SimilarNameSearchResult(
                    calculate_with="exact",
                    name=exact_result.name,
                    name_alpha=exact_result.name_alpha,
                    name_plain=exact_result.name_plain,
                    genus=exact_result.genus,
                    family=exact_result.family,
                    placed_in_genus=exact_result.placed_in_genus,
                    wfo_id=exact_result.wfo_id,
                    similarity=1.0,
                )
            )
        return return_values

    # If no exact match, use phonetic similarity with Metaphone algorithm
    # Metaphone is better than soundex for non-English names including Latin scientific names
    # Also try Jaro-Winkler which works well for scientific names with shared prefixes
    name_metaphone = jellyfish.metaphone(search_for_name)
    first_letter = search_for_name[0].upper()

    # Get names that start with same letter to reduce the dataset for phonetic comparison
    candidate_stmt = session.query(*columns).where(
        models.Plant.name_alpha.like(f"{first_letter}%")
    )

    candidates = session.execute(candidate_stmt).all()

    # Filter candidates by Metaphone similarity and Jaro-Winkler
    phonetic_matches = []
    for candidate in candidates:
        candidate_metaphone = jellyfish.metaphone(candidate.name_alpha)

        # Check if metaphone codes match
        metaphone_match = name_metaphone == candidate_metaphone

        # Also check Jaro-Winkler similarity for scientific names (good for genus/species prefixes)
        jaro_similarity = jellyfish.jaro_winkler_similarity(
            search_for_name.lower(), candidate.name_alpha.lower()
        )

        if metaphone_match or jaro_similarity > 0.8:
            # Calculate combined similarity score
            sequence_ratio = SequenceMatcher(
                None, search_for_name.lower(), candidate.name_alpha.lower()
            ).ratio()
            final_similarity = max(jaro_similarity, sequence_ratio)

            if final_similarity > 0.5:
                phonetic_matches.append(
                    schemas.SimilarNameSearchResult(
                        calculate_with="metaphone_jaro",
                        name=candidate.name,
                        name_alpha=candidate.name_alpha,
                        name_plain=candidate.name_plain,
                        genus=candidate.genus,
                        family=candidate.family,
                        placed_in_genus=candidate.placed_in_genus,
                        wfo_id=candidate.wfo_id,
                        similarity=round(final_similarity, 2),
                    )
                )

    if phonetic_matches:
        return sorted(phonetic_matches, key=lambda x: x.similarity, reverse=True)[:30]

    results = []
    ratios = []
    # If no phonetic matches, fall back to pattern-based search with Levenshtein distance

    if len(name_splitted) < 2:
        search_str = f"{search_for_name}%"
    else:
        search_str = f"{name_splitted[0]}% {name_splitted[1]}%"
    stmt3 = session.query(*columns).where(models.Plant.name_alpha.like(search_str))
    results = session.execute(stmt3).all()

    # check for similarity

    for result in results:
        ratio = SequenceMatcher(None, search_for_name, result.name_alpha).ratio()
        if ratio > 0.3:  # Threshold for similarity
            ratios.append(
                schemas.SimilarNameSearchResult(
                    calculate_with="pattern_match",
                    name=result.name,
                    name_alpha=result.name_alpha,
                    name_plain=result.name_plain,
                    genus=result.genus,
                    family=result.family,
                    placed_in_genus=result.placed_in_genus,
                    wfo_id=result.wfo_id,
                    similarity=round(ratio, 2),
                )
            )
    if ratios:
        return sorted(ratios, key=lambda x: x.similarity, reverse=True)

    # if no results Levenshtein
    if not ratios:
        stmt4 = stmt.where(
            or_(
                models.Plant.name_alpha.like(f"{search_for_name[0]}%"),
                models.Plant.name_alpha.like(f"%{search_for_name[-4:]}"),
            )
        )
        results = session.execute(stmt4).all()

        for result in results:
            ratio = Levenshtein.ratio(search_for_name, result.name_alpha)
            if ratio > 0.3:
                ratios.append(
                    schemas.SimilarNameSearchResult(
                        calculate_with="levenshtein",
                        name=result.name,
                        name_alpha=result.name_alpha,
                        name_plain=result.name_plain,
                        genus=result.genus,
                        family=result.family,
                        placed_in_genus=result.placed_in_genus,
                        wfo_id=result.wfo_id,
                        similarity=round(ratio, 2),  # Convert to percentage
                    )
                )
        if ratios:
            return sorted(ratios, key=lambda x: x.similarity, reverse=True)[:3]

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Name '{search_for_name}' not found.",
        )
