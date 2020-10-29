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

import logging
from datetime import datetime
from typing import Any, List, Union

from github.GitRelease import GitRelease
from github.Tag import Tag
from semver import VersionInfo
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)


class Release(Entity):
    """Release entity."""

    entity_schema = Schema({"release_date": int, "note": str,})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        return [tag for tag in self.get_raw_github_data() if tag.commit.sha not in self.previous_knowledge]

    def store(self, release: Union[Tag, GitRelease]):
        """Override :func:`~Entity.store`."""
        is_tag = issubclass(Tag, type(release))

        version_name = release.name
        name = version_name[1:] if len(version_name) > 0 and version_name[0] == "v" else version_name

        try:
            version = VersionInfo.parse(name)
        except ValueError:
            _LOGGER.info("Found tag is not a valid release, skipping")
            return

        self.stored_entities[release.commit.sha] = {
            "major": version.major,
            "minor": version.minor,
            "patch": version.patch,
            "prerelease": version.prerelease,
            "build": version.build,
            "release_date": self.__class__.get_tag_release_date(release) if is_tag else release.created_at.timestamp(),
            "note": self.__class__.get_tag_release_note(release) if is_tag else release.body,
        }

    @staticmethod
    def get_tag_release_date(release_tag: Tag):
        """Get release date from regular Tag."""
        if release_tag.commit.get_pulls().totalCount == 0:
            return datetime.strptime(release_tag.commit.last_modified, "%a, %d %b %Y %X %Z").timestamp()

        return release_tag.commit.get_pulls()[0].closed_at.timestamp()

    @staticmethod
    def get_tag_release_note(release_tag: Tag):
        """Get release note from regular Tag."""
        if release_tag.commit.get_pulls().totalCount == 0:
            return release_tag.commit.commit.message

        return release_tag.commit.get_pulls()[0].body

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        releases = [r for r in self.repository.get_releases()]
        releases.extend([t for t in self.repository.get_tags()])

        return releases
