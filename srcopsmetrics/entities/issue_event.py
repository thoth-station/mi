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

"""Atomic entity Issue Event."""

from typing import List

from github.IssueEvent import IssueEvent as GithubIssueEvent
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity


class IssueEvent(Entity):
    """Issue Event entity class.

    This entity is atomic and raw response from GitHub is extracted.
    Entities are recodnized by their unique IDs.
    """

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return self.get_latest_new_entities()

    def get_latest_new_entities(self):
        """Return only events that are not in previous knowledge.

        Atomicity validates all the other entities.
        """
        latest_entities = []

        ## events are returned chronologically from latest to oldest
        for event in self.get_raw_github_data():
            if event.id in self.previous_knowledge:
                break
            latest_entities.append(event)

        return latest_entities

    def store(self, event: GithubIssueEvent):
        """Override :func:`~Entity.store`."""
        id = event.id

        raw_response_dict = event.raw_data
        raw_response_dict.__delitem__("id")

        self.stored_entities[id] = raw_response_dict

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_issues_events()
