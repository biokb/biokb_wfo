"""MySQL database importer module."""

import logging
import os
import re
import urllib
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional

import ijson
import pandas as pd
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from biokb_wfo.constants import (
    BASE_URL_DOWNLOAD,
    COLUMN_MAPPINGS,
    DATA_FOLDER,
    DB_DEFAULT_CONNECTION_STR,
    PLACE_IN_FIELDS,
)
from biokb_wfo.db import models

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger: logging.Logger = logging.getLogger(__name__)


class DbManager:
    """Database import for WFO data."""

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        """Init DatabaseImporter

        Args:
            data_folder_path (Optional[str]): Folder downloadfiles. Defaults to None.
            engine (Optional[Engine]): SQLAlchemy engine. Defaults to None.
            redownload (bool): True if the data should be downloaded
                               even if they already exists. Default False.
        """
        self.__data_folder: str = DATA_FOLDER
        connection_str: str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine: Engine = engine if engine else create_engine(str(connection_str))
        if self.__engine.dialect.name == "sqlite":
            with self.__engine.connect() as connection:
                connection.execute(text("pragma foreign_keys=ON"))
        logger.info("Engine: %s", self.__engine)
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.__engine)
        self.cache_ids: Dict[str, Dict[str, int]] = {}
        self.mapper = PLACE_IN_FIELDS | COLUMN_MAPPINGS

    @property
    def session(self) -> Session:
        """Get a new SQLAlchemy session.

        Returns:
            Session: SQLAlchemy session
        """
        return self.Session()

    def _set_data_folder(self, data_folder: str) -> None:
        """Sets the data folder path.

        This is mainly for testing purposes.
        """
        self.__data_folder = data_folder

    def __reset_database(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        models.Base.metadata.drop_all(self.__engine)
        models.Base.metadata.create_all(self.__engine)

    def import_data(
        self, force_download: bool = False, delete_files: bool = True
    ) -> Dict[str, int]:
        path = self.__download_data(force_download=force_download)
        self.__reset_database()
        inserted = self.__insert_data(path)
        if delete_files:
            os.remove(path)
        return inserted

    def __download_data(self, force_download: bool = False) -> str:
        """Downloads wfo data.

        Args:
            redownload (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files
            already exist locally. Defaults to False.
        """
        if not os.path.exists(self.__data_folder):
            os.makedirs(self.__data_folder, exist_ok=True)
        found_file_name = re.search(
            r"(plant_list_\d{4}-\d{1,2}.json).zip", BASE_URL_DOWNLOAD
        )
        if found_file_name:
            file_name = found_file_name.group(0)
            zipped_file_path = os.path.join(self.__data_folder, file_name)

            if not os.path.exists(zipped_file_path) or force_download:
                logger.info(f"Downloading WFO data from {BASE_URL_DOWNLOAD}...")
                urllib.request.urlretrieve(
                    BASE_URL_DOWNLOAD,
                    zipped_file_path,
                )
            return zipped_file_path
        else:
            raise ValueError("Could not find file name in download URL.")

    def __insert_data(self, path: str, delete_files: bool = False) -> Dict[str, int]:
        inserted_in_place_tables = self.__inserted_place_in_data(path)
        inserted_names = self.__insert_names(path)
        return inserted_in_place_tables | inserted_names

    def __inserted_place_in_data(self, zip_path: str) -> Dict[str, int]:
        data: defaultdict[str, set] = defaultdict(set)
        file_name = Path(zip_path).name.split(".zip")[0]

        logger.info("Inserting PLACE_IN_FIELDS data into database...")
        with zipfile.ZipFile(zip_path, "r") as z:
            with z.open(file_name) as f:
                for item in ijson.items(f, "item"):
                    for key in [x for x in item.keys() if x in PLACE_IN_FIELDS]:
                        data[PLACE_IN_FIELDS[key]].add(item[key])

        inserted_counts: dict[str, int] = {}
        for k in data:
            enum_data = enumerate(sorted(data[k]), start=1)
            self.cache_ids[k] = {x[1]: x[0] for x in list(enum_data)}
            df = pd.DataFrame(
                {
                    "id": list(self.cache_ids[k].values()),
                    "name": list(self.cache_ids[k].keys()),
                }
            )
            inserts: int | None = df.to_sql(
                name=f"wfo_{k}",
                con=self.__engine,
                if_exists="append",
                index=False,
            )
            inserted_counts[k] = inserts if inserts is not None else 0
        return inserted_counts

    def __insert_names(self, zip_path: str) -> Dict[str, int]:
        file_name = Path(zip_path).name.split(".zip")[0]
        rows = []  # type: ignore

        counter = 0
        logger.info("Inserting names data into database...")
        with zipfile.ZipFile(zip_path, "r") as z:
            with z.open(file_name) as f:

                for item in ijson.items(f, "item"):
                    counter += 1
                    if counter % 100000 == 0:
                        self.__insert_names_from_rows(rows)
                        rows = []
                    row = {k: v for k, v in item.items() if k in self.mapper}  # type: ignore
                    rows.append(row)
                if rows:
                    self.__insert_names_from_rows(rows)
        return {"name": counter}

    def __insert_names_from_rows(self, rows: list[Dict[str, Any]]) -> int:
        """Insert names data into database."""

        df = pd.DataFrame(rows)
        df = df.rename(columns=self.mapper)
        df["id"] = df["id"].str.replace("wfo-", "").astype(int)
        df["parent_id"] = (
            df["parent_id_temp"].str.extract(r"wfo-(\d+)-").astype("Int64")
        )
        df.drop(columns=["parent_id_temp"], inplace=True)
        df["ipni"] = df["ipni"].str.extract(r"urn:lsid:ipni.org:names:(\d+-\d+)")

        for column in PLACE_IN_FIELDS.values():
            if column not in df.columns:
                continue
            df[f"{column}_id"] = df[column].map(self.cache_ids[column]).astype("Int64")
            df.drop(columns=[column], inplace=True)

        return (
            df.to_sql(
                name="wfo_name",
                con=self.__engine,
                if_exists="append",
                index=False,
            )
            or 0
        )


def import_data(
    engine: Optional[Engine] = None,
    force_download: bool = False,
    delete_files: bool = False,
) -> Dict[str, int]:
    """Import all data in database.

    Args:
        engine (Optional[Engine]): SQLAlchemy engine. Defaults to None.
        force_download (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files
            already exist locally. Defaults to False.
        delete_files (bool, optional): If True, downloaded files are
                                       deleted after import.
            Defaults to False.

    Returns:
        Dict[str, int]: table=key and number of inserted=value
    """
    db_manager = DbManager(engine)
    return db_manager.import_data(
        force_download=force_download, delete_files=delete_files
    )


def get_session(engine: Optional[Engine] = None) -> Session:
    """Get a new SQLAlchemy session.

    Returns:
        Session: SQLAlchemy session
    """
    db_manager = DbManager(engine)
    return db_manager.session
