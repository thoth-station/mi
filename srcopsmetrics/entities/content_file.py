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

from github.ContentFile import ContentFile as GithubContentFile
from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)


class ContentFile(Entity):
    """GitHub ContentFile entity."""

    entity_schema = Schema({"name": str, "path": str, "content": str})  # TODO: Adjust content type

    def __init__(self, repository):
        """Initialize with repo and prev knowledge."""
        self.stored = {}
        self.repository = repository
        self.prev_knowledge = None

    def analyse(self) -> PaginatedList:
        """Override :func:`~BaseEntity.analyse`."""
        _LOGGER.info("-------------Content Files Analysis-------------")

        # TODO: Extend to all types of files. Currently only README are considered.
        # TODO: Add all types of README extensions available
        content_file_text = ""
        for file_name in ["README.md", "README.rst"]:

            try:
                content_file = self.repository.get_contents(file_name)
                # file_path = content_file.path
                encoded = content_file.decoded_content
                # TODO: Adjust because most of the files are not text
                content_file_text = encoded.decode("utf-8")
            except Exception as e:
                _LOGGER.info("%r not found for: %r" % (file_name, self.repository.full_name))
                _LOGGER.warning(e)

            # if content_file_text:
            #     with KnowledgeAnalysis(
            #         entity=EntityTypeEnum.CONTENT_FILE.value,
            #     ) as analysis:
            #         accumulated = analysis.store()
            #     break

        if not content_file_text:
            return None

        return None

    def store(self, file_content: GithubContentFile):
        """Override :func:`~BaseEntity.store`."""
        self.stored["content_files"] = {
            "name": file_content[0],
            "path": file_content[1],
            "content": file_content[2],
        }

    def stored_entities(self):
        """Override :func:`~BaseEntity.stored_entities`."""
        return self.stored
