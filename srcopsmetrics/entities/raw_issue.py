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

"""Raw data Issue."""

from github.Issue import Issue
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity
import logging


_LOGGER = logging.getLogger(__name__)


class RawIssue(Entity):
    """Issue class as returned by GitHub API."""

    entity_schema = Schema({int: {str: Any(str, int)}})

    def analyse(self):
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, entity: Issue):
        """Override :func:`~Entity.store`."""
        if entity.number in self.previous_knowledge.index:
            _LOGGER.debug("Issue %s already analysed, skipping")
            return

        id = entity.number

        raw_response_dict = entity.raw_data
        raw_response_dict.__delitem__("id")

        self.stored_entities[id] = raw_response_dict

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_issues()
