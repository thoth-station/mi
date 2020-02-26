#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright(C) 2020 Francesco Murdaca, Dominik Tuchyna
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A base class for collecting bot knowledge from GitHub."""

import os
import logging
import time
import json
from datetime import datetime

from typing import Any
from typing import Dict
from typing import Optional

from pathlib import Path

from github import Github

from thoth.storages.exceptions import NotFoundError
from thoth.storages.ceph import CephStore

_LOGGER = logging.getLogger(__name__)

API_RATE_MINIMAL_REMAINING = 20


class GitHubKnowledgeStore:
    """Context manager for entity storage process from GitHub."""

    _FILENAME_ENTITY = {"Issue": "issues", "PullRequest": "pull_requests"}

    _PREFIX = os.getenv("PREFIX")
    _HOST = os.getenv("HOST")
    _BUCKET = os.getenv("BUCKET")

    def __init__(
        self,
        *,
        is_local: Optional[bool] = False,
        entity_type: Optional[str] = None,
        new_entities: Optional[str] = None,
        accumulator: Optional[str] = None,
        store_method: Optional[str] = None,
    ):
        """Initialize with previous and new knowledge of an entity."""
        self.is_local = is_local
        if is_local:
            _LOGGER.info("Use local for knowledge loading and storing.")
        else:
            _LOGGER.info("Use Ceph for knowledge loading and storing.")

        self.entity_type = entity_type
        self.new_entities = new_entities
        self.accumulator = accumulator
        self.store_method = store_method

    def __enter__(self):
        """Context manager enter method."""
        return self

    def __exit__(self, type, value, traceback):
        """Context manager exit method."""
        if type is not None:
            _LOGGER.info("Problem occured, current state of the knowledge saved.")
        return self.accumulator

    def store(self):
        """Iterate through entities of given repository and accumulate them."""
        for idx, entity in enumerate(self.new_entities, 1):
            github = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
            remaining = github.rate_limiting[0]

            if remaining <= API_RATE_MINIMAL_REMAINING:
                wait_time = github.rate_limiting_resettime - int(datetime.now().timestamp())
                _LOGGER.info("API rate limit REACHED, will now wait for %d minutes" % (wait_time // 60))
                time.sleep(wait_time)

            if idx % 10 == 0:
                _LOGGER.info("[ API requests remaining: %d ]" % remaining)

            _LOGGER.info("Analysing %s no. %d/%d" % (self.entity_type, idx, len(self.new_entities)))

            self.store_method(entity, self.accumulator)
        return self.accumulator

    def save_knowledge(self, file_path: Path, data: Dict[str, Any]):
        """Save collected knowledge as json.

        The saved json contains one dictionary with single key 'results'
        under which the knowledge is stored.

        Arguments:
            file_path {Path} -- where the knowledge should be saved
            data {Dict[str, Any]} -- collected knowledge. Should be json compatible
        """
        results = {"results": data}

        _LOGGER.info("Saving knowledge file %s of size %d" % (os.path.basename(file_path), len(data)))

        if not self.is_local:
            ceph_filename = os.path.relpath(file_path).replace("./", "")
            s3 = self.get_ceph_store()
            s3.store_document(results, ceph_filename)
            _LOGGER.info("Saved on CEPH at %s%s%s" % (s3.bucket, s3.prefix, ceph_filename))
        else:
            with open(file_path, "w") as f:
                json.dump(results, f)
            _LOGGER.info("Saved locally at %s" % file_path)

    def get_ceph_store(self) -> CephStore:
        """Establish a connection to the CEPH."""
        s3 = CephStore(prefix=self._PREFIX, host=self._HOST, bucket=self._BUCKET)
        s3.connect()
        return s3

    def load_previous_knowledge(self, project_name: str, file_path: Path, knowledge_type: str) -> Dict[str, Any]:
        """Load previously collected repo knowledge. If a repo was not inspected before, create its directory.

        Arguments:
            repo_path {Path} -- path of the inspected github repository

        Returns:
            Dict[str, Any] -- previusly collected knowledge.
                            Empty dict if the knowledge does not exist.

        """
        filename = self._FILENAME_ENTITY[knowledge_type]

        if file_path is None:
            pwd = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
            project_path = pwd.joinpath("./" + project_name)
            file_path = project_path.joinpath("./" + filename + ".json")

        results = self.load_remotely(file_path) if not self.is_local else self.load_locally(file_path)

        if results is None:
            _LOGGER.info("No previous knowledge found for %s" % project_name)
            results = {}
            return results

        _LOGGER.info(
            "Found previous knowledge for %s with %d entities of type %s" % (project_name, len(results), knowledge_type)
        )

        return results

    @staticmethod
    def load_locally(file_path: Path) -> json:
        """Load knowledge file from local storage."""
        _LOGGER.info("Loading knowledge locally...")
        if not file_path.exists() or os.path.getsize(file_path) == 0:
            return None
        with open(file_path, "r") as f:
            data = json.load(f)
            results = data["results"]
        return results

    def load_remotely(self, file_path: Path) -> json:
        """Load knowledge file from Ceph storage."""
        _LOGGER.info("Loading knowledge from Ceph...")
        ceph_filename = os.path.relpath(file_path).replace("./", "")
        try:
            return self.get_ceph_store().retrieve_document(ceph_filename)["results"]
        except NotFoundError:
            _LOGGER.info("Knowledge %s not found on Ceph" % file_path)
