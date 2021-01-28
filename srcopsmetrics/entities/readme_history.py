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

"""ReadMeHistory entity class."""

import logging
from datetime import datetime
from typing import List

from github.ContentFile import ContentFile as GithubContentFile
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities.readme import ReadMe

_LOGGER = logging.getLogger(__name__)


class ReadMeHistory(ReadMe):
    """README History entity."""

    entity_schema = Schema({"name": str, "path": str, "content": str, "type": str, "size": int})

    def analyse(self) -> List[GithubContentFile]:
        """Override :func:`~Entity.analyse`."""
        readme = self.get_raw_github_data()

        if self.previous_knowledge is None or len(self.previous_knowledge) == 0:
            return [readme]

        date = int(datetime.strptime(readme.last_modified, "%a, %d %b %Y %X %Z").timestamp())
        if not readme or str(date) in self.previous_knowledge:
            return []

        return [readme]

    def store(self, content_file: GithubContentFile):
        """Override :func:`~Entity.store`."""
        last_modified = int(datetime.strptime(content_file.last_modified, "%a, %d %b %Y %X %Z").timestamp())
        self.stored_entities[str(last_modified)] = {
            "name": content_file.name,
            "path": content_file.path,
            "content": content_file.decoded_content.decode("utf-8"),
            "type": content_file.type,
            "size": content_file.size,
        }
