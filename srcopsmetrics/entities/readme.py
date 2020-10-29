#!/usr/bin/env python3
# Copyright (C) 2020 Dominik Tuchyna
#
# This file is part of SrcOpsMetrics.
#
# SrcOpsMetrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SrcOpsMetrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SrcOpsMetrics.  If not, see <http://www.gnu.org/licenses/>.

"""ContentFile entity class."""

import logging
from typing import List

from github.ContentFile import ContentFile as GithubContentFile
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)


class ReadMe(Entity):
    """GitHub ReadMe entity."""

    entity_schema = Schema({"name": str, "path": str, "content": str, "type": str, "license": str, "size": int,})

    def analyse(self) -> List[GithubContentFile]:
        """Override :func:`~Entity.analyse`."""
        # TODO: recursive Readme analysis - is that a good idea?

        if self.previous_knowledge is None or len(self.previous_knowledge) == 0:
            return [self.get_raw_github_data()]

        if self.previous_knowledge["readme"]["size"] == self.repository.get_readme().size:
            return []

        return [self.get_raw_github_data()]

    def store(self, content_file: GithubContentFile):
        """Override :func:`~Entity.store`."""
        self.stored_entities[content_file.path] = {
            "name": content_file.name,
            "path": content_file.path,
            "content": content_file.decoded_content.decode("utf-8"),
            "type": content_file.type,
            "license": content_file.license,
            "size": content_file.size,
        }

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_readme()
