# Copyright (C) 2021 Dominik Tuchyna
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

"""License Repositories entity class."""

from typing import List
from github.Repository import Repository

from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity
from srcopsmetrics.github_handling import get_github_object

LICENSE_QUERY = "license:"


class LicenseRepos(Entity):
    """Entity for collecting repositories names and their licenses."""

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, github_entity: Repository):
        """Override :func:`~Entity.store`."""
        self.stored_entities[github_entity.full_name] = {"license": "gpl-3.0"}

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        # licenses = pd.read_csv("./srcopsmetrics/entities/licenses.csv").to_numpy().flatten()
        # repos = []
        # for key in licenses:
        #     repos.extend(get_github_object().search_repositories(query=LICENSE_QUERY + key))
        # return repos
        return get_github_object().search_repositories(query=LICENSE_QUERY + "gpl-3.0")
