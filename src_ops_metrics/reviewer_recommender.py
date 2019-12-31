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

"""Reviewer Reccomendation."""

import logging
import os
import json
import time
from datetime import timedelta
from datetime import datetime

from typing import Tuple
import numpy as np
import pandas as pd

from pathlib import Path
from collections import Counter

from pre_processing import retrieve_knowledge
from pre_processing import pre_process_project_data, pre_process_contributors_data
from utils import convert_num2label, convert_score2num


_LOGGER = logging.getLogger(__name__)

BOTS_NAMES = [
    "sesheta",
    "dependencies[bot]",
    "dependabot[bot]",
    ]


def evaluate_contributor_score(
    contribution_1: float,
    contribution_2: float,
    contribution_3: float,
    contribution_4: float,
    contribution_5: float
) -> float:
    """Evaluate contributor score.

    Contributions:
    1: Number of PR reviewed respect to total number of PR reviewed by the team.

    2: Mean time to review a PR by reviewer respect to team repostiory MTTR.

    3: Mean length of PR respect to minimum value of PR length for a specific label.

    4: Number of commits respect to the total number of commits in the repository.

    5: Time since last review.

    TODO 6: Number of issue closed by a PR reviewed from an author respect to total number of issue closed.
    """
    k1 = 1.1    # Weight factor of contribution 1
    k2 = 1      # Weight factor of contribution 2
    k3 = 1.2    # Weight factor of contribution 3
    k4 = 1.4    # Weight factor of contribution 4
    k5 = 1      # Weight factor of contribution 5

    final_score = (
        k1 * contribution_1
        * k2 * contribution_2
        * k3 * contribution_3
        * k4 * contribution_4
        * k5 * contribution_5
    )

    return final_score


def evaluate_reviewers(
    project: Tuple[str, str],
    number_reviewer: int = 2,
    detailed_statistics: bool = False,
    analyze_single_scores: bool = False,
    filter_contributors: bool = True,
    ):
    """Evaluate statistics from the knowledge of the bot and provide number of reviewers.

    :param number_reviewer: number of reviewers to select
    :param detailed_statistics: show detailed statistics
    :param analyze_single_scores: show each contribution that goes to the final score
    :param filter_contributors: filter contributor that never reviewed
    """
    knowledge_path = Path.cwd().joinpath("./src_ops_metrics/Bot_Knowledge")
    data = retrieve_knowledge(knowledge_path=knowledge_path, project=project)

    now_time = datetime.now()

    projects_reviews_data = pre_process_project_data(data=data)
    
    # Project statistics
    project_commits_number = sum([pr["commits_number"] for pr in data.values()])
    project_prs_number = len(data)
    project_prs_reviewed_number = len(projects_reviews_data["MTTR_in_time"])
    project_mtfr = projects_reviews_data["MTFR_in_time"][-1][2]
    project_mttr = projects_reviews_data["MTTR_in_time"][-1][2]
    project_reviews_length_score = projects_reviews_data["median_pr_length_score"]

    project_data = pd.DataFrame(
        [
            (
                project,
                project_prs_number,
                project_commits_number,
                project_prs_reviewed_number,
                str(timedelta(hours=project_mtfr)),
                str(timedelta(hours=project_mttr))
            )
        ], columns=[
            "Repository",
            "PullRequest n.",
            "Commits n.",
            "PullRequestRev n.",
            "MTTFR", # Median Time to First Review 
            "MTTR" # Median Time to Review
            ])
    _LOGGER.info(
        "-------------------------------------------------------------------------------"
    )
    print(project_data)
    _LOGGER.info(
        "-------------------------------------------------------------------------------"
    )

    contributors = sorted(projects_reviews_data["contributors"])
    contributor_data = []
    scores_data = []

    # Contributors that reviewed and that didn't reviewed
    contributors_reviews_data = pre_process_contributors_data(data=data)

    for contributor in contributors:

        _LOGGER.debug(f"Analyzing contributor: {contributor}")
        if contributor in contributors_reviews_data.keys() and contributor not in BOTS_NAMES:

            contributor_commits_number = sum([
                pr["commits_number"]
                for pr in data.values()
                if pr["created_by"] == contributor])

            contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    contributor_prs_number += 1

            contributor_prs_reviewed_number = len(contributors_reviews_data[contributor]["reviews"])
            contributor_median_pr_length = contributors_reviews_data[contributor]["median_pr_length"]
            contributor_reviews_number = contributors_reviews_data[contributor]["number_reviews"]
            contributor_reviews_length = contributors_reviews_data[contributor]["median_review_length"]
            contributor_reviews_length_score = contributors_reviews_data[contributor]["median_pr_length_score"]
            contributor_mtfr = contributors_reviews_data[contributor]["MTFR_in_time"][-1][2]
            contributor_mttr = contributors_reviews_data[contributor]["MTTR_in_time"][-1][2]

            contributor_time_reviews = []
            for reviews in contributors_reviews_data[contributor]["reviews"].values():
                for review in reviews:
                    contributor_time_reviews.append(review["submitted_at"])
            last_review_dt = max(contributor_time_reviews)

            contributor_time_last_review = now_time - datetime.fromtimestamp(last_review_dt)

            contributor_data.append(
                    (
                        contributor,
                        contributor_prs_number,
                        contributor_prs_number/project_prs_number,
                        contributor_prs_reviewed_number,
                        contributor_prs_reviewed_number/project_prs_reviewed_number,
                        contributor_median_pr_length,
                        contributor_reviews_number,
                        contributor_reviews_length,
                        str(timedelta(hours=contributor_mtfr)),
                        str(timedelta(hours=contributor_mttr)),
                        contributor_time_last_review,
                        contributor_commits_number,
                        contributor_commits_number/project_commits_number,
                        False
                    )
                )

            final_score = evaluate_contributor_score(
                contribution_1=contributor_prs_number/project_prs_number,
                contribution_2=timedelta(hours=project_mttr)/timedelta(hours=contributor_mttr),
                contribution_3=contributor_reviews_length_score/project_reviews_length_score,
                contribution_4=contributor_commits_number/project_commits_number,
                contribution_5=1
            )

    #     * k5 *(((last_review_author_time - first_PR_approved_time).total_seconds())/((now_time - first_PR_approved_time).total_seconds()))

            scores_data.append(
                (
                    contributor,
                    contributor_prs_number/project_prs_number,
                    timedelta(hours=project_mttr)/timedelta(hours=contributor_mttr),
                    contributor_reviews_length_score/project_reviews_length_score,
                    contributor_commits_number/project_commits_number,
                    1,
                    final_score
                )
            )

        elif contributor in BOTS_NAMES:

            bot_contributor_commits_number = sum([
                pr["commits_number"]
                for pr in data.values()
                if pr["created_by"] == contributor])

            bot_contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    bot_contributor_prs_number += 1

            contributor_data.append(
                    (
                        contributor,
                        bot_contributor_prs_number,
                        bot_contributor_prs_number/project_prs_number,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        bot_contributor_commits_number,
                        contributor_commits_number/project_commits_number,
                        True
                    )
                )

        else:

            contributor_commits_number = sum([
                pr["commits_number"]
                for pr in data.values()
                if pr["created_by"] == contributor])

            contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    contributor_prs_number += 1

            contributor_data.append(
                    (
                        contributor,
                        contributor_prs_number,
                        contributor_prs_number/project_prs_number,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        contributor_commits_number,
                        contributor_commits_number/project_commits_number,
                        False
                    )
                )

    contributors_data = pd.DataFrame(
        contributor_data, columns=[
            "Contributor",
            "PR n.",        # Pull Request number
            "PR %",         # Pull Request percentage respect to total
            "PRRev n.",     # Pull Request Reviewed number
            "PRRev %",      # Pull Request Reviewed percentage respect to total
            "MPRLen",       # Median Pull Request Reviewed Length
            "Rev n.",       # Reviews number
            "MRL",          # Median Review Length (Word count based)
            "MTTFR",        # Median Time to First Review 
            "MTTR",         # Median Time to Review
            "TLR",          # Time Last Review [hr]
            "Comm n.",      # Commits number
            "Comm %",       # Commits percentage
            "Bot"           # Is a bot?
            ])
    print()
    print(contributors_data)

    contributors_score_data = pd.DataFrame(
        scores_data, columns=[
            "Contributor",
            "C1",           # Contribution 1
            "C2",           # Contribution 2
            "C3",           # Contribution 3
            "C4",           # Contribution 4
            "C5",           # Contribution 5
            "Score"         # Contributor Final Score
            ])

    print()
    sorted_reviewers = contributors_score_data.sort_values(by=['Score'], ascending=False)
    print(sorted_reviewers)

    print()
    _LOGGER.info(f"Number of reviewers requested: {number_reviewer}")
    if 
    _LOGGER.info(
            f"Reviewers: {sorted_reviewers['Contributor'].head(number_reviewer).values}")
