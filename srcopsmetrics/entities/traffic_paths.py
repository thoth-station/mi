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

"""Traffic top Paths stats class."""

from datetime import datetime
from typing import List

from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity


class TrafficPaths(Entity):
    """Traffic Path entity."""

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, github_entity):
        """Override :func:`~Entity.store`."""
        ## To avoid multi indexing, just create a concatenated id on top of entry
        id = f"{self.date_id}_{getattr(github_entity, self.entry_key)}"

        self.stored_entities[id] = github_entity.raw_data

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        self.date_id = str(datetime.today())
        self.entry_key = "path"
        return self.repository.get_top_paths()
