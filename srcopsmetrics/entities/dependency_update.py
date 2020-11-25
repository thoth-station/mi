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

from github.Commit import Commit
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class DependencyUpdate(Entity):
    """Python Dependency update entity.

    Any change (git commit) that was made into the Pipfile.lock file
    is considered a dependency update. It could be either manual (by
    contributor commiting to the file) or automatic (done by bot).
    """

    entity_schema = Schema({"user": str, "date": int})

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        if self.previous_knowledge is None:
            return self.get_raw_github_data()

        return [commit for commit in self.get_raw_github_data() if commit.sha not in self.previous_knowledge.keys()]

    def store(self, commit: Commit):
        """Override :func:`~Entity.store`."""
        self.stored_entities[commit.sha] = {
            "user": self.get_author(commit),
            "date": int(commit.commit.author.date.timestamp()),
        }

    def get_author(self, commit):
        """Get author login of the commit."""
        prs = commit.get_pulls()
        commit_author = commit.author

        if prs.totalCount:
            return prs[0].user.login

        if commit_author:
            return commit_author.login

        return commit.commit.author.name

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_commits(path="Pipfile.lock")
