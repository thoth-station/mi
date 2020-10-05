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

import logging
import os
import time
import copy
from datetime import datetime

from github import Github
from github.GithubException import GithubException
from voluptuous.error import MultipleInvalid

from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)

API_RATE_MINIMAL_REMAINING = 20


class KnowledgeAnalysis:
    """Context manager that iterates through all entities in repository and collects them."""

    _GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    _KEY_ID = os.getenv("CEPH_KEY_ID")
    _SECRET_KEY = os.getenv("CEPH_SECRET_KEY")
    _PREFIX = os.getenv("CEPH_BUCKET_PREFIX")
    _HOST = os.getenv("S3_ENDPOINT_URL")
    _BUCKET = os.getenv("CEPH_BUCKET")

    def __init__(
        self, *, entity: Entity = None, is_local: bool = False,
    ):
        """Initialize with previous and new knowledge of an entity."""
        self.entity = entity
        self.backup = None
        self.knowledge_updated = False

    def __enter__(self):
        """Context manager enter method."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit method."""
        if exc_type is not None:
            _LOGGER.info("Cached knowledge could not be saved")

    def run(self):
        """Iterate through entities of given repository and accumulate them."""
        github = Github(self._GITHUB_ACCESS_TOKEN)
        _LOGGER.info("-------------%s Analysis-------------" % self.entity.name)

        try:
            for idx, entity in enumerate(self.entity.analyse(), 1):
                self.knowledge_updated = True

                remaining = github.rate_limiting[0]

                if remaining <= API_RATE_MINIMAL_REMAINING:
                    wait_time = github.rate_limiting_resettime - int(datetime.now().timestamp())
                    _LOGGER.info("API rate limit REACHED, will now wait for %d minutes" % (wait_time // 60))
                    time.sleep(wait_time)

                if idx % 10 == 0:
                    _LOGGER.info("[ API requests remaining: %d ]" % remaining)

                _LOGGER.info("Analysing %s no. %d/%d" % (self.entity.name, idx, len(self.entity.analyse())))

                self.backup = entity
                self.entity.store(entity)

        except (GithubException, KeyboardInterrupt):
            _LOGGER.info("Problem occured, saving cached knowledge")
            try:
                self.entity.entities_schema(self.accumulator)
                return self.entity.stored_entities()
            except MultipleInvalid:
                self.entity.entities_schema(self.accumulator_backup)
                return self.backup.stored_entities()

        # return self.entity.stored_entities()

    def save_analysed_knowledge(self):
        if self.knowledge_updated:
            self.entity.save_knowledge()
        else:
            _LOGGER.info("Nothing to store, no update operation needed")
