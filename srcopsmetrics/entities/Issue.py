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
from typing import Any, List

from github.Issue import Issue
from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities.BaseEntity import BaseEntity
from srcopsmetrics.github_knowledge import GitHubKnowledge

_LOGGER = logging.getLogger(__name__)


class Issues(BaseEntity):
    """GitHub Issue entity."""

    def __init__(self, repository):
        """Initialize with repo and prev knowledge."""
        self.stored = {}
        self.repository = repository
        self.prev_knowledge = None

    def analyse(self) -> PaginatedList:
        """Override :func:`~BaseEntity.analyse`."""
        _LOGGER.info(
            "-------------Issues (that are not PR) Analysis-------------")

        current_issues = [issue for issue in self.repository.get_issues(
            state='all') if issue.pull_request is None]
        new_issues = GitHubKnowledge.get_only_new_entities(
            self.prev_knowledge, current_issues)

        return new_issues

    def store(self, issue: Issue):
        """Override :func:`~BaseEntity.store`."""
        if issue.pull_request is not None:
            return  # we analyze issues and prs differentely

        labels = [label.name for label in issue.get_labels()]

        self.stored[str(issue.number)] = {
            "created_by": issue.user.login,
            "created_at": int(issue.created_at.timestamp()),
            "closed_by": issue.closed_by.login if issue.closed_by is not None else None,
            "closed_at": int(issue.closed_at.timestamp()) if issue.closed_at is not None else None,
            "labels": GitHubKnowledge.get_non_standalone_labels(labels),
            "interactions": GitHubKnowledge.get_interactions(issue.get_comments()),
        }

    def stored_entities(self):
        """Override :func:`~BaseEntity.stored_entities`."""
        return self.stored

    @staticmethod
    def entity_name() -> str:
        """Override :func:`~BaseEntity.entity_name`."""
        return "Issue"

    @staticmethod
    def entitiy_schema() -> Schema:
        """Override :func:`~BaseEntity.entity_schema`."""
        return Schema(
            {
                "created_by": str,
                "created_at": int,
                "closed_by": Any(str, None),
                "closed_at": Any(int, None),
                "labels": [str],
                "interactions": {str: int},
            }
        )

    @staticmethod
    def entities_schema() -> Schema:
        """Override :func:`~BaseEntity.entities_schema`."""
        return Schema(
            {
                str: Issue,
            }
        )
