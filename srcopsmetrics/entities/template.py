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

"""Template entity class."""

from typing import Any, List

from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class TemplateEntity(Entity):
    """Template entity.

    Serves as a skelet for implementing a new entity so the contributor
    does not have to spend time copying everything from interface class.

    For further inspiration look at other implemented entities like Issue
    or PullRequest.
    """

    entity_schema = Schema({"extracted_information": Any})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""

    def store(self, github_entity):
        """Override :func:`~Entity.store`."""
        self.stored["key"] = {
            "extracted_information": github_entity.attribute,
        }

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_entity()
