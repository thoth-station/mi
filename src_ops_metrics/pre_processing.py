#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Francesco Murdaca
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

"""Pre-processing functions."""

import logging

import numpy as np

from typing import Tuple, Dict, Any, List
from pathlib import Path
from datetime import timedelta
from datetime import datetime

from create_bot_knowledge import load_previous_knowledge
from utils import convert_num2label, convert_score2num


_LOGGER = logging.getLogger(__name__)


def retrieve_knowledge(knowledge_path: Path, project: str) -> Dict[str, Any]:
    """Retrieve knowledge collected for a project."""
    project_knowledge_path = knowledge_path.joinpath("./" + f"{project}")
    pulls_data_path = project_knowledge_path.joinpath("./pull_requests.json")

    return load_previous_knowledge(project, pulls_data_path, "PullRequest")


def pre_process_project_data(data: Dict[str, Any]):
    """Pre process of data for a given project repository.

    Data example with 1 PR:

    {
        "37": {
            "size": null,
            "labels": [],
            "created_by": "pacospace",
            "created_at": 1576170840.0,
            "closed_at": 1576171248.0,
            "closed_by": "fridex",
            "time_to_close": 408.0,
            "merged_at": 1576171248.0,
            "commits_number": 1,
            "referenced_issues": [],
            "interactions": {}, 
            "reviews": {
                "331430111": {"author": "fridex", "words_count": 2, "submitted_at": 1576171243.0, "state": "APPROVED"}
                },
                "requested_reviewers": []
                }
            }
    """

    pr_ids = sorted([int(k) for k in data.keys()])

    tfr_per_pr = []                     # Time to First Review (TTFR) [hr]
    ttr_per_pr = []                     # Time to Review (TTR) [hr]

    mtfr_in_time = []                   # Median TTFR [hr]
    mttr_in_time = []                   # Mean TTR [hr]

    tfr_in_time = []                    # TTFR in time [hr]
    ttr_in_time = []                    # TTR in time [hr]

    contributors = []

    project_prs_size_encoded = []       # Pull Request length

    for pr_id in pr_ids:
        pr = data[str(pr_id)]

        if pr["reviews"] and pr["size"]:
            dt_created = datetime.fromtimestamp(pr["created_at"])

            dt_first_review = datetime.fromtimestamp([r for r in pr["reviews"].values()][0]['submitted_at'])

            tfr_per_pr.append((dt_first_review - dt_created).total_seconds() / 3600)

            # Consider all approved reviews
            pr_approved_dt = [
                datetime.fromtimestamp(review["submitted_at"])
                for review in pr["reviews"].values()
                if review["state"] == "APPROVED"
            ]

            if pr_approved_dt:
                # Take maximum to consider last approved if more than one contributor has to approve
                dt_approved = max(pr_approved_dt)

                ttr_per_pr.append((dt_approved - dt_created).total_seconds() / 3600)

                ttr_in_time.append(
                    (
                        dt_created,
                        pr_id,
                        (dt_approved - dt_created).total_seconds() / 3600,
                        pr["size"])
                )
                mttr_in_time.append((dt_created, pr_id, np.median(ttr_per_pr)))

            else:
                dt_merged = datetime.fromtimestamp(pr["merged_at"])
                ttr_per_pr.append((dt_merged - dt_created).total_seconds() / 3600)

                ttr_in_time.append(
                    (
                        dt_created,
                        pr_id,
                        (dt_merged - dt_created).total_seconds() / 3600,
                        pr["size"])
                )
                mttr_in_time.append((dt_created, pr_id, np.median(ttr_per_pr)))

            tfr_in_time.append(
                (
                    dt_created,
                    pr_id,
                    (dt_first_review - dt_created).total_seconds() / 3600,
                    pr["size"])
            )

            mtfr_in_time.append((dt_created, pr_id, np.median(tfr_per_pr)))

            project_prs_size_encoded.append(convert_score2num(label=pr["size"]))

        if pr["created_by"] not in contributors:
            contributors.append(pr["created_by"])

    project_reviews_data = {}
    project_reviews_data["TFR_in_time"] = tfr_in_time
    project_reviews_data["TTR_in_time"] = ttr_in_time
    project_reviews_data["MTFR_in_time"] = mtfr_in_time
    project_reviews_data["MTTR_in_time"] = mttr_in_time
    project_reviews_data["contributors"] = contributors

    # Encode Pull Request sizes for the contributor
    project_pr_median_size, project_length_score = convert_num2label(
        score=np.median(project_prs_size_encoded)
        )
    project_reviews_data["median_pr_length"] = project_pr_median_size
    project_reviews_data["median_pr_length_score"] = project_length_score

    return project_reviews_data


def pre_process_contributors_data(data: Dict[str, Any]):
    """Pre process of data for contributors in a project repository."""
    pr_ids = sorted([int(k) for k in data.keys()])

    contributors_reviews_data = {}

    tfr_per_pr = {}     # Time to First Review (TTFR) [hr]
    ttr_per_pr = {}     # Time to Review (TTR) [hr]

    pr_length = {}      # Pull Request length per Reviewer

    mtfr_in_time = {}   # Median TTFR [hr]
    mttr_in_time = {}   # Mean TTR [hr]

    tfr_in_time = {}    # TTFR in time [hr]
    ttr_in_time = {}    # TTR in time [hr]

    for pr_id in pr_ids:
        pr = data[str(pr_id)]
        if pr["reviews"] and pr["size"]:

            dt_created = datetime.fromtimestamp(pr["created_at"])

            review_info_per_reviewer = {}

            for review in pr["reviews"].values():
                # Check reviews and discard comment of the author of the PR
                if review["author"] != pr["created_by"]:
                    if review["author"] not in contributors_reviews_data.keys():
                        contributors_reviews_data[review["author"]] = {}
                        contributors_reviews_data[review["author"]]["reviews"] = {}
                        if pr_id not in contributors_reviews_data[review["author"]]["reviews"].keys():
                            contributors_reviews_data[review["author"]]["reviews"][pr_id] = [{
                                "words_count": review["words_count"],
                                "submitted_at": review["submitted_at"],
                                "state": review["state"]
                            }
                            ]
                        else:
                            contributors_reviews_data[review["author"]]["reviews"][pr_id].append({
                                "words_count": review["words_count"],
                                "submitted_at": review["submitted_at"],
                                "state": review["state"]
                            }
                            )
                    else:
                        if pr_id not in contributors_reviews_data[review["author"]]["reviews"].keys():
                            contributors_reviews_data[review["author"]]["reviews"][pr_id] = [{
                                "words_count": review["words_count"],
                                "submitted_at": review["submitted_at"],
                                "state": review["state"]
                            }
                            ]
                        else:
                            contributors_reviews_data[review["author"]]["reviews"][pr_id].append({
                                "words_count": review["words_count"],
                                "submitted_at": review["submitted_at"],
                                "state": review["state"]
                            }
                            )

                    if review["author"] not in review_info_per_reviewer.keys():
                        review_info_per_reviewer[review["author"]] = [review["submitted_at"]]
                    else:
                        review_info_per_reviewer[review["author"]].append(review["submitted_at"])

            for reviewer, reviewer_info in review_info_per_reviewer.items():
                dt_first_review = datetime.fromtimestamp(reviewer_info[0])

                if reviewer not in tfr_per_pr.keys():
                    tfr_per_pr[reviewer] = [(dt_first_review - dt_created).total_seconds() / 3600]
                    tfr_in_time[reviewer] = [
                        (
                            dt_created,
                            pr_id,
                            (dt_first_review - dt_created).total_seconds() / 3600,
                            pr["size"])
                ]
                else:
                    tfr_per_pr[reviewer].append((dt_first_review - dt_created).total_seconds() / 3600)
                    tfr_in_time[reviewer].append(
                        (
                            dt_created,
                            pr_id,
                            (dt_first_review - dt_created).total_seconds() / 3600,
                            pr["size"])
                    )

                dt_approved = [
                    datetime.fromtimestamp(review["submitted_at"])
                    for review in pr["reviews"].values()
                    if review["state"] == "APPROVED" and review["author"] == reviewer
                ]

                # if not dt_approved: 
                #     dt_approved = datetime.fromtimestamp(pr["merged_at"])

                if dt_approved:
                    if reviewer not in ttr_per_pr.keys():
                        ttr_per_pr[reviewer] = [(dt_approved[0] - dt_created).total_seconds() / 3600]
                        ttr_in_time[reviewer] = [
                            (
                                dt_created,
                                pr_id,
                                (dt_approved[0] - dt_created).total_seconds() / 3600,
                                pr["size"])
                    ]
                    else:
                        ttr_per_pr[reviewer].append((dt_approved[0] - dt_created).total_seconds() / 3600)
                        ttr_in_time[reviewer].append(
                            (
                                dt_created,
                                pr_id,
                                (dt_approved[0] - dt_created).total_seconds() / 3600,
                                pr["size"])
                        )

                if reviewer not in mtfr_in_time.keys():
                    mtfr_in_time[reviewer] = [(dt_created, pr_id, np.median(tfr_per_pr[reviewer]))]
                    mttr_in_time[reviewer] = [(dt_created, pr_id, np.median(ttr_per_pr[reviewer]))]
                else:
                    mtfr_in_time[reviewer].append((dt_created, pr_id, np.median(tfr_per_pr[reviewer])))
                    mttr_in_time[reviewer].append((dt_created, pr_id, np.median(ttr_per_pr[reviewer])))

                if reviewer not in pr_length.keys():
                    pr_length[reviewer] = [pr["size"]]
                else:
                    pr_length[reviewer] = pr["size"]



    for reviewer in contributors_reviews_data.keys():
        number_reviews = 0
        reviews_length = []
        for reviews in contributors_reviews_data[reviewer]["reviews"].values():
            number_reviews += len(reviews)
            review_words = 0
            for review in reviews:
                review_words += review["words_count"]

            reviews_length.append(review_words)

        contributors_reviews_data[reviewer]["number_reviews"] = number_reviews
        contributors_reviews_data[reviewer]["median_review_length"] = np.median(reviews_length)

        # Encode Pull Request sizes for the contributor
        contributor_prs_size_encoded = [convert_score2num(label=pr_size) for pr_size in pr_length[reviewer]]
        contributor_pr_median_size, contributor_relative_score = convert_num2label(
            score=np.median(contributor_prs_size_encoded)
            )
        contributors_reviews_data[reviewer]["median_pr_length"] = contributor_pr_median_size
        contributors_reviews_data[reviewer]["median_pr_length_score"] = contributor_relative_score

        contributors_reviews_data[reviewer]["MTFR_in_time"] = mtfr_in_time[reviewer]
        contributors_reviews_data[reviewer]["MTTR_in_time"] = mttr_in_time[reviewer]

    return contributors_reviews_data
