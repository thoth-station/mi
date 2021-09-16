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

"""Traffic stats class."""

from datetime import datetime
from typing import List

from github.Clones import Clones
from github.Path import Path
from github.Referrer import Referrer
from github.View import View
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity


class Traffic(Entity):
    """Traffic entity."""

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, github_entity):
        """Override :func:`~Entity.store`."""
        id = None
        type = None
        today = datetime.today().date()

        if isinstance(github_entity, View):
            id = github_entity.timestamp

            # today statistics of view and clones are never complete, have to wait for tomorrow
            if id == today:
                return

            type = "view"
        elif isinstance(github_entity, Clones):
            id = github_entity.timestamp

            if id == today:
                return

            type = "clones"
        elif isinstance(github_entity, Referrer):
            id = today
            type = "referrer"
        elif isinstance(github_entity, Path):
            id = today
            type = "path"

        date_id = str(id)

        if date_id not in self.previous_knowledge:
            self.previous_knowledge[date_id] = {}
        elif type in self.previous_knowledge[date_id]:
            return

        if date_id not in self.stored_entities:
            self.stored_entities[date_id] = {}

        data = github_entity.raw_data
        data["type"] = type

        if "timestamp" in data:
            data.__delitem__("timestamp")

        self.stored_entities[date_id] = data

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        traffic_stats = self.repository.get_top_paths()
        traffic_stats.extend(self.repository.get_top_referrers())
        traffic_stats.extend(self.repository.get_views_traffic()["views"])
        traffic_stats.extend(self.repository.get_clones_traffic()["clones"])

        return traffic_stats
