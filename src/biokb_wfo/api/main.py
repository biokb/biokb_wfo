import logging
import os
import re
import secrets
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from typing import Annotated, AsyncGenerator, Generator, List

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
from biokb_wfo.rdf.neo4j_importer import Neo4jImporter
from biokb_wfo.rdf.turtle import TurtleCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)

USERNAME: str = os.environ.get("WFO_API_USERNAME", "admin")
PASSWORD: str = os.environ.get("WFO_API_PASSWORD", "admin")


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
    " Please refer to [World Flora Online website](https://www.worldfloraonline.org)"
)

app = FastAPI(
    title="RESTful API for BioKB-WFO.",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
    root_path=os.environ.get("API_WFO_ROOT_PATH", ""),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def run_api(host: str = "0.0.0.0", port: int = 8000) -> None:
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


@app.get("/export_ttls/", tags=[Tag.DBMANAGE])
async def get_report(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_create: bool = Query(
        False,
        description="Whether to re-generate the TTL files even if they already exist.",
    ),
) -> FileResponse:

    file_path = ZIPPED_TTLS_PATH
    if not os.path.exists(file_path) or force_create:
        try:
            TurtleCreator().create_ttls()
        except Exception as e:
            logger.error(f"Error generating TTL files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating TTL files. Data already imported?",
            ) from e
    return FileResponse(
        path=file_path, filename="wfo_ttls.zip", media_type="application/zip"
    )


@app.get("/import_neo4j/", tags=[Tag.DBMANAGE])
async def import_neo4j(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    uri: str | None = Query(
        NEO4J_URI,
        description="The Neo4j URI. If not provided, "
        "the default from environment variable is used.",
    ),
    user: str | None = Query(
        NEO4J_USER,
        description="The Neo4j user. If not provided,"
        " the default from environment variable is used.",
    ),
    password: str | None = Query(
        NEO4J_PASSWORD,
        description="The Neo4j password. If not provided,"
        " the default from environment variable is used.",
    ),
) -> dict[str, str]:
    """Import RDF turtle files in Neo4j."""
    try:
        if not os.path.exists(ZIPPED_TTLS_PATH):
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=(
                    "Zipped TTL files not found. Please "
                    "generate them first using /export_ttls/ endpoint."
                ),
            )
        importer = Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password)
        importer.import_ttls()
    except Exception as e:
        logger.error(f"Error importing data into Neo4j: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data into Neo4j: {e}",
        ) from e
    return {"status": "Neo4j import completed successfully."}


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
    Search names.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Name,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/name/first_hit/", response_model=schemas.NameFoundResult, tags=[Tag.NAME])
async def search_name_first_hit(
    names: list[str] = Query(
        ...,
        description="List of names to search for correct names",
        openapi_examples={
            "example 1": {"value": ["Achila meliflium", "Almue Fera"]},
            "example 2": {"value": ["Achillea millefolium", "Acer rubrum"]},
        },
    ),
    session: Session = Depends(get_session),
) -> schemas.NameFoundResult | None:
    """"""
    url_template = "https://www.worldfloraonline.org/taxon/wfo-"
    names = [re.sub(r"\s+", " ", name.strip()) for name in names]
    result: models.Name | None = None
    found_in: str = "Not defined"
    found_name: schemas.NameFoundResult | None = None

    # first try to get valid names
    for name in names:
        for column in [
            models.Name.full_name_plain,
            models.Name.full_name_no_authors,
            models.Name.full_name,
        ]:
            result = (
                session.query(models.Name)
                .filter(
                    column == name,
                    models.Name.status == models.StatusEnums.VALID.value,
                )
                .first()
            )
            if result:
                found_in = column.name
                break

        if not result:
            # if no valid name found, try to get synonyms
            for column in [
                models.Name.full_name_plain,
                models.Name.full_name_no_authors,
                models.Name.full_name,
            ]:
                result = (
                    session.query(models.Name)
                    .filter(
                        column == name,
                        models.Name.status != models.StatusEnums.VALID.value,
                    )
                    .first()
                )
                if result:
                    found_in = column.name
                    break
    if isinstance(result, models.Name):
        # if a valid name is found, return it as Name
        url = f"{url_template}{result.id:010}"
        found_name = schemas.NameFoundResult(
            wfo_id=result.id,
            found_in=found_in,
            full_name=result.full_name,
            full_name_no_authors=result.full_name_no_authors,
            full_name_plain=result.full_name_plain,
            genus=result.genus.name if result.genus else None,
            family=result.family.name if result.family else None,
            status=result.status,
            rank=result.rank,
            role=result.role,
            url=url,
        )
    return found_name


@app.get(
    "/names/find_similar",
    response_model=list[schemas.SimilarNameSearchResult],
    tags=[Tag.NAME],
)
async def names_find_similar(
    session: Session = Depends(get_session),
    search_for_name: str = Query(
        ...,
        description="Name to search for",
        openapi_examples={
            "example 1": {"value": "acHila meliflium"},
            "example 2": {"value": "Almue Fera"},
        },
    ),
    status_: models.StatusEnums | None = Query(
        None,
        description="status",
    ),
    rank: models.RankEnums | None = Query(
        None,
        description="rank",
    ),
    role: models.RoleEnums | None = Query(
        None,
        description="role",
    ),
) -> list[schemas.SimilarNameSearchResult] | None:

    search_for_name = re.sub(r"\s+", " ", search_for_name.strip())
    name_splitted: List[str] = [x.strip() for x in search_for_name.split(" ")]

    filters = []
    filters += [models.Name.status == status_.value] if status_ else []
    filters += [models.Name.rank == rank.value] if rank else []
    filters += [models.Name.role == role.value] if role else []

    exact_results = (
        session.query(models.Name)
        .where(models.Name.full_name_plain.like(search_for_name), *filters)
        .all()
    )

    # First, check for exact match
    # If an exact match is found, return it immediately.

    if exact_results:
        return_values: list[schemas.SimilarNameSearchResult] = []
        for exact_result in exact_results:
            return_values.append(
                schemas.SimilarNameSearchResult(
                    id=exact_result.id,
                    full_name=exact_result.full_name,
                    status=exact_result.status,
                    role=exact_result.role,
                    rank=exact_result.rank,
                    year=exact_result.year,
                    ipni=exact_result.ipni,
                    calculate_with="exact",
                    similarity=1.0,
                )
            )
        return return_values

    # If no exact match, use phonetic similarity with Metaphone algorithm
    # Metaphone is better than soundex for non-English names including
    # Latin scientific names
    # Also try Jaro-Winkler which works well for scientific names with shared prefixes
    name_metaphone = jellyfish.metaphone(search_for_name)
    first_letter = search_for_name[0].upper()

    # Get names that start with same letter to reduce the dataset for
    # phonetic comparison
    candidates: List[models.Name] = (
        session.query(models.Name)
        .where(models.Name.full_name_plain.like(f"{first_letter}%"), *filters)
        .all()
    )

    # Filter candidates by Metaphone similarity and Jaro-Winkler
    phonetic_matches: list[schemas.SimilarNameSearchResult] = []
    for candidate in candidates:
        candidate_metaphone = jellyfish.metaphone(candidate.full_name)

        # Check if metaphone codes match
        metaphone_match = name_metaphone == candidate_metaphone

        # Also check Jaro-Winkler similarity for scientific names
        # (good for genus/species prefixes)
        jaro_similarity = jellyfish.jaro_winkler_similarity(
            search_for_name.lower(), candidate.full_name.lower()
        )

        if metaphone_match or jaro_similarity > 0.8:
            # Calculate combined similarity score
            sequence_ratio = SequenceMatcher(
                None, search_for_name.lower(), candidate.full_name.lower()
            ).ratio()
            final_similarity = max(jaro_similarity, sequence_ratio)

            if final_similarity > 0.5:
                phonetic_match = schemas.SimilarNameSearchResult(
                    id=candidate.id,
                    full_name=candidate.full_name,
                    status=candidate.status,
                    role=candidate.role,
                    rank=candidate.rank,
                    year=candidate.year,
                    ipni=candidate.ipni,
                    calculate_with="metaphone_jaro",
                    similarity=round(final_similarity, 2),
                )
                phonetic_matches.append(phonetic_match)

    if phonetic_matches:
        return sorted(phonetic_matches, key=lambda x: x.similarity, reverse=True)[:30]

    sequence_matches: list[schemas.SimilarNameSearchResult] = []
    # If no phonetic matches, fall back to pattern-based search with
    # Levenshtein distance

    if len(name_splitted) < 2:
        search_str = f"{search_for_name}%"
    else:
        search_str = f"{name_splitted[0]}% {name_splitted[1]}%"

    results: List[models.Name] = (
        session.query(models.Name)
        .where(models.Name.full_name.like(search_str), *filters)
        .all()
    )

    # check for similarity

    for result in results:
        ratio = SequenceMatcher(None, search_for_name, result.full_name).ratio()
        if ratio > 0.3:  # Threshold for similarity
            sequence_matches.append(
                schemas.SimilarNameSearchResult(
                    id=result.id,
                    full_name=result.full_name,
                    status=result.status,
                    rank=result.rank,
                    year=result.year,
                    ipni=result.ipni,
                    role=result.role,
                    calculate_with="sequence_matcher",
                    similarity=round(ratio, 2),
                )
            )
    if sequence_matches:
        return sorted(sequence_matches, key=lambda x: x.similarity, reverse=True)

    # if no results sequence_matcher
    lstein_matches: list[schemas.SimilarNameSearchResult] = []
    results = (
        session.query(models.Name)
        .where(
            or_(
                models.Name.full_name.like(f"{search_for_name[0]}%"),
                models.Name.full_name.like(f"%{search_for_name[-4:]}"),
            ),
            *filters,
        )
        .all()
    )

    for result in results:
        ratio = Levenshtein.ratio(search_for_name, result.full_name)
        if ratio > 0.3:
            lstein_matches.append(
                schemas.SimilarNameSearchResult(
                    id=result.id,
                    full_name=result.full_name,
                    status=result.status,
                    role=result.role,
                    rank=result.rank,
                    year=result.year,
                    ipni=result.ipni,
                    calculate_with="levenshtein",
                    similarity=round(ratio, 2),
                )
            )
    if lstein_matches:
        return sorted(lstein_matches, key=lambda x: x.similarity, reverse=True)[:3]

    # No matches found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Name '{search_for_name}' not found.",
    )


@app.get("/species/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_species(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search species.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Species,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/genus/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_genus(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search genus.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Genus,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/tribe/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_tribe(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search tribe.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Tribe,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/family/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_family(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search family.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Family,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/order/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_order(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search order.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Order,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/phylum/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_phylum(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search phylum.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Phylum,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subkingdom/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subkingdom(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subkingdom.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subkingdom,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/kingdom/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_kingdom(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search kingdom.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Kingdom,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/section/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_section(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search section.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Section,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subgenus/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subgenus(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subgenus.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subgenus,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subspecies/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subspecies(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subspecies.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subspecies,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/variety/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_variety(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search variety.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Variety,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subtribe/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subtribe(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subtribe.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subtribe,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subclass/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subclass(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subclass.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subclass,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/classification/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_classification(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search classification.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Classification,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subfamily/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subfamily(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subfamily.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subfamily,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/superorder/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_superorder(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search superorder.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Superorder,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/series/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_series(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search series.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Series,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subsection/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subsection(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subsection.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subsection,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/supertribe/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_supertribe(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search supertribe.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Supertribe,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subvariety/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subvariety(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subvariety.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subvariety,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subseries/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subseries(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subseries.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subseries,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/subform/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_subform(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search subform.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Subform,
        session=session,
        limit=limit,
        offset=offset,
    )


@app.get("/prole/", response_model=schemas.TaxonSearchResults, tags=[Tag.NAME])
async def search_prole(
    search: schemas.TaxonSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search prole.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Prole,
        session=session,
        limit=limit,
        offset=offset,
    )
