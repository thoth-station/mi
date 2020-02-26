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

import numpy as np

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from pathlib import Path
from datetime import timedelta
from datetime import datetime

from srcopsmetrics.github_knowledge_store import GitHubKnowledgeStore
from srcopsmetrics.utils import convert_num2label
from srcopsmetrics.utils import convert_score2num

from srcopsmetrics.entity_schema import IssueSchema
from srcopsmetrics.entity_schema import PullRequestSchema

_LOGGER = logging.getLogger(__name__)


class PreProcessing:
    """Pre processing functions for entity extracted."""

    def retrieve_knowledge(
        self, knowledge_path: Path, project: str, entity_type: str, is_local: bool = False
    ) -> Union[Dict[str, Any], None]:
        """Retrieve knowledge (PRs) collected for a project."""
        project_knowledge_path = knowledge_path.joinpath("./" + f"{project}")

        with GitHubKnowledgeStore(is_local=is_local) as store:
            pull_requests_data_path = project_knowledge_path.joinpath(
                "./" + store._FILENAME_ENTITY[entity_type] + ".json"
            )
            data = store.load_previous_knowledge(project, pull_requests_data_path, entity_type)

        if data:
            return data
        else:
            _LOGGER.error("No previous knowledge found for %s" % project)

    def pre_process_issues_project_data(self, data: Dict[str, Any]):
        """Pre process of data for a given project repository."""
        if not data:
            return {}
        ids = sorted([int(k) for k in data.keys()])

        project_issues_data = {}

        project_issues_data["contributors"] = []
        project_issues_data["ids"] = []
        project_issues_data["TTCI"] = []
        project_issues_data["created_dts"] = []

        for id in ids:
            issue = data[str(id)]

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

    def pre_process_prs_project_data(self, data: Dict[str, Any]):
        """Pre process of data for a given project repository."""
        if not data:
            return {}
        ids = sorted([int(k) for k in data.keys()])

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
            pr = data[str(id)]

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
        pr_approved_dt = max(pr_approved_dt)

        ttr = (pr_approved_dt - pr_created_dt).total_seconds() / 3600
        extracted_data["TTR"].append(ttr)

        mttr = np.median(extracted_data["TTR"])
        extracted_data["MTTR"].append(mttr)

        # PR reviews timestamps
        extracted_data["reviews_dts"] += [r["submitted_at"] for r in pr["reviews"].values()]

        return extracted_data

    def pre_process_contributors_data(self, data: Dict[str, Any], contributors: List[str]):
        """Pre process of data for contributors in a project repository."""
        pr_ids = sorted([int(k) for k in data.keys()])

        contributors_reviews_data = {}
        contributors_reviews_data["reviewers"] = []
        contributors_reviews_data["created_dts"] = []

        interactions = {}
        for contributor in contributors:
            contributor_interaction = dict.fromkeys(contributors, 0)
            interactions[contributor] = contributor_interaction

        for pr_id in pr_ids:
            pr = data[str(pr_id)]

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
            if len(contributors_reviews_data[reviewer]["PRs_size"]) > 1:
                contributor_prs_size_encoded = [
                    convert_score2num(label=pr_size) for pr_size in contributors_reviews_data[reviewer]["PRs_size"]
                ]
            else:
                contributor_prs_size_encoded = convert_score2num(label=contributors_reviews_data[reviewer]["PRs_size"])

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

        reviews_submitted_dts_per_reviewer = {}

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
        pr: Dict[str, Any], reviewer: str, review_submission_dt: datetime.timestamp, extracted_data: Dict[str, Any]
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

    def pre_process_issues_creators(self, issues_data: IssueSchema) -> Dict[str, int]:
        """Analyse number of created issues for each contributor that has created issue.

        :type issues_data:IssueSchema:
        :param issues_data:IssueSchema:
        :rtype: { <contributor> : <number of created issues> }
        """
        creators = {}
        for issue_id in issues_data.keys():
            issue_author = issues_data[issue_id]["created_by"]
            if issue_author not in creators:
                creators[issue_author] = 0
            creators[issue_author] += 1

        return creators

    def pre_process_issues_closers(self, issues_data: IssueSchema, pr_data: PullRequestSchema) -> Dict[str, int]:
        """Analyse number of closed issues for each contributor that has closed issue.

        A closure is also when the contributor's Pull Request closed the issue.

        :param issues_data:IssueSchema:
        :param pr_data:PullRequestSchema:
        :rtype: { <contributor> : <number of closed issues> }
        """
        closers = {}
        for issue_id in issues_data.keys():
            issue_author = issues_data[issue_id]["closed_by"]
            if issue_author not in closers:
                closers[issue_author] = 0
            closers[issue_author] += 1

        for pr_id in pr_data.keys():
            if pr_data[pr_id]["merged_at"] is None:
                continue

            pr_author = pr_data[pr_id]["created_by"]
            for _ in pr_data[pr_id]["referenced_issues"]:
                if pr_author not in closers:
                    closers[pr_author] = 0
                closers[pr_author] += 1

        return closers

    def pre_process_issue_interactions(self, issues_data: IssueSchema) -> Dict[str, Dict[str, int]]:
        """Analyse interactions between contributors with respect to closed issues in project.

        The interaction is analysed between any issue creator and any person who has ever commented
        any issue created by the issue creator.

        Interaction number is just a sum of all of the words in a comment.

        :param issues_data:IssueSchema:
        :rtype: { <contributor> : { <commenter> : <overall interaction number throughout the project> } }
        """
        authors = {}
        for issue_id in issues_data.keys():
            issue_author = issues_data[issue_id]["created_by"]
            if issue_author not in authors:
                authors[issue_author] = {}
            for interactioner in issues_data[issue_id]["interactions"].keys():
                if interactioner == issue_author:
                    continue
                if interactioner not in authors[issue_author]:
                    authors[issue_author][interactioner] = 0
                authors[issue_author][interactioner] += issues_data[issue_id]["interactions"][interactioner]
        return authors

    def pre_process_issue_labels_with_ttci(
        self, issues_data: IssueSchema
    ) -> Dict[str, List[Tuple[List[float], List[datetime]]]]:
        """Analyse Time To Close Issue for any label that labeled closed issue.

        :param issues_data:Dict:
        :rtype: { <label> : [[<closed_issue_ttci>], [<closed_issue_creation_date>]] }
        """
        issues = {}
        for issue_id in issues_data.keys():
            issue_labels = issues_data[issue_id]["labels"]
            ttci = int(issues_data[issue_id]["closed_at"] - int(issues_data[issue_id]["created_at"]))
            for label in issue_labels:
                if label not in issues:
                    issues[label] = [[], []]
                issues[label][0].append(ttci / 3600)
                issues[label][1].append(datetime.fromtimestamp(issues_data[issue_id]["created_at"]))
        return issues

    def pre_process_issue_labels_to_issue_creators(self, issues_data: IssueSchema) -> Dict[str, Dict[str, int]]:
        """Analyse number of every label (of closed issues) for any contributor that has created an issue.

        :param issues_data:IssueSchema:
        :rtype: { <issue_creator> : { <issue_label> : <label_occurence_in_created_issues> } }
        """
        authors = {}
        for issue_id in issues_data.keys():
            issue_author = issues_data[issue_id]["created_by"]
            if issue_author not in authors:
                authors[issue_author] = {}
            for label in issues_data[issue_id]["labels"]:
                if label not in authors[issue_author]:
                    authors[issue_author][label] = 0
                authors[issue_author][label] += 1
        return authors

    def pre_process_issue_labels_to_issue_closers(
        self, issues_data: IssueSchema, pull_requests_data: PullRequestSchema
    ) -> Dict[str, Dict[str, int]]:
        """Analyse number of every label (of closed issues) for any contributor that has closed an issue.

        A issue closer is also a contributor, whose Pull Request closed the issue (by referencing it)

        :param issues_data:IssueSchema:
        :param pull_requests_data:PullRequestSchema:
        :rtype: { <issue_closer> : { <issue_label> : <label_occurence_in_closed_issues> } }
        """
        closers = {}
        for issue_id in issues_data.keys():
            issue_closer = issues_data[issue_id]["closed_by"]
            if issue_closer not in closers:
                closers[issue_closer] = {}
            for label in issues_data[issue_id]["labels"]:
                if label not in closers[issue_closer]:
                    closers[issue_closer][label] = 0
                closers[issue_closer][label] += 1

        for pr_id in pull_requests_data.keys():
            if pull_requests_data[pr_id]["merged_at"] is None:
                continue

            pr_author = pull_requests_data[pr_id]["created_by"]
            if pr_author not in closers:
                closers[pr_author] = {}

            for ref_issue in pull_requests_data[pr_id]["referenced_issues"]:
                for label in issues_data[ref_issue]["labels"]:
                    if label not in closers[pr_author]:
                        closers[pr_author][label] = 0
                    closers[pr_author][label] += 1

        return closers

    def pre_process_issues_closed_by_pr_size(
        self, issues_data: IssueSchema, pr_data: PullRequestSchema
    ) -> Dict[str, int]:
        """Analyse number of closed issues to every Pull Request size.

        :param issues_data:Dict:
        :param pr_data:Dict:
        :rtype: { <pr_size_label> : <number_of_closed_issues> }
        """
        issues = {}
        for pr_id in pr_data.keys():
            for issue_id in pr_data[pr_id]["referenced_issues"]:

                ttci = int(issues_data[issue_id]["closed_at"] - int(issues_data[issue_id]["created_at"]))
                size = pr_data[pr_id]["size"]

                if pr_data[pr_id][size] not in issues:
                    issues[size] = []
                issues[size].append(ttci)
        return issues
