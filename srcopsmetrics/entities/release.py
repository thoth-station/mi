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

"""Release entity class."""

from typing import Any, List

from github.GitRelease import GitRelease
from github.GitTag import GitTag
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class Release(Entity):
    """Release entity."""

    entity_schema = Schema(
        {
            "release_date": int,
            "note": str,
        })

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return [tag for tag in self.get_raw_github_data() if tag.name not in self.previous_knowledge]

    def store(self, release: GitTag):
        """Override :func:`~Entity.store`."""
        release_pull_request = release.commit.get_pulls()[0]

        self.stored[release.name] = {
            "release_date": release_pull_request.closed_at,
            "note": release_pull_request.body,
        }

    def stored_entities(self):
        """Override :func:`~Entity.stored_entities`."""
        return self.stored

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_tags()
