#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2020 Francesco Murdaca, Dominik Tuchyna
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

"""Used to iterate through all entities from repository."""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from github import Github
from github.GithubException import GithubException
from thoth.storages.ceph import CephStore
from thoth.storages.exceptions import NotFoundError
from voluptuous.error import MultipleInvalid
from voluptuous.schema_builder import Schema

from srcopsmetrics.entity_schema import Schemas

_LOGGER = logging.getLogger(__name__)

API_RATE_MINIMAL_REMAINING = 20


class KnowledgeAnalysis:
    """Context manager that iterates through all entities in repository and collects them."""

    _ENTITY_SCHEMA = {
        "Issue": Schemas.Issues,
        "PullRequest": Schemas.PullRequests,
        "ContentFiles": Schemas.ContentFiles,
    }

    _GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    _KEY_ID = os.getenv("CEPH_KEY_ID")
    _SECRET_KEY = os.getenv("CEPH_SECRET_KEY")
    _PREFIX = os.getenv("CEPH_BUCKET_PREFIX")
    _HOST = os.getenv("S3_ENDPOINT_URL")
    _BUCKET = os.getenv("CEPH_BUCKET")

    def __init__(
        self,
        *,
        entity_type: Optional[str] = None,
        new_entities: Optional[str] = None,
        accumulator: Optional[str] = None,
        store_method: Optional[str] = None,
    ):
        """Initialize with previous and new knowledge of an entity."""
        self.entity_type = entity_type
        self.new_entities = new_entities
        self.accumulator = accumulator
        self.accumulator_backup = accumulator
        self.store_method = store_method

    def __enter__(self):
        """Context manager enter method."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit method."""
        if exc_type is not None:
            _LOGGER.info("Cached knowledge could not be saved")

    def store(self):
        """Iterate through entities of given repository and accumulate them."""
        github = Github(self._GITHUB_ACCESS_TOKEN)

        try:
            for idx, entity in enumerate(self.new_entities, 1):

                remaining = github.rate_limiting[0]

                if remaining <= API_RATE_MINIMAL_REMAINING:
                    wait_time = github.rate_limiting_resettime - int(datetime.now().timestamp())
                    _LOGGER.info("API rate limit REACHED, will now wait for %d minutes" % (wait_time // 60))
                    time.sleep(wait_time)

                if idx % 10 == 0:
                    _LOGGER.info("[ API requests remaining: %d ]" % remaining)

                _LOGGER.info("Analysing %s no. %d/%d" % (self.entity_type, idx, len(self.new_entities)))

                self.accumulator_backup = self.accumulator
                self.store_method(entity, self.accumulator)

        except (GithubException, KeyboardInterrupt):
            _LOGGER.info("Problem occured, saving cached knowledge")
            try:
                self._ENTITY_SCHEMA[self.entity_type](self.accumulator)
                return self.accumulator
            except MultipleInvalid:
                self._ENTITY_SCHEMA[self.entity_type](self.accumulator_backup)
                return self.accumulator_backup

        return self.accumulator
