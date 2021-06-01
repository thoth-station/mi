# Copyright (C) 2020 Dominik Tuchyna
#
# This file is part of thoth-station/mi - Meta-information Indicators.
#
# thoth-station/mi - Meta-information Indicators is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thoth-station/mi - Meta-information Indicators is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with thoth-station/mi - Meta-information Indicators.  If not, see <http://www.gnu.org/licenses/>.

"""Knowledge storage tools and classes."""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union

import json

from thoth.storages.ceph import CephStore
from thoth.storages.exceptions import NotFoundError

from srcopsmetrics.enums import StoragePath

import pandas as pd

_LOGGER = logging.getLogger(__name__)


def load_data_frame(path_or_buf: Union[Path, Any]) -> pd.DataFrame:
    """Load DataFrame from either string data or path."""
    df = pd.read_json(path_or_buf, orient="records", lines=True)
    if not df.empty:
        df = df.set_index("id")
    return df


def load_json(path_or_buf: Union[Path, str]) -> Any:
    """Load json data from string or filepath."""
    if isinstance(path_or_buf, Path):
        with open(path_or_buf, "r") as f:
            return json.loads(f.read())

    return json.loads(path_or_buf)


class KnowledgeStorage:
    """Class for knowledge loading and saving."""

    _FILENAME_ENTITY = {
        "Issue": "issues",
        "PullRequest": "pull_requests",
        "ContentFile": "content_file",
    }

    _GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    _KEY_ID = os.getenv("CEPH_KEY_ID")
    _SECRET_KEY = os.getenv("CEPH_SECRET_KEY")
    _PREFIX = os.getenv("CEPH_BUCKET_PREFIX")
    _HOST = os.getenv("S3_ENDPOINT_URL")
    _BUCKET = os.getenv("CEPH_BUCKET")

    def __init__(self, is_local: Optional[bool] = False):
        """Initialize to behave as either local or remote storage."""
        self.is_local = is_local
        location = os.getenv(StoragePath.LOCATION_VAR.value, StoragePath.DEFAULT.value)
        self.main = Path(location)

        _LOGGER.debug("Use %s for knowledge loading and storing." % ("local" if is_local else "Ceph"))
        _LOGGER.debug("Use %s as a main path for storage.", self.main)

    def get_ceph_store(self) -> CephStore:
        """Establish a connection to the CEPH."""
        s3 = CephStore(
            key_id=self._KEY_ID, secret_key=self._SECRET_KEY, prefix=self._PREFIX, host=self._HOST, bucket=self._BUCKET
        )
        s3.connect()
        return s3

    def save_data(self, file_path: Path, data: Dict[str, Any]):
        """Save data as json.

        Arguments:
            file_path {Path} -- where the knowledge should be saved
            data {Dict[str, Any]} -- collected knowledge. Should be json compatible

        """
        _LOGGER.info("Saving knowledge file %s of size %d" % (os.path.basename(file_path), len(data)))

        if not self.is_local:
            ceph_filename = os.path.relpath(file_path).replace("./", "")
            s3 = self.get_ceph_store()
            s3.store_document(data, ceph_filename)
            _LOGGER.info("Saved on CEPH at %s/%s%s" % (s3.bucket, s3.prefix, ceph_filename))
        else:
            with open(file_path, "w") as f:
                json.dump(data, f)
            _LOGGER.info("Saved locally at %s" % file_path)

    def load_data(self, file_path: Optional[Path] = None, as_json: bool = False) -> Dict[str, Any]:
        """Load previously collected repo knowledge. If a repo was not inspected before, create its directory.

        Arguments:
            file_path {Optional[Path]} -- path to previously stored knowledge from
                               inspected github repository. If None is passed, the used path will
                               be :value:`~enums.StoragePath.DEFAULT`

            as_json {bool} -- load data as a plain json file

        Returns:
            Dict[str, Any] -- previusly collected knowledge.
                            Empty dict if the knowledge does not exist.

        """
        if file_path is None:
            raise ValueError("Filepath has to be specified.")

        results = (
            self.load_locally(file_path, as_json=as_json)
            if self.is_local
            else self.load_remotely(file_path, as_json=as_json)
        )

        if results is None:
            _LOGGER.info("File does not exist.")
            return {}

        _LOGGER.info("Data from file %s loaded")
        return results

    @staticmethod
    def load_locally(file_path: Path, as_json: bool = False) -> pd.DataFrame:
        """Load knowledge file from local storage."""
        _LOGGER.info("Loading knowledge locally")

        if not file_path.exists():
            _LOGGER.debug("Knowledge %s not found locally" % file_path)
            return pd.DataFrame()

        if as_json:
            return load_json(file_path)
        return load_data_frame(file_path)

    def load_remotely(self, file_path: Path, as_json: bool = False) -> pd.DataFrame:
        """Load knowledge file from Ceph storage."""
        _LOGGER.info("Loading knowledge from Ceph")

        ceph_filename = os.path.relpath(file_path).replace("./", "")
        try:
            data = self.get_ceph_store().retrieve_document(ceph_filename)
            if not as_json:
                data = load_data_frame(data)
            return data

        except NotFoundError:
            _LOGGER.debug("Knowledge %s not found on Ceph" % ceph_filename)
            return pd.DataFrame()
