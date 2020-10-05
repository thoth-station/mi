#!/usr/bin/env python3
# Copyright (C) 2020 Dominik Tuchyna
#
# This file is part of SrcOpsMetrics.
#
# SrcOpsMetrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SrcOpsMetrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SrcOpsMetrics.  If not, see <http://www.gnu.org/licenses/>.

"""Entity interface class."""

import os
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Collection, Dict
import logging

from github import Github
from github.Repository import Repository
from voluptuous.schema_builder import Schema

from srcopsmetrics.enums import StoragePath
from srcopsmetrics.storage import KnowledgeStorage
from srcopsmetrics import utils
from srcopsmetrics.entities.tools.storage import KnowledgeStorage

_LOGGER = logging.getLogger(__name__)


class Entity(metaclass=ABCMeta):
    """This class defines interface every entity class should implement."""

    # @abstractmethod
    def __init__(self, repository: Repository):
        """Initialize entity with github repository.

        Every entity should be initialized just with the repository name.
        """
        self.repository = repository

    # @property
    # @abstractmethod
    # def repository(self) -> Repository:
    #     """Repository object as defined in GitHub API documentation.

    #     Currently only PyGithub supported.
    #     """
    #     return self._repository

    # @repository.setter
    # @abstractmethod
    # def repository(self, repository):
    #     return self._repository

    # @property
    # @abstractmethod
    # def previous_knowledge(self) -> Collection:
    #     """Previous knowledge of given entity.

    #     Can be anything iterable.
    #     """

    @property
    # @abstractmethod
    # @classmethod
    def name(self) -> str:
        """Entity name as defined in GitHub API documentation.

        If this entity is not part of GitHub API, its name is up to contributor.
        """
        return type(self).__name__

    @property
    # @abstractmethod
    # @classmethod
    def filename(self) -> str:
        """File name of stored knowledge.

        If this entity is not part of GitHub API, its name is up to contributor.
        """
        return type(self).__name__

    @property
    @abstractmethod
    def entity_schema(self) -> Schema:
        """Return schema of a single entity that is analysed and stored.

        Entity is stored inside the entities_schema.
        """

    @property
    def entities_schema(self) -> Schema:
        """Return schema of how all of the entities of repo are stored."""
        return Schema({str: self.entity_schema})

    @abstractmethod
    def analyse(self) -> Collection:
        """Gather list of all entities that are later analysed using store method.

        :rtype: gathered list
        """

    @abstractmethod
    def store(self, single_entity):
        """Store passed entity.

        All the stored entities are then retrieved by stored_entities function.
        """

    @abstractmethod
    def stored_entities(self) -> Collection:
        """Return analysed entities."""

    def init_previous_knowledge(self, is_local: bool = False):
        """Every entity must have a previous knowledge initialization method."""

        self.previous_knowledge = self.load_previous_knowledge()

    @property
    def file_path(self) -> Path:
        """Get entity file path."""
        path = Path.cwd().joinpath(os.getenv(StoragePath.LOCATION_VAR.value, StoragePath.KNOWLEDGE_PATH.value))

        project_path = path.joinpath("./" + self.repository.full_name)
        utils.check_directory(project_path)

        return project_path.joinpath("./" + self.filename + ".json")

    def save_knowledge(self, file_path: Path = None, is_local: bool = False):
        """Save collected knowledge as json."""
        if self.stored_entities() is None or len(self.stored_entities()) == 0:
            _LOGGER.info("Nothing to store.")
            _LOGGER.info("\n")
            return

        if not file_path:
            file_path = self.file_path

        _LOGGER.info("Saving knowledge file %s of size %d" % (os.path.basename(file_path), len(self.stored_entities())))

        if not is_local:
            ceph_filename = os.path.relpath(file_path).replace("./", "")
            s3 = KnowledgeStorage().get_ceph_store()
            s3.store_document(self.stored_entities(), ceph_filename)
            _LOGGER.info("Saved on CEPH at %s/%s%s" % (s3.bucket, s3.prefix, ceph_filename))
        else:
            with open(file_path, "w") as f:
                json.dump(self.stored_entities(), f)
            _LOGGER.info("Saved locally at %s" % file_path)

    def load_previous_knowledge(self, is_local: bool = False) -> Dict[str, Any]:
        """Load previously collected repo knowledge. If a repo was not inspected before, create its directory."""
        if self.file_path is None and self.repository is None:
            raise ValueError("Either filepath or project name have to be specified.")

        data = (
            KnowledgeStorage().load_locally(self.file_path)
            if is_local
            else KnowledgeStorage().load_remotely(self.file_path)
        )

        if data is None:
            _LOGGER.info("No previous knowledge of type %s found" % self.name)
            return {}

        _LOGGER.info(
            "Found previous %s knowledge for %s with %d records" % (self.name, self.repository.full_name, len(data))
        )
        return data

    @abstractmethod
    def get_raw_github_data() -> Collection:
        """Get all entities method from github using PyGithub."""
        pass

    def get_only_new_entities(self) -> Collection:
        """Get new entities (whether PRs or other Issues).

        The comparisson is made on IDs between previously collected
        entities and all currently present entities on GitHub.

        Returns:
            List[PaginatedList] -- filtered new data without the old ones

        """
        old_knowledge_ids = [int(id) for id in self.previous_knowledge.keys()]
        _LOGGER.debug("Currently gathered ids %s" % old_knowledge_ids)

        new_data = self.get_raw_github_data()

        new_knowledge_ids = [entity.number for entity in new_data]

        only_new_ids = set(new_knowledge_ids) - set(old_knowledge_ids)
        if len(only_new_ids) == 0:
            _LOGGER.info("No new knowledge found for update")
        else:
            _LOGGER.debug("New ids to be examined are %s" % only_new_ids)
        return [x for x in new_data if x.number in only_new_ids]
