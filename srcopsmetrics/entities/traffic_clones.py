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

"""Traffic Clones stats class."""

from datetime import datetime
from typing import List

from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity


class TrafficClones(Entity):
    """Traffic entity."""

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, github_entity):
        """Override :func:`~Entity.store`."""
        id = github_entity.timestamp.date()
        date_id = str(id)

        if id == datetime.today().date():
            return

        if date_id in self.previous_knowledge and self.previous_knowledge["uniques"] is not None:
            return

        if date_id not in self.stored_entities:
            self.stored_entities[date_id] = {}

        self.stored_entities[date_id]["uniques"] = github_entity.uniques
        self.stored_entities[date_id]["count"] = github_entity.count

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        github_clones = self.repository.get_clones_traffic()
        self.stored_entities[str(datetime.today().date())] = {
            "uniques": None,
            "count": None,
            "last_two_weeks_uniques": github_clones["uniques"],
            "last_two_weeks_count": github_clones["count"],
        }
        return github_clones["clones"]
