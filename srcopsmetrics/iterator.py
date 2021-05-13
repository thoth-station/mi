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
from datetime import datetime, timezone

from github import Github
from github.GithubException import GithubException
from github.PaginatedList import PaginatedList
from tqdm import tqdm

from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)

API_RATE_MINIMAL_REMAINING = 80


class KnowledgeAnalysis:
    """Context manager that iterates through all entities in repository and collects them."""

    _GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    _KEY_ID = os.getenv("CEPH_KEY_ID")
    _SECRET_KEY = os.getenv("CEPH_SECRET_KEY")
    _PREFIX = os.getenv("CEPH_BUCKET_PREFIX")
    _HOST = os.getenv("S3_ENDPOINT_URL")
    _BUCKET = os.getenv("CEPH_BUCKET")

    def __init__(
        self, entity: Entity, is_local: bool = False,
    ):
        """Initialize with previous and new knowledge of an entity."""
        self.entity = entity
        self.knowledge_updated = False
        self.is_local = is_local
        self.github = Github(self._GITHUB_ACCESS_TOKEN)

    def __enter__(self):
        """Context manager enter method."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit method."""
        if exc_type is not None:
            _LOGGER.info("Cached knowledge could not be saved")

    def init_previous_knowledge(self, is_local: bool = False):
        """Every entity must have a previous knowledge initialization method."""
        self.entity.previous_knowledge = self.entity.load_previous_knowledge(is_local=self.is_local)

    def wait_until_api_reset(self):
        """Wait until the GitHub API rate limit is reset."""
        gh_time = self.github.get_rate_limit().core.reset
        local_time = datetime.now(tz=timezone.utc)

        wait_time = (gh_time - local_time.replace(tzinfo=None)).seconds
        wait_time += 60

        _LOGGER.info("API rate limit REACHED, will now wait for %d minutes" % (wait_time // 60))
        time.sleep(wait_time)

    def run(self):
        """Iterate through entities of given repository and accumulate them."""
        _LOGGER.info("-------------%s Analysis-------------" % self.entity.name())

        try:
            entities = self.entity.analyse()
            length = entities.totalCount if isinstance(entities, PaginatedList) else len(entities)
            for idx, entity in enumerate(tqdm(entities, total=length), 1):
                self.knowledge_updated = True

                remaining = self.github.get_rate_limit().core.remaining

                if remaining <= API_RATE_MINIMAL_REMAINING:
                    self.wait_until_api_reset()

                if idx % 5 == 0:
                    _LOGGER.info("[API requests remaining: %d]" % remaining)

                self.entity.store(entity)

        except (GithubException, KeyboardInterrupt) as e:
            _LOGGER.warning(str(e))
            _LOGGER.warning("Problem occured, cached data will be saved")

    def save_analysed_knowledge(self):
        """Save analysed knowledge if new information was extracted."""
        if self.knowledge_updated:
            self.entity.save_knowledge(is_local=self.is_local)
        else:
            _LOGGER.info("Nothing to store, no update operation needed")
