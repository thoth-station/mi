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

"""Pull Request entity class."""

import logging
from typing import Dict, Generator, List

from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest as GithubPullRequest
from voluptuous.schema_builder import Schema
from voluptuous.validators import Any

from srcopsmetrics.entities import Entity
from srcopsmetrics.entities.tools.knowledge import GitHubKnowledge

_LOGGER = logging.getLogger(__name__)

PullRequestReview = Schema({"author": str, "words_count": int, "submitted_at": int, "state": str})
PullRequestReviews = Schema({str: PullRequestReview})

ISSUE_KEYWORDS = {"close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"}


class PullRequest(Entity):
    """GitHub PullRequest entity."""

    entity_schema = Schema(
        {
            "title": str,
            "body": str,
            "size": str,
            "labels": {str: {str: Any(int, str)}},
            "created_by": str,
            "created_at": int,
            "closed_at": Any(None, int),
            "closed_by": Any(None, str),
            "merged_at": Any(None, int),
            "commits_number": int,
            "referenced_issues": [int],
            "interactions": {str: int},
            "reviews": PullRequestReviews,
            "requested_reviewers": [str],
        }
    )

    def analyse(self) -> PaginatedList:
        """Override :func:`~Entity.analyse`."""
        return self.get_only_new_entities()

    def store(self, pull_request: GithubPullRequest):
        """Override :func:`~Entity.store`."""
        commits = pull_request.commits

        created_at = int(pull_request.created_at.timestamp())
        closed_at = int(pull_request.closed_at.timestamp()) if pull_request.closed_at is not None else None
        merged_at = int(pull_request.merged_at.timestamp()) if pull_request.merged_at is not None else None

        closed_by = pull_request.as_issue().closed_by.login if pull_request.as_issue().closed_by is not None else None

        labels = [label.name for label in pull_request.get_labels()]

        # Evaluate size of PR
        pull_request_size = None
        if labels:
            pull_request_size = GitHubKnowledge.get_labeled_size(labels)

        if not pull_request_size:
            lines_changes = pull_request.additions + pull_request.deletions
            pull_request_size = GitHubKnowledge.assign_pull_request_size(lines_changes=lines_changes)

        self.stored_entities[str(pull_request.number)] = {
            "title": pull_request.title,
            "body": pull_request.body,
            "size": pull_request_size,
            "created_by": pull_request.user.login,
            "created_at": created_at,
            "closed_at": closed_at,
            "closed_by": closed_by,
            "merged_at": merged_at,
            "commits_number": commits,
            "referenced_issues": PullRequest.get_referenced_issues(pull_request),
            "interactions": GitHubKnowledge.get_interactions(pull_request.get_issue_comments()),
            "reviews": self.extract_pull_request_reviews(pull_request),
            "requested_reviewers": self.extract_pull_request_review_requests(pull_request),
            "labels": GitHubKnowledge.get_labels(pull_request.as_issue()),
        }

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_pulls(state="all")

    @staticmethod
    def extract_pull_request_review_requests(pull_request: GithubPullRequest) -> List[str]:
        """Extract features from requested reviews of the PR.

        GitHub understands review requests rather as requested reviewers than actual
        requests.

        Arguments:
            pull_request {PullRequest} -- PR of which we can extract review requests.

        Returns:
            List[str] -- list of logins of the requested reviewers

        """
        requested_users = pull_request.get_review_requests()[0]

        extracted = []
        for user in requested_users:
            extracted.append(user.login)
        return extracted

    @staticmethod
    def extract_pull_request_reviews(pull_request: GithubPullRequest) -> Dict[str, Dict[str, Any]]:
        """Extract required features for each review from PR.

        Arguments:
            pull_request {PullRequest} -- Pull Request from which the reviews will be extracted

        Returns:
            Dict[str, Dict[str, Any]] -- dictionary of extracted reviews. Each review is stored

        """
        reviews = pull_request.get_reviews()
        _LOGGER.info("  -num of reviews found: %d" % reviews.totalCount)

        results = {}
        for idx, review in enumerate(reviews, 1):
            _LOGGER.info("      -analysing review no. %d/%d" % (idx, reviews.totalCount))
            results[str(review.id)] = {
                "author": review.user.login,
                "words_count": len(review.body.split(" ")),
                "submitted_at": int(review.submitted_at.timestamp()),
                "state": review.state,
            }
        return results

    @staticmethod
    def get_referenced_issues(pull_request: GithubPullRequest) -> List[str]:
        """Scan all of the Pull Request comments and get referenced issues.

        Arguments:
            pull_request {PullRequest} -- Pull request for which the referenced
                                        issues are extracted

        Returns:
            List[str] -- IDs of referenced issues within the Pull Request.

        """
        issues_referenced = []
        for comment in pull_request.get_issue_comments():
            for id in PullRequest.search_for_references(comment.body):
                issues_referenced.append(id)

        for id in PullRequest.search_for_references(pull_request.body):
            issues_referenced.append(id)

        _LOGGER.debug("      referenced issues: %s" % issues_referenced)
        return issues_referenced

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
