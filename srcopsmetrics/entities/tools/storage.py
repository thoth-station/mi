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
from typing import Optional

from thoth.storages.ceph import CephStore
from thoth.storages.exceptions import NotFoundError

from srcopsmetrics.enums import StoragePath

import pandas as pd

_LOGGER = logging.getLogger(__name__)


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

    @staticmethod
    def load_locally(file_path: Path, as_csv: bool = True) -> pd.DataFrame:
        """Load knowledge file from local storage."""
        _LOGGER.info("Loading knowledge locally")
        try:
            return pd.read_csv(file_path, index_col=0)

        except FileNotFoundError:
            _LOGGER.debug("Knowledge %s not found locally" % file_path)
            return pd.DataFrame()

    def load_remotely(self, file_path: Path, as_csv: bool = True) -> pd.DataFrame:
        """Load knowledge file from Ceph storage."""
        _LOGGER.info("Loading knowledge from Ceph")

        ceph_filename = os.path.relpath(file_path).replace("./", "")
        try:
            data = self.get_ceph_store().retrieve_document(ceph_filename)
            return pd.DataFrame(data)

        except NotFoundError:
            _LOGGER.debug("Knowledge %s not found on Ceph" % ceph_filename)
            return pd.DataFrame()
