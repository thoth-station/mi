#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright(C) 2020 Francesco Murdaca, Dominik Tuchyna
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A base class for collecting bot knowledge from GitHub."""

import os
import logging
import time
import json
from datetime import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

from pathlib import Path

from github import Github
from github import GithubObject
from github import Issue
from github import IssueComment
from github import PullRequest
from github import PullRequestReview
from github import PaginatedList
from github.Repository import Repository

from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.github_knowledge_store import GitHubKnowledgeStore

_LOGGER = logging.getLogger(__name__)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

ISSUE_KEYWORDS = {"close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"}

STANDALONE_LABELS = {"size"}


class GitHubKnowledge:
    """Class of methods entity extraction from GitHub."""

    _FILENAME_ENTITY = {"Issue": "issues", "PullRequest": "pull_requests"}

    def connect_to_source(self, project: Tuple[str, str]) -> Repository:
        """Connect to GitHub.

        :param project: Tuple source repo and repo name.
        """
        # Connect using PyGitHub
        g = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50)
        repo_name = project[0] + "/" + project[1]
        repo = g.get_repo(repo_name)

        return repo

    @staticmethod
    def assign_pull_request_size(lines_changes: int) -> str:
        """Assign size of PR is label is not provided."""
        if lines_changes > 1000:
            return "XXL"
        elif lines_changes >= 500 and lines_changes <= 999:
            return "XL"
        elif lines_changes >= 100 and lines_changes <= 499:
            return "L"
        elif lines_changes >= 30 and lines_changes <= 99:
            return "M"
        elif lines_changes >= 10 and lines_changes <= 29:
            return "S"
        elif lines_changes >= 0 and lines_changes <= 9:
            return "XS"

    @staticmethod
    def get_labeled_size(labels: List[str]) -> Union[str, None]:
        """Extract size label from list of labels.

        Size label is in form 'size/<SIZE>', where <SIZE> can be
        XS, S, L, etc...
        """
        for label in labels:
            if label.startswith("size"):
                return label.split("/")[1]

    @staticmethod
    def get_non_standalone_labels(labels: List[str]):
        """Get non standalone labels by filtering them from all of the labels."""
        return [label for label in labels if label not in STANDALONE_LABELS]

    @staticmethod
    def get_referenced_issues(pull_request: PullRequest) -> List[int]:
        """Scan all of the Pull Request comments and get referenced issues.

        Arguments:
            pull_request {PullRequest} -- Pull request for which the referenced
                                        issues are extracted

        Returns:
            List[int] -- IDs of referenced issues within the Pull Request.

        """
        issues_referenced = []
        for comment in pull_request.get_issue_comments():
            message = comment.body.split(" ")
            for idx, word in enumerate(message):
                if word.replace(":", "") in ISSUE_KEYWORDS:
                    try:
                        _LOGGER.info("      ...found keyword referencing issue")
                        referenced_issue_number = message[idx + 1]
                        assert (referenced_issue_number).startswith("https")
                        # last element of url is always the issue number
                        issues_referenced.append(referenced_issue_number.split("/")[-1])
                        _LOGGER.info("      ...referenced issue number present")
                        # we assure that this was really referenced issue
                        # and not just a keyword without number
                    except (IndexError, AssertionError) as e:
                        _LOGGER.info("      ...referenced issue number absent")
                        _LOGGER.debug(str(e))
        _LOGGER.debug("      referenced issues: %s" % issues_referenced)
        return issues_referenced

    @staticmethod
    def get_only_new_entities(old_data: Dict[str, Any], new_data: PaginatedList) -> PaginatedList:
        """Get new entities (whether PRs or other Issues).

        The comparisson is made on IDs between previously collected
        entities and all currently present entities on GitHub.

        Arguments:PaginatedList
            old_data {Dict[str, Any]} -- previously collected knowledge
            new_data {PaginatedList} -- current entities present on GitHub
                            (acquired by GitHub API)

        Returns:
            List[PaginatedList] -- filtered new data without the old ones

        """
        old_knowledge_ids = [int(id) for id in old_data.keys()]
        _LOGGER.debug("Currently gathered ids %s" % old_knowledge_ids)

        new_knowledge_ids = [pr.number for pr in new_data]

        only_new_ids = set(new_knowledge_ids) - set(old_knowledge_ids)
        if len(only_new_ids) == 0:
            _LOGGER.info("No new knowledge found for update")
        else:
            _LOGGER.debug("New ids to be examined are %s" % only_new_ids)

        return [x for x in new_data if x.number in only_new_ids]

    @staticmethod
    def get_interactions(comments) -> Dict:
        """Get overall word count for comments per author."""
        interactions = {comment.user.login: 0 for comment in comments}
        for comment in comments:
            # we count by the num of words in comment
            interactions[comment.user.login] += len(comment.body.split(" "))
        return interactions

    def store_issue(self, issue: Issue, data: Dict[str, Dict[str, Any]]):
        """Extract required information from issue and store it to the current data.

        This is targeted only for issues that are not Pull Requests.

        Arguments:
            issue {Issue} -- Issue (that is not PR).
            data {Dict[str, Union[str, int]])} -- Dictionary where the issue will be stored.

        """
        if issue.pull_request is not None:
            return  # we analyze issues and prs differentely

        labels = [label.name for label in issue.get_labels()]

        data[issue.number] = {
            "created_by": issue.user.login,
            "created_at": issue.created_at.timestamp(),
            "closed_by": issue.closed_by.login,
            "closed_at": issue.closed_at.timestamp(),
            "labels": self.get_non_standalone_labels(labels),
            "interactions": self.get_interactions(issue.get_comments()),
        }

        # TODO: think about saving comments
        # would it be valuable?

    def analyse_issues(
        self, project: Repository, prev_issues: Dict[str, Any], is_local: bool = False
    ) -> Dict[str, Any]:
        """Analyse of every closed issue in repository.

        Arguments:
            project {Repository} -- currently the PyGithub lib is used because of its functionality
                                    ogr unfortunatelly did not provide enough to properly analyze issues

            project_knowledge {Path} -- project directory where the issues knowledge will be stored

        """
        _LOGGER.info("-------------Issues (that are not PR) Analysis-------------")

        current_issues = [issue for issue in project.get_issues(state="closed") if issue.pull_request is None]
        new_issues = self.get_only_new_entities(prev_issues, current_issues)

        if len(new_issues) == 0:
            return

        with GitHubKnowledgeStore(
            entity_type=EntityTypeEnum.ISSUE.value,
            new_entities=new_issues,
            accumulator=prev_issues,
            store_method=self.store_issue,
            is_local=is_local,
        ) as analysis:
            accumulated = analysis.store()
        return accumulated

    @staticmethod
    def extract_pull_request_review_requests(pull_request: PullRequest) -> List[str]:
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
    def extract_pull_request_reviews(pull_request: PullRequest) -> Dict[str, Dict[str, Any]]:
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
            results[review.id] = {
                "author": review.user.login,
                "words_count": len(review.body.split(" ")),
                "submitted_at": review.submitted_at.timestamp(),
                "state": review.state,
            }
        return results

    def store_pull_request(self, pull_request: PullRequest, results: Dict[str, Dict[str, Any]]):
        """Analyse pull request and save its desired features to results.

        Arguments:
            pull_request {PullRequest} -- PR that is going to be inspected and stored.
            results {Dict[str, Dict[str, Any]]} -- dictionary where all the currently
                                                PRs are stored and where the given PR
                                                will be stored.
        """
        commits = pull_request.commits
        # TODO: Use commits to extract information.
        # commits = [commit for commit in pull_request.get_commits()]

        created_at = pull_request.created_at.timestamp()
        closed_at = pull_request.closed_at.timestamp()

        # Get the review approval if it exists
        # approval = next((review for review in reviews if review.state == 'APPROVED'), None)
        # pr_approved = approval.submitted_at.timestamp() if approval is not None else None
        # pr_approved_by = pull_request.approved_by.name if approval is not None else None
        # time_to_approve = pr_approved - created_at if approval is not None else None

        merged_at = pull_request.merged_at.timestamp() if pull_request.merged_at is not None else None

        labels = [label.name for label in pull_request.get_labels()]

        # Evaluate size of PR
        pull_request_size = None

        if labels:
            pull_request_size = self.get_labeled_size(labels)

        if not pull_request_size:
            lines_changes = pull_request.additions + pull_request.deletions
            pull_request_size = self.assign_pull_request_size(lines_changes=lines_changes)

        results[str(pull_request.number)] = {
            "size": pull_request_size,
            "labels": self.get_non_standalone_labels(labels),
            "created_by": pull_request.user.login,
            "created_at": created_at,
            # "approved_at": pr_approved,
            # "approved_by": pr_approved_by,
            # "time_to_approve": time_to_approve,
            "closed_at": closed_at,
            "closed_by": pull_request.as_issue().closed_by.login,
            "merged_at": merged_at,
            "commits_number": commits,
            "referenced_issues": self.get_referenced_issues(pull_request),
            "interactions": self.get_interactions(pull_request.get_issue_comments()),
            "reviews": self.extract_pull_request_reviews(pull_request),
            "requested_reviewers": self.extract_pull_request_review_requests(pull_request),
        }

    def analyse_pull_requests(
        self, project: Repository, prev_pulls: Dict[str, Any], is_local: bool = False
    ) -> Dict[str, Any]:
        """Analyse every closed pull_request in repository.

        Arguments:
            project {Repository} -- currently the PyGithub lib is used because of its functionality
                                    ogr unfortunatelly did not provide enough to properly analyze issues

            project_knowledge {Path} -- project directory where the issues knowledge will be stored
        """
        _LOGGER.info("-------------Pull Requests Analysis (including its Reviews)-------------")

        current_pulls = project.get_pulls(state="closed")
        new_pulls = self.get_only_new_entities(prev_pulls, current_pulls)

        if len(new_pulls) == 0:
            return

        with GitHubKnowledgeStore(
            entity_type=EntityTypeEnum.PULL_REQUEST.value,
            new_entities=new_pulls,
            accumulator=prev_pulls,
            store_method=self.store_pull_request,
            is_local=is_local,
        ) as analysis:
            accumulated = analysis.store()
        return accumulated

    def analyse_entity(self, github_repo: str, project_path: str, github_type: str, is_local: bool = False):
        """Load old knowledge and update it with the newly analysed one and save it.

        Arguments:
            github_repo {str} -- Github repo that will be analysed
            project_path {str} -- The main directory where the knowledge will be stored
            github_type {str} -- Currently can be only "Issue" or "PullRequest"
            is_local {bool} -- If true, the local store will be used for knowledge loading and storing.
        """
        _METHOD_ANALYSIS_ENTITY = {"Issue": self.analyse_issues, "PullRequest": self.analyse_pull_requests}

        filename = self._FILENAME_ENTITY[github_type]
        analyse = _METHOD_ANALYSIS_ENTITY[github_type]

        path = project_path.joinpath("./" + filename + ".json")

        with GitHubKnowledgeStore(is_local=is_local) as store:
            prev_knowledge = store.load_previous_knowledge(
                project_name=github_repo.full_name, file_path=path, knowledge_type=github_type
            )
            new_knowledge = analyse(github_repo, prev_knowledge, is_local=is_local)
            if new_knowledge is not None:
                store.save_knowledge(path, new_knowledge)
