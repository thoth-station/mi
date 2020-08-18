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
from typing import Generator, List, Optional

from github.Issue import Issue as GithubIssue
from github.PullRequest import PullRequest
from github.PaginatedList import PaginatedList
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities.BaseEntity import BaseEntity
from srcopsmetrics.github_knowledge import GitHubKnowledge

_LOGGER = logging.getLogger(__name__)

ISSUE_KEYWORDS = {"close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"}


class Issue(BaseEntity):
    """GitHub Issue entity."""

    entity_name = "Issue"

    entity_schema = Schema(
        {
            "created_by": str,
            "created_at": int,
            "closed_by": Optional[str],
            "closed_at": Optional[int],
            "labels": [str],
            "interactions": {str: int},
        }
    )

    entities_schema = Schema({str: entity_schema})

    def __init__(self, repository):
        """Initialize with repo and prev knowledge."""
        self.stored = {}
        self.repository = repository
        self.prev_knowledge = None

    def analyse(self) -> PaginatedList:
        """Override :func:`~BaseEntity.analyse`."""
        _LOGGER.info("-------------Issues (that are not PR) Analysis-------------")

        current_issues = [issue for issue in self.repository.get_issues(state="all") if issue.pull_request is None]
        new_issues = GitHubKnowledge.get_only_new_entities(self.prev_knowledge, current_issues)

        return new_issues

    def store(self, issue: GithubIssue):
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
    def search_for_references(body: str) -> Generator[str, None, None]:
        """Return generator for iterating through referenced IDs in a comment."""
        if body is None:
            return

        message = body.split(" ")
        for idx, word in enumerate(message):
            if word.replace(":", "").lower() not in ISSUE_KEYWORDS:
                return

            _LOGGER.info("      ...found keyword referencing issue")
            referenced_issue_number = message[idx + 1]
            if referenced_issue_number.startswith("https"):
                # last element of url is always the issue number
                ref_issue = referenced_issue_number.split("/")[-1]
            elif referenced_issue_number.startswith("#"):
                ref_issue = referenced_issue_number.replace("#", "")
            else:
                _LOGGER.info("      ...referenced issue number absent")
                _LOGGER.debug("      keyword message: %s" % body)
                return

            if not referenced_issue_number.isnumeric():
                _LOGGER.info("      ...referenced issue number in incorrect format")
                return

            _LOGGER.info("      ...referenced issue number: %s" % ref_issue)
            yield ref_issue

    @staticmethod
    def get_referenced_issues(self, pull_request: PullRequest) -> List[str]:
        """Scan all of the Pull Request comments and get referenced issues.

        Arguments:
            pull_request {PullRequest} -- Pull request for which the referenced
                                        issues are extracted

        Returns:
            List[str] -- IDs of referenced issues within the Pull Request.

        """
        issues_referenced = []
        for comment in pull_request.get_issue_comments():
            for id in self.search_for_references(comment.body):
                issues_referenced.append(id)

        for id in self.search_for_references(pull_request.body):
            issues_referenced.append(id)

        _LOGGER.debug("      referenced issues: %s" % issues_referenced)
        return issues_referenced
