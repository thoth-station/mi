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
from typing import Optional

from github.Issue import Issue as GithubIssue
from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity
from srcopsmetrics.entities.tools.knowledge import GitHubKnowledge
from srcopsmetrics.github_handling import get_github_object

_LOGGER = logging.getLogger(__name__)

CROSS_REFERENCE_EVENT_KEYWORD = "cross-referenced"

PROJECT_REFERENCE_EVENT_KEYWORDS = {
    "added_to_project",
    "moved_columns_in_project",
    "removed_from_project",
}


class Issue(Entity):
    """GitHub Issue entity."""

    entity_schema = Schema(
        {
            "title": str,
            "body": Any(None, str),
            "created_by": str,
            "created_at": int,
            "closed_by": Any(None, str),
            "closed_at": Any(None, int),
            "labels": {str: {str: Any(int, str)}},
            "interactions": {str: int},
        }
    )

    def get_project_board(self, timeline) -> Optional[Any]:
        """Get current project board for issue."""
        project_board_url = None

        events = {}

        for entry in timeline:

            if entry.event in PROJECT_REFERENCE_EVENT_KEYWORDS:
                event_timestamp = int(entry.created_at.timestamp())
                project_board_url = entry.__dict__["_rawData"]["project_url"]
                events[entry.event] = [(event_timestamp, project_board_url)]

            if entry.event == "added_to_project" or entry.event == "moved_columns_in_project":

                project_board_url = entry.__dict__["_rawData"]["project_url"]
                # column_name = entry.__dict__["_rawData"]["column_name"]
                project_board = get_github_object().get_project(project_board_url)

        return project_board

    def analyse(self) -> PaginatedList:
        """Override :func:`~Entity.analyse`."""
        return self.get_raw_github_data()

    def store(self, issue: GithubIssue):
        """Override :func:`~Entity.store`."""
        if issue.pull_request:
            return  # only issues that are not pull requests are considered

        if issue.number in self.previous_knowledge.index:
            return  # if in previous knowledge, no need to analyse

        if issue.pull_request is not None:
            return  # we analyze issues and prs differentely

        comments = issue.get_comments()
        comments_list = [
            {"created_at": int(com.created_at.timestamp()), "created_by": com.user.login, "body": com.body}
            for com in comments
        ]
        commenters = set([com["created_by"] for com in comments_list])

        timeline = issue.get_timeline()
        cross_references = [
            entry.source.issue.url for entry in timeline if entry.event == CROSS_REFERENCE_EVENT_KEYWORD
        ]

        self.stored_entities[str(issue.number)] = {
            "title": issue.title,
            "body": issue.body,
            "created_by": issue.user.login,
            "created_at": int(issue.created_at.timestamp()),
            "closed_by": issue.closed_by.login if issue.closed_by is not None else None,
            "closed_at": int(issue.closed_at.timestamp()) if issue.closed_at is not None else None,
            "labels": GitHubKnowledge.get_labels(issue),
            "interactions": GitHubKnowledge.get_interactions(comments),
            "first_response_at": min(comments_list, key=lambda x: int(x["created_at"])),
            "commenters_number": len(commenters),
            "comments_number": len(comments_list),
            "comments": comments_list,
            "cross_references": cross_references,
            "cross_references_number": len(cross_references),
            "assignees": [user.login for user in issue.assignees],
        }

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_issues(state="all")
