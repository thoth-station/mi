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

"""BaseEntity interface class."""

from abc import abstractmethod, ABCMeta
from typing import Any, List

from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema


class BaseEntity(metaclass=ABCMeta):
    """BaseEntity defines interface every entity class should implement."""

    @property
    @abstractmethod
    def entity_name() -> str:
        """Entity name as defined in GitHub API documentation.

        If this entity is not part of GitHub API, its name is up to contributor.
        """
        pass

    @property
    @abstractmethod
    def entitiy_schema() -> Schema:
        """Return schema of a single entity that is analysed and stored.

        Entity is stored inside the entities_schema.
        """
        pass

    @property
    @abstractmethod
    def entities_schema() -> Schema:
        """Return schema of how all of the entities of repo are stored."""
        pass

    @abstractmethod
    def analyse(self) -> Any[PaginatedList, List]:
        """Gather list of all entities that are later analysed using store method.

        :rtype: gathered list
        """
        pass

    @abstractmethod
    def store(self, single_entity):
        """Store passed entity.

        All the stored entities are then retrieved by stored_entities function.
        """
        pass

    @abstractmethod
    def stored_entities(self):
        """Return analysed entities."""
        pass
