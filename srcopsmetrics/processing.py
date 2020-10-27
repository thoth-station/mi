#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2019, 2020 Francesco Murdaca
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

"""Pre-processing GitHub data."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np

from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import PullRequest
from srcopsmetrics.storage import ProcessedKnowledge
from srcopsmetrics.utils import convert_num2label, convert_score2num

_LOGGER = logging.getLogger(__name__)


class Processing:
    """Pre processing functions for entity extracted."""

    def __init__(self, issues, pull_requests):
        """Initialize with issues and pull requests knowledge.

        If any of the entities is not specified, the behaviour
        of corresponding process function is undefined.
        """
        self.issues = Issue.entities_schema(issues)
        self.pull_requests = PullRequest.entities_schema(pull_requests)

    def regenerate(self):
        """Process stored knowledge and save it."""
        os.environ["PROCESS_KNOWLEDGE"] = "True"
        self.process_issues_creators()
        self.process_issues_closers()
        self.process_issues_closed_by_pr_size()
        self.process_issue_interactions()
        self.process_issue_labels_to_issue_closers()
        self.process_issue_labels_to_issue_creators()
        _LOGGER.info("Processed knowledge generated")

    def process_issues_project_data(self):
        """Pre process of data for a given project repository."""
        if not self.issues:
            return {}

        ids = sorted([int(k) for k in self.issues.keys()])

        project_issues_data = {}
        project_issues_data["contributors"] = []
        project_issues_data["ids"] = []
        project_issues_data["TTCI"] = []
        project_issues_data["created_dts"] = []

        for id in ids:
            id = str(id)
            if self.issues[id]["closed_at"] is None:
                continue

            issue = self.issues[str(id)]

            if issue["created_by"] not in project_issues_data["contributors"]:
                project_issues_data["contributors"].append(issue["created_by"])

            self._analyze_issue_for_project_data(issue_id=id, issue=issue, extracted_data=project_issues_data)

        return project_issues_data

    @staticmethod
    def _analyze_issue_for_project_data(issue_id: int, issue: Dict[str, Any], extracted_data: Dict[str, Any]):
        """Extract project data from Pull Request."""
        extracted_data["ids"].append(issue_id)

        time_to_close = int(issue["closed_at"]) - int(issue["created_at"])
        extracted_data["TTCI"].append(time_to_close / 3600)

        created_dt = datetime.fromtimestamp(issue["created_at"])
        extracted_data["created_dts"].append(created_dt)

        return extracted_data

    def process_prs_project_data(self):
        """Pre process of data for a given project repository."""
        if not self.pull_requests:
            return {}

        ids = sorted([int(k) for k in self.pull_requests.keys()])

        project_reviews_data = {}
        project_reviews_data["contributors"] = []
        project_reviews_data["ids"] = []
        project_reviews_data["created_dts"] = []
        project_reviews_data["reviews_dts"] = []

        project_reviews_data["TTFR"] = []  # Time to First Review (TTFR) [hr]
        project_reviews_data["MTTFR"] = []  # Median TTFR [hr]

        project_reviews_data["TTR"] = []  # Time to Review (TTR) [hr]
        project_reviews_data["MTTR"] = []  # Median TTR [hr]

        project_reviews_data["MTTCI"] = []  # Median TTCI [hr]

        project_reviews_data["PRs_size"] = []  # Pull Request length
        # Pull Request length encoded
        project_reviews_data["encoded_PRs_size"] = []

        for id in ids:
            id = str(id)
            if self.pull_requests[id]["closed_at"] is None:
                continue
            pr = self.pull_requests[str(id)]

            if pr["created_by"] not in project_reviews_data["contributors"]:
                project_reviews_data["contributors"].append(pr["created_by"])

            self._analyze_pr_for_project_data(pr_id=id, pr=pr, extracted_data=project_reviews_data)

        project_reviews_data["last_review_time"] = max(project_reviews_data["reviews_dts"])

        # Encode Pull Request sizes for the contributor
        project_pr_median_size, project_length_score = convert_num2label(
            score=np.median(project_reviews_data["encoded_PRs_size"])
        )
        project_reviews_data["median_pr_length"] = project_pr_median_size
        project_reviews_data["median_pr_length_score"] = project_length_score

        return project_reviews_data

    @staticmethod
    def _analyze_pr_for_project_data(pr_id: int, pr: Dict[str, Any], extracted_data: Dict[str, Any]):
        """Extract project data from Pull Request."""
        if not pr["reviews"]:
            return extracted_data

        # Consider all approved reviews
        pr_approved_dt = [
            datetime.fromtimestamp(review["submitted_at"])
            for review in pr["reviews"].values()
            if review["state"] == "APPROVED"
        ]

        if not pr_approved_dt:
            return extracted_data

        extracted_data["ids"].append(pr_id)

        # PR created timestamp
        pr_created_dt = datetime.fromtimestamp(pr["created_at"])
        extracted_data["created_dts"].append(pr_created_dt)

        # PR first review timestamp (no matter the contributor)
        pr_first_review_dt = datetime.fromtimestamp([r for r in pr["reviews"].values()][0]["submitted_at"])

        ttfr = (pr_first_review_dt - pr_created_dt).total_seconds() / 3600
        extracted_data["TTFR"].append(ttfr)

        mttfr = np.median(extracted_data["TTFR"])
        extracted_data["MTTFR"].append(mttfr)

        project_prs_size = pr["size"]
        extracted_data["PRs_size"].append(project_prs_size)
        extracted_data["encoded_PRs_size"].append(convert_score2num(label=project_prs_size))

        # Take maximum to consider last approved if more than one contributor has to approve
        pr_approved_dt_max = max(pr_approved_dt)

        ttr = (pr_approved_dt_max - pr_created_dt).total_seconds() / 3600
        extracted_data["TTR"].append(ttr)

        mttr = np.median(extracted_data["TTR"])
        extracted_data["MTTR"].append(mttr)

        # PR reviews timestamps
        extracted_data["reviews_dts"] += [r["submitted_at"] for r in pr["reviews"].values()]

        return extracted_data

    def process_contributors_data(self, contributors: List[str]):
        """Pre process of data for contributors in a project repository."""
        pr_ids = sorted([int(k) for k in self.pull_requests.keys()])

        contributors_reviews_data: Dict[str, Any] = {}
        contributors_reviews_data["reviewers"] = []
        contributors_reviews_data["created_dts"] = []

        interactions = {}
        for contributor in contributors:
            contributor_interaction = dict.fromkeys(contributors, 0)
            interactions[contributor] = contributor_interaction

        for pr_id in pr_ids:
            pr = self.pull_requests[str(pr_id)]

            self._analyze_pr_for_contributor_data(pr_id=pr_id, pr=pr, extracted_data=contributors_reviews_data)

            self._analyze_contributors_interaction(
                pr_interactions=pr["interactions"], pr_author=pr["created_by"], interactions_data=interactions
            )

        for reviewer in contributors_reviews_data["reviewers"]:

            number_reviews = 0
            reviews_length = []
            time_reviews = []

            for reviews in contributors_reviews_data[reviewer]["reviews"].values():
                number_reviews += len(reviews)
                review_words = 0
                for review in reviews:
                    review_words += review["words_count"]
                    time_reviews.append(review["submitted_at"])

                reviews_length.append(review_words)

            last_review_dt = max(time_reviews)

            contributors_reviews_data[reviewer]["number_reviews"] = number_reviews
            contributors_reviews_data[reviewer]["median_review_length"] = np.median(reviews_length)
            contributors_reviews_data[reviewer]["last_review_time"] = last_review_dt

            # Encode Pull Request sizes for the contributor
            contributor_prs_size_encoded = [
                convert_score2num(label=pr_size) for pr_size in contributors_reviews_data[reviewer]["PRs_size"]
            ]

            contributor_pr_median_size, contributor_relative_score = convert_num2label(
                score=np.median(contributor_prs_size_encoded)
            )
            contributors_reviews_data[reviewer]["median_pr_length"] = contributor_pr_median_size
            contributors_reviews_data[reviewer]["median_pr_length_score"] = contributor_relative_score
            contributors_reviews_data[reviewer]["interactions"] = interactions[reviewer]

        return contributors_reviews_data

    def _analyze_pr_for_contributor_data(self, pr_id: int, pr: Dict[str, Any], extracted_data: Dict[str, Any]):
        """Extract project data from Pull Request."""
        if not pr["reviews"]:
            return extracted_data

        pr_author = pr["created_by"]

        reviews_submitted_dts_per_reviewer: Dict[str, Any] = {}

        for review in pr["reviews"].values():
            self._extract_review_data(
                pr_id=pr_id,
                pr_author=pr_author,
                contributor_review=review,
                extracted_data=extracted_data,
                reviews_submitted_dts_per_reviewer=reviews_submitted_dts_per_reviewer,
            )

        for reviewer, review_submission_dt in reviews_submitted_dts_per_reviewer.items():

            self._evaluate_reviewer_data(
                pr=pr, reviewer=reviewer, review_submission_dt=review_submission_dt, extracted_data=extracted_data
            )

    @staticmethod
    def _extract_review_data(
        pr_id: int,
        pr_author: str,
        contributor_review: Dict[str, Any],
        extracted_data: Dict[str, Any],
        reviews_submitted_dts_per_reviewer: Dict[str, Any],
    ):
        """Extract contributor data from Pull Request reviews."""
        # Check reviews and discard comment of the author of the PR
        if contributor_review["author"] == pr_author:
            return extracted_data

        if contributor_review["author"] not in extracted_data["reviewers"]:
            extracted_data["reviewers"].append(contributor_review["author"])
            extracted_data[contributor_review["author"]] = {}
            extracted_data[contributor_review["author"]]["reviews"] = {}
            extracted_data[contributor_review["author"]]["ids"] = []
            # Time to First Review (TTFR) [hr]
            extracted_data[contributor_review["author"]]["TTFR"] = []
            extracted_data[contributor_review["author"]]["MTTFR"] = []  # Median TTFR [hr]
            extracted_data[contributor_review["author"]]["TTR"] = []  # Time to Review (TTR) [hr]
            extracted_data[contributor_review["author"]]["MTTR"] = []  # Median TTR [hr]
            extracted_data[contributor_review["author"]]["PRs_size"] = []  # Pull Request length
            # Pull Request length encoded
            extracted_data[contributor_review["author"]]["encoded_PRs_size"] = []

        if pr_id not in extracted_data[contributor_review["author"]]["reviews"].keys():
            extracted_data[contributor_review["author"]]["reviews"][pr_id] = [
                {
                    "words_count": contributor_review["words_count"],
                    "submitted_at": contributor_review["submitted_at"],
                    "state": contributor_review["state"],
                }
            ]
        else:
            extracted_data[contributor_review["author"]]["reviews"][pr_id].append(
                {
                    "words_count": contributor_review["words_count"],
                    "submitted_at": contributor_review["submitted_at"],
                    "state": contributor_review["state"],
                }
            )

        if contributor_review["author"] not in reviews_submitted_dts_per_reviewer.keys():
            reviews_submitted_dts_per_reviewer[contributor_review["author"]] = [contributor_review["submitted_at"]]
        else:
            reviews_submitted_dts_per_reviewer[contributor_review["author"]].append(contributor_review["submitted_at"])

        return extracted_data

    @staticmethod
    def _evaluate_reviewer_data(
        pr: Dict[str, Any], reviewer: str, review_submission_dt: List[int], extracted_data: Dict[str, Any]
    ):
        """Evaluate reviewer data from reviews."""
        if not pr["reviews"]:
            return extracted_data

        dt_approved = [
            datetime.fromtimestamp(review["submitted_at"])
            for review in pr["reviews"].values()
            if review["state"] == "APPROVED" and review["author"] == reviewer
        ]

        if not dt_approved:
            return extracted_data

        # PR created timestamp
        pr_created_dt = datetime.fromtimestamp(pr["created_at"])
        extracted_data["created_dts"].append(pr_created_dt)

        pr_first_review_dt = datetime.fromtimestamp(review_submission_dt[0])
        ttfr = (pr_first_review_dt - pr_created_dt).total_seconds() / 3600
        extracted_data[reviewer]["TTFR"] = ttfr

        mttfr = np.median(extracted_data[reviewer]["TTFR"])
        extracted_data[reviewer]["MTTFR"].append(mttfr)

        project_prs_size = pr["size"]
        extracted_data[reviewer]["PRs_size"].append(project_prs_size)
        extracted_data[reviewer]["encoded_PRs_size"].append(convert_score2num(label=project_prs_size))

        # Take maximum to consider last approved if more than one contributor has to approve
        pr_approved_dt = max(dt_approved)

        ttr = (pr_approved_dt - pr_created_dt).total_seconds() / 3600
        extracted_data[reviewer]["TTR"].append(ttr)

        mttr = np.median(extracted_data[reviewer]["TTR"])
        extracted_data[reviewer]["MTTR"].append(mttr)

    @staticmethod
    def _analyze_contributors_interaction(
        pr_interactions: Dict[str, int], pr_author: str, interactions_data: Dict[str, Dict[str, int]]
    ):
        """Analyze project contributors interactions."""
        if not pr_interactions:
            return interactions_data

        for contributor, interaction_info in pr_interactions.items():
            if contributor != pr_author:
                # Check if it is a bot.
                if contributor not in interactions_data[pr_author].keys():
                    pass
                else:
                    interactions_data[pr_author][contributor] += interaction_info

        return interactions_data

    @ProcessedKnowledge
    def process_pr_creators(self) -> Dict[str, int]:
        """Analyse number of created pull requests for each contributor that has created pr.

        :rtype: { <contributor> : <number of created pull requrests> }
        """
        creators = {}
        for pr_id in self.pull_requests.keys():
            pr_author = self.pull_requests[pr_id]["created_by"]
            if pr_author not in creators:
                creators[pr_author] = 0
            creators[pr_author] += 1

        return creators

    @ProcessedKnowledge
    def process_pr_reviewers(self) -> Dict[str, int]:
        """Analyse number of reviewed pull requests for each contributor that has reviewed pr.

        :rtype: { <contributor> : <number of reviews> }
        """
        reviewers = {}
        for pr_id in self.pull_requests.keys():
            for review in self.pull_requests[pr_id]["reviews"].values():
                reviewer = review["author"]
                if reviewer not in reviewers:
                    reviewers[reviewer] = 0
                reviewers[reviewer] += 1

        return reviewers

    @ProcessedKnowledge
    def process_issues_creators(self) -> Dict[str, int]:
        """Analyse number of created issues for each contributor that has created issue.

        :rtype: { <contributor> : <number of created issues> }
        """
        creators = {}
        for issue_id in self.issues.keys():
            issue_author = self.issues[issue_id]["created_by"]
            if issue_author not in creators:
                creators[issue_author] = 0
            creators[issue_author] += 1

        return creators

    @ProcessedKnowledge
    def process_issues_closers(self) -> Dict[str, int]:
        """Analyse number of closed issues for each contributor that has closed issue.

        A closure is also when the contributor's Pull Request closed the issue.

        :rtype: { <contributor> : <number of closed issues> }
        """
        closers = {}
        for issue_id in self.issues.keys():
            issue_author = self.issues[issue_id]["closed_by"]
            if issue_author is None:
                continue

            if issue_author not in closers:
                closers[issue_author] = 0
            closers[issue_author] += 1

        for pr_id in self.pull_requests.keys():
            if self.pull_requests[pr_id]["merged_at"] is None:
                continue

            pr_author = self.pull_requests[pr_id]["created_by"]
            for _ in self.pull_requests[pr_id]["referenced_issues"]:
                if pr_author not in closers:
                    closers[pr_author] = 0
                closers[pr_author] += 1

        return closers

    @ProcessedKnowledge
    def process_issue_interactions(self) -> Dict[str, Dict[str, int]]:
        """Analyse interactions between contributors with respect to closed issues in project.

        The interaction is analysed between any issue creator and any person who has ever commented
        any issue created by the issue creator.

        Interaction number is just a sum of all of the words in a comment.

        :rtype: { <contributor> : { <commenter> : <overall interaction number throughout the project> } }
        """
        authors: Dict[str, Dict[str, int]] = {}
        for issue_id in self.issues.keys():
            issue_author = self.issues[issue_id]["created_by"]
            if issue_author not in authors:
                authors[issue_author] = {}
            for interactioner in self.issues[issue_id]["interactions"].keys():
                if interactioner == issue_author:
                    continue
                if interactioner not in authors[issue_author]:
                    authors[issue_author][interactioner] = 0
                authors[issue_author][interactioner] += self.issues[issue_id]["interactions"][interactioner]
        return authors

    @ProcessedKnowledge
    def process_issue_labels_with_ttci(self) -> Dict[str, Tuple[List[float], List[int]]]:
        """Analyse Time To Close Issue for any label that labeled closed issue.

        :param self.issues:Dict:
        :rtype: { <label> : [[<closed_issue_ttci>], [<closed_issue_creation_date>]] }
        """
        issues: Dict[str, Tuple[List[float], List[int]]] = {}
        for issue_id in (i for i in self.issues.keys() if self.issues[i]["closed_at"]):
            issue_labels = self.issues[issue_id]["labels"]
            ttci = int(self.issues[issue_id]["closed_at"]) - int(self.issues[issue_id]["created_at"])

            for label in issue_labels:
                if label not in issues:
                    issues[label] = ([], [])
                issues[label][0].append(ttci / 3600)
                issues[label][1].append(int(self.issues[issue_id]["created_at"]))
        return issues

    @ProcessedKnowledge
    def process_issue_labels_to_issue_creators(self) -> Dict[str, Dict[str, int]]:
        """Analyse number of every label (of closed issues) for any contributor that has created an issue.

        :rtype: { <issue_creator> : { <issue_label> : <label_occurence_in_created_issues> } }
        """
        authors: Dict[str, Dict[str, int]] = {}
        for issue_id in self.issues.keys():
            issue_author = self.issues[issue_id]["created_by"]
            if issue_author not in authors:
                authors[issue_author] = {}
            for label in self.issues[issue_id]["labels"]:
                if label not in authors[issue_author]:
                    authors[issue_author][label] = 0
                authors[issue_author][label] += 1
        return authors

    @ProcessedKnowledge
    def process_issue_labels_to_issue_closers(self) -> Dict[str, Dict[str, int]]:
        """Analyse number of every label (of closed issues) for any contributor that has closed an issue.

        A issue closer is also a contributor, whose Pull Request closed the issue (by referencing it)

        :rtype: { <issue_closer> : { <issue_label> : <label_occurence_in_closed_issues> } }
        """
        closers: Dict[str, Dict[str, int]] = {}
        for issue_id in self.issues.keys():
            issue_closer = self.issues[issue_id]["closed_by"]
            if issue_closer not in closers:
                closers[issue_closer] = {}
            for label in self.issues[issue_id]["labels"]:
                if label not in closers[issue_closer]:
                    closers[issue_closer][label] = 0
                closers[issue_closer][label] += 1

        for pr_id in self.pull_requests.keys():
            if self.pull_requests[pr_id]["merged_at"] is None:
                continue

            pr_author = self.pull_requests[pr_id]["created_by"]
            if pr_author not in closers:
                closers[pr_author] = {}

            for ref_issue in self.pull_requests[pr_id]["referenced_issues"]:
                if ref_issue not in self.issues.keys():
                    # TODO: re-implement extracting referenced issues by event @mentioned
                    continue

                for label in self.issues[ref_issue]["labels"]:
                    if label not in closers[pr_author]:
                        closers[pr_author][label] = 0
                    closers[pr_author][label] += 1

        return closers

    @ProcessedKnowledge
    def process_issues_closed_by_pr_size(self) -> Dict[str, List[int]]:
        """Analyse number of closed issues to every Pull Request size.

        :rtype: { <pr_size_label> : <number_of_closed_issues> }
        """
        issues: Dict[str, List[int]] = {}
        for pr_id in (i for i in self.pull_requests.keys() if self.pull_requests[i]["closed_at"]):
            for issue_id in (i for i in self.pull_requests[pr_id]["referenced_issues"] if self.issues[i]["closed_at"]):
                ttci = int(self.issues[issue_id]["closed_at"] - int(self.issues[issue_id]["created_at"]))

                size = self.pull_requests[pr_id]["size"]

                if size not in issues:
                    issues[size] = []
                issues[size].append(ttci)
        return issues

    @ProcessedKnowledge
    def overall_issues_status(self) -> Dict[str, int]:
        """Analyse current statuses of issues.

        :rtype: { <issue_status> : <num_of_corresponding_entities> }
        """
        statuses = {
            "active": 0,
            "closed": 0,
        }
        for id in self.issues.keys():
            status = "active" if self.issues[id]["closed_at"] is None else "closed"
            statuses[status] += 1
        return statuses

    @ProcessedKnowledge
    def overall_prs_status(self) -> Dict[str, int]:
        """Analyse current statuses of pull requests.

        :rtype: { <pull_request_status> : <num_of_corresponding_entities> }
        """
        statuses = {
            "active": 0,
            "merged": 0,
            "rejected": 0,
        }
        for id in self.pull_requests.keys():
            status = (
                "merged"
                if self.pull_requests[id]["merged_at"]
                else "rejected"
                if self.pull_requests[id]["closed_at"]
                else "active"
            )
            statuses[status] += 1
        return statuses
