import json
import logging
import os
from functools import partial
from pathlib import Path
from typing import Any, Dict, Optional, Type

from thoth.storages.ceph import CephStore
from thoth.storages.exceptions import NotFoundError

from srcopsmetrics import utils
from srcopsmetrics.enums import StoragePath
from srcopsmetrics.utils import check_directory

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

    def load_locally(file_path: Path) -> Optional[Dict[str, Any]]:
        """Load knowledge file from local storage."""
        _LOGGER.info("Loading knowledge locally")
        if not file_path.exists() or os.path.getsize(file_path) == 0:
            _LOGGER.debug("Knowledge %s not found locally" % file_path)
            return None
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def load_remotely(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load knowledge file from Ceph storage."""
        _LOGGER.info("Loading knowledge from Ceph")
        ceph_filename = os.path.relpath(file_path).replace("./", "")
        try:
            return self.get_ceph_store().retrieve_document(ceph_filename)
        except NotFoundError:
            _LOGGER.debug("Knowledge %s not found on Ceph" % file_path)
            return None
