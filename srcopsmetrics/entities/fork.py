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

"""Fork entity class."""

from typing import List

from github.Repository import Repository
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class Fork(Entity):
    """Fork class."""

    entity_schema = Schema(int)

    def analyse(self) -> List[Repository]:
        """Override :func:`~Entity.analyse`."""
        return [repo for repo in self.get_raw_github_data() if repo.owner.login not in self.previous_knowledge.keys()]

    def store(self, fork: Repository):
        """Override :func:`~Entity.store`."""
        self.stored_entities[fork.owner.login] = int(fork.created_at.timestamp())

    def get_raw_github_data(self) -> List[Repository]:
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_forks()
