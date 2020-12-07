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

"""Issue entity class."""

import logging

from github.Issue import Issue as GithubIssue
from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity
from srcopsmetrics.entities.tools.knowledge import GitHubKnowledge

_LOGGER = logging.getLogger(__name__)


class Issue(Entity):
    """GitHub Issue entity."""

    entity_schema = Schema(
        {
            "title": str,
            "body": str,
            "created_by": str,
            "created_at": int,
            "closed_by": Any(None, str),
            "closed_at": Any(None, int),
            "labels": {str: {str: Any(int, str)}},
            "interactions": {str: int},
        }
    )

    def analyse(self) -> PaginatedList:
        """Override :func:`~Entity.analyse`."""
        return self.get_only_new_entities()

    def store(self, issue: GithubIssue):
        """Override :func:`~Entity.store`."""
        if issue.pull_request is not None:
            return  # we analyze issues and prs differentely

        self.stored_entities[str(issue.number)] = {
            "title": issue.title,
            "body": issue.body,
            "created_by": issue.user.login,
            "created_at": int(issue.created_at.timestamp()),
            "closed_by": issue.closed_by.login if issue.closed_by is not None else None,
            "closed_at": int(issue.closed_at.timestamp()) if issue.closed_at is not None else None,
            "labels": GitHubKnowledge.get_labels(issue),
            "interactions": GitHubKnowledge.get_interactions(issue.get_comments()),
        }

    def previous_knowledge(self):
        """Override :func:`~Entity.previous_knowledge`."""
        return self.previous_knowledge

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return [issue for issue in self.repository.get_issues(state="all") if not issue.pull_request]
