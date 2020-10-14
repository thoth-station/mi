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
    """Template entity.

    Serves as a skelet for implementing a new entity so the contributor
    does not have to spend time copying everything from interface class.

    For further inspiration look at other implemented entities like Issue
    or PullRequest.
    """

    entity_schema = Schema({"user": str, "date": int})

    def __init__(self, repository):
        """Initialize with repo and prev knowledge."""
        self.stored = {}
        self.repository = repository

    def analyse(self) -> List[Any]:
        """Override :func:`~Entity.analyse`."""
        if self.previous_knowledge is None:
            return self.get_raw_github_data()

        return [commit for commit in self.get_raw_github_data() if commit.sha not in self.previous_knowledge.keys()]

    def store(self, commit: Commit):
        """Override :func:`~Entity.store`."""
        git_commit = commit.commit

        author = commit.author.login if commit.author is not None else git_commit.author.email
        date = git_commit.author.date

        self.stored[commit.sha] = {
            "user": author,
            "date": date.timestamp(),
        }

    def stored_entities(self):
        """Override :func:`~Entity.stored_entities`."""
        return self.stored

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_commits(path="Pipfile.lock")
