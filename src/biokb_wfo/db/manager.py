"""MySQL database importer module."""

import json
import logging
import os
import re
import urllib
import urllib.request
import zipfile
from typing import Dict, Optional

import pandas as pd
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from tqdm import tqdm

from biokb_wfo.constants import (
    BASE_URL_DOWNLOAD,
    DATA_FOLDER,
    DB_DEFAULT_CONNECTION_STR,
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
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.__engine)

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

    def __create_empty_db(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        models.Base.metadata.drop_all(self.__engine)
        models.Base.metadata.create_all(self.__engine)

    def import_data(
        self, force_download: bool = False, keep_files: bool = False
    ) -> Dict[str, int]:
        path = self.__download_data(force_download=force_download)
        self.__create_empty_db()
        return self.__insert_data(path)

    def __download_data(self, force_download: bool = False) -> str:
        """Downloads chebi data from it's ftp server.

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
            file_path = os.path.join(self.__data_folder, file_name)

            if not os.path.exists(file_path) or force_download:
                logger.info(f"Downloading WFO data from {BASE_URL_DOWNLOAD}...")
                urllib.request.urlretrieve(
                    BASE_URL_DOWNLOAD,
                    file_path,
                )
                # extract plant_list_2025-12.json from teh zip file
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(self.__data_folder)

                logger.info(f"Downloaded WFO data to {file_path}.")
            extracted_file = found_file_name.group(1)
            path_to_extracted_file = os.path.join(
                self.__data_folder, extracted_file, extracted_file
            )
            return path_to_extracted_file
        else:
            raise ValueError("Could not find file name in download URL.")

    def __insert_data(self, path: str) -> Dict[str, int]:
        cols = {
            "accepted_full_name_string_plain_s": "name",
            "full_name_string_alpha_s": "name_alpha",
            "full_name_string_plain_s": "name_plain",
            "genus_string_s": "genus",
            "placed_in_family_s": "family",
            "placed_in_genus_s": "placed_in_genus",
            "wfo_id_s": "wfo_id",
        }
        new_rows = []
        for line in tqdm(open(path, "r")):
            line = line.strip().strip(",")
            if line in ["[", "]"]:
                continue
            row = json.loads(line)
            nomenclatural_status_s = row.get("nomenclatural_status_s", "")
            if nomenclatural_status_s != "valid":
                continue
            filtered_row = {col: row.get(col) for col in cols.keys()}
            new_rows.append(filtered_row)
        df = pd.DataFrame(new_rows)
        df.rename(columns=cols, inplace=True)
        df.to_sql(
            models.Name.__tablename__,
            con=self.__engine,
            if_exists="append",
            index=False,
            chunksize=5000,
        )
        return {models.Name.__tablename__: df.shape[0]}


def import_data(
    engine: Optional[Engine] = None,
    force_download: bool = False,
    keep_files: bool = False,
) -> Dict[str, int]:
    """Import all data in database.

    Args:
        engine (Optional[Engine]): SQLAlchemy engine. Defaults to None.
        force_download (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files
            already exist locally. Defaults to False.
        keep_files (bool, optional): If True, downloaded files are kept after import.
            Defaults to False.

    Returns:
        Dict[str, int]: table=key and number of inserted=value
    """
    db_manager = DbManager(engine)
    return db_manager.import_data(force_download=force_download, keep_files=keep_files)


def get_session(engine: Optional[Engine] = None) -> Session:
    """Get a new SQLAlchemy session.

    Returns:
        Session: SQLAlchemy session
    """
    db_manager = DbManager(engine)
    return db_manager.session
