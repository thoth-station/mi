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

"""Code frequency entity class."""

from typing import Any, List

from github.StatsCodeFrequency import StatsCodeFrequency
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class CodeFrequency(Entity):
    """Code frequency statistics entity."""

    entity_schema = Schema({"additions": int, "deletions": int})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return [s for s in self.get_raw_github_data() if str(s.week.timestamp()) not in self.previous_knowledge.keys()]

    def store(self, stats: StatsCodeFrequency):
        """Override :func:`~Entity.store`."""
        self.stored_entities[str(stats.week.timestamp())] = {
            "additions": stats.additions,
            "deletions": stats.deletions,
        }

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_stats_code_frequency()
