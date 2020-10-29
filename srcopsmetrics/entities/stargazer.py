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

"""Stargazer entity class."""

from typing import Any, List

from github.Stargazer import Stargazer as GithubStargazer
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class Stargazer(Entity):
    """Repository Stargazer entity."""

    entity_schema = Schema(int)

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return [s for s in self.get_raw_github_data() if s.user.login not in self.previous_knowledge]

    def store(self, stargazer: GithubStargazer):
        """Override :func:`~Entity.store`."""
        self.stored_entities[stargazer.user.login] = int(stargazer.starred_at.timestamp())

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_stargazers_with_dates()
