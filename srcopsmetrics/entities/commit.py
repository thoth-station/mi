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

"""Commit entity."""

from typing import Dict, List

from github.Commit import Commit as GithubCommit
from voluptuous.schema_builder import Schema
from voluptuous import Any
from datetime import datetime

from srcopsmetrics.entities import Entity


class Commit(Entity):
    """Commit entity class."""

    entity_schema = Schema(
        {
            "pull_request": Any(None, int),
            "patch": Schema({str: str}),
            "author": str,
            "message": str,
            "date": int,
            "additions": int,
            "deletions": int,
        }
    )

    def analyse(self) -> List[GithubCommit]:
        """Override :func:`~Entity.analyse`."""
        return [c for c in self.get_raw_github_data() if c.sha not in self.previous_knowledge]

    def store(self, commit: GithubCommit):
        """Override :func:`~Entity.store`."""
        pull_request_id = commit.get_pulls()[0].number if commit.get_pulls().totalCount != 0 else None

        self.stored_entities[commit.sha] = {
            "pull_request": pull_request_id,
            "patch": Commit.get_patches_for_files(commit),
            "author": commit.author.login if commit.author else commit.commit.author.name,
            "message": commit.commit.message,
            "date": int(datetime.strptime(commit.last_modified, "%a, %d %b %Y %X %Z").timestamp()),
            "additions": commit.stats.additions,
            "deletions": commit.stats.deletions,
        }

    @staticmethod
    def get_patches_for_files(commit: GithubCommit) -> Dict[str, str]:
        """Inspect whole patch according to specific files."""
        return {f.filename: f.patch for f in commit.files}

    def get_raw_github_data(self) -> List[GithubCommit]:
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_commits()
