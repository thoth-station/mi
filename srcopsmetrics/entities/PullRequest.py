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
from typing import Any, Dict, List, Optional

from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest as GithubPullRequest
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities.BaseEntity import BaseEntity
from srcopsmetrics.github_knowledge import GitHubKnowledge

_LOGGER = logging.getLogger(__name__)

PullRequestReview = Schema({"author": str, "words_count": int, "submitted_at": int, "state": str})
PullRequestReviews = Schema({str: PullRequestReview})


class PullRequest(BaseEntity):
    """GitHub PullRequest entity."""

    entity_name = "PullRequest"

    entity_schema = Schema(
        {
            "size": str,
            "labels": [str],
            "created_by": str,
            "created_at": int,
            # "approved_at": pr_approved,
            # "approved_by": pr_approved_by,
            # "time_to_approve": time_to_approve,
            "closed_at": Optional[int],
            "closed_by": Optional[str],
            "merged_at": Optional[int],
            "commits_number": int,
            "referenced_issues": [int],
            "interactions": {str: int},
            "reviews": PullRequestReviews,
            "requested_reviewers": [str],
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
        _LOGGER.info("-------------Pull Requests Analysis (including its Reviews)-------------")

        current_pulls = self.repository.get_pulls(state="all")
        new_pulls = GitHubKnowledge.get_only_new_entities(self.prev_knowledge, current_pulls)

        return new_pulls

    def store(self, pull_request: GithubPullRequest):
        """Override :func:`~BaseEntity.store`."""
        commits = pull_request.commits
        # TODO: Use commits to extract information.
        # commits = [commit for commit in pull_request.get_commits()]

        created_at = int(pull_request.created_at.timestamp())
        closed_at = int(pull_request.closed_at.timestamp()) if pull_request.closed_at is not None else None
        merged_at = int(pull_request.merged_at.timestamp()) if pull_request.merged_at is not None else None

        closed_by = pull_request.as_issue().closed_by.login if pull_request.as_issue().closed_by is not None else None

        labels = [label.name for label in pull_request.get_labels()]

        # Evaluate size of PR
        pull_request_size = None
        if labels:
            pull_request_size = self.get_labeled_size(labels)

        if not pull_request_size:
            lines_changes = pull_request.additions + pull_request.deletions
            pull_request_size = self.assign_pull_request_size(lines_changes=lines_changes)

        self.stored[str(pull_request.number)] = {
            "size": pull_request_size,
            "labels": self.get_non_standalone_labels(labels),
            "created_by": pull_request.user.login,
            "created_at": created_at,
            "closed_at": closed_at,
            "closed_by": closed_by,
            "merged_at": merged_at,
            "commits_number": commits,
            "referenced_issues": self.get_referenced_issues(pull_request),
            "interactions": self.get_interactions(pull_request.get_issue_comments()),
            "reviews": self.extract_pull_request_reviews(pull_request),
            "requested_reviewers": self.extract_pull_request_review_requests(pull_request),
        }

    def stored_entities(self):
        """Override :func:`~BaseEntity.stored_entities`."""
        return self.stored

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
