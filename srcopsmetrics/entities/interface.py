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

from abc import ABCMeta, abstractmethod
from typing import Any, Collection, Iterable

from github.Repository import Repository
from voluptuous.schema_builder import Schema

from srcopsmetrics.storage import KnowledgeStorage


class Entity(metaclass=ABCMeta):
    """This class defines interface every entity class should implement."""

    @abstractmethod
    def __init__(self, repository: Repository):
        """Initialize entity with github repository.

        Every entity should be initialized just with the repository name."""
        

    @abstractmethod
    def init_previous_knowledge(self, is_local: bool):
        """Every entity must have a previous knowledge initialization method."""
        storage = KnowledgeStorage(is_local=is_local)
        path = storage.get_entity_file_path(entity=self)

        self.previous_knowledge = storage.load_previous_knowledge( # type: ignore
            project_name=self.repository.full_name, file_path=path, entity=self.__class__
        )

    @property
    @abstractmethod
    def repository(self) -> Repository:
        """Repository object as defined in GitHub API documentation.

        Currently only PyGithub supported. 
        """
        return self.repository

    @property
    @abstractmethod
    def previous_knowledge(self) -> Collection:
        """Previous knowledge of given entity.

        Can be anything iterable. 
        """

    @property
    @abstractmethod
    @classmethod
    def name(self) -> str:
        """Entity name as defined in GitHub API documentation.

        If this entity is not part of GitHub API, its name is up to contributor.
        """
        return type(self).__name__

    @property
    @abstractmethod
    @classmethod
    def filename(cls) -> str:
        """File name of stored knowledge.

        If this entity is not part of GitHub API, its name is up to contributor.
        """
        return cls.__name__

    @property
    @abstractmethod
    def entity_schema(self) -> Schema:
        """Return schema of a single entity that is analysed and stored.

        Entity is stored inside the entities_schema.
        """

    @property
    @abstractmethod
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
