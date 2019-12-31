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

from visualization import retrieve_knowledge
from visualization import post_process_project_data, post_process_contributors_data
from utils import convert_num2label, convert_score2num

_LOGGER = logging.getLogger(__name__)

BOTS_NAMES = [
    "sesheta",
    "dependencies[bot]",
    "dependabot[bot]",
    ]


def evaluate_reviewers(
    project: Tuple[str, str],
    number_reviewer: int = 2,
    detailed_statistics: bool = False,
    analyze_single_scores: bool = False,
    filter_contributors: bool = True,
    use_median: bool = False
    ):
    """Evaluate statistics from the knowledge of the bot and provide number of reviewers.

    :param number_reviewer: number of reviewers to select
    :param detailed_statistics: show detailed statistics
    :param analyze_single_scores: show each contribution that goes to the final score
    :param filter_contributors: filter contributor that never reviewed
    """
    knowledge_path = Path.cwd().joinpath("./src_ops_metrics/Bot_Knowledge")
    data = retrieve_knowledge(knowledge_path=knowledge_path, project=project)

    _, _, mtfr_in_time, mttr_in_time, contributors = post_process_project_data(data=data)

    # Project statistics
    project_commits_number = sum([pr["commits_number"] for pr in data.values()])
    project_prs_number = len(data)
    project_prs_reviewed_number = len(mttr_in_time)
    project_mtfr = mtfr_in_time[-1][2]
    project_mttr = mttr_in_time[-1][2]

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

    contributors = sorted(contributors)
    contributor_data = []

    # Contributors that reviewed and that didn't reviewed
    contributors_reviews_data = post_process_contributors_data(data=data)

    for contributor in contributors:

        _LOGGER.debug(f"Analyzing contributor: {contributor}")
        if contributor in contributors_reviews_data.keys():


            contributor_commits_number = sum([
                pr["commits_number"]
                for pr in data.values()
                if pr["created_by"] == contributor])

            contributor_prs_number = 0
            for pr in data.values():
                if pr["created_by"] == contributor:
                    contributor_prs_number += 1

            contributor_prs_reviewed_number = len(contributors_reviews_data[contributor]["reviews"])
            contributor_reviews_number = contributors_reviews_data[contributor]["number_reviews"]
            contributor_reviews_length = contributors_reviews_data[contributor]["median_review_length"]
            contributor_mtfr = contributors_reviews_data[contributor]["MTFR_in_time"][-1][2]
            contributor_mttr = contributors_reviews_data[contributor]["MTTR_in_time"][-1][2]


            contributor_data.append(
                    (
                        contributor,
                        contributor_prs_number,
                        contributor_prs_number/project_prs_number,
                        contributor_prs_reviewed_number,
                        contributor_prs_reviewed_number/project_prs_reviewed_number,
                        0,
                        contributor_reviews_number,
                        contributor_reviews_length,
                        str(timedelta(hours=contributor_mtfr)),
                        str(timedelta(hours=contributor_mttr)),
                        0,
                        contributor_commits_number,
                        contributor_commits_number/project_commits_number
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
                        contributor_commits_number/project_commits_number
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
            "Commits n.",
            "Commits %"
            ])
    print(contributors_data)

    #                 ##############################################################################
    #                 ################ TTR in Time per Author in Project ###########################
    #                 ##############################################################################

    #                 # Plot results
    #                 inputs_plots = []
    #                 for key, pr in data["results"].items():

    #                     if pr["PR_approved"] and pr["PR_approved_by"] == author:
    #                         # inputs_plots.append([key, pr["PR_TTR"]/(3600*24)])
    #                         dt_created = datetime.fromtimestamp(pr["PR_created"])
    #                         dt_approved = datetime.fromtimestamp(pr["PR_approved"])
    #                         inputs_plots.append(
    #                             [
    #                                 datetime.fromtimestamp(pr["PR_created"]),
    #                                 (dt_approved - dt_created).total_seconds() / 3600,
    #                                 key,
    #                                 datetime.fromtimestamp(pr["PR_approved"])
    #                             ]
    #                         )

    #                 # Sort results by PR ID
    #                 inputs_plots = sorted(inputs_plots, key=lambda x: int(x[2]))

    #                 PR_created_time_per_id = [el[0] for el in inputs_plots]
    #                 TTR_time_per_id = [el[1] for el in inputs_plots]

    #                 if len(PR_created_time_per_id) != len(TTR_time_per_id):
    #                     _LOGGER.warning(
    #                         f"PR_created_time_per_id {len(PR_created_time_per_id)}"
    #                         f"and TTR_time_per_id {len(TTR_time_per_id)} do not have the same length!"
    #                     )
    #                     raise Exception(
    #                         f"PR_created_time_per_id {len(PR_created_time_per_id)}"
    #                         f"and TTR_time_per_id {len(TTR_time_per_id)} do not have the same length!"
    #                     )

    #                 ax2.plot([el[0] for el in inputs_plots], [el[1] for el in inputs_plots], "-o", label=author)

    #                 ##############################################################################

    #                 ##############################################################################
    #                 ############################### Evaluate Score ###############################
    #                 ##############################################################################

    #                 # Relative scores contributions:
    #                 # 1: Number of PR reviewed respect to total number of PR reviewed by the team.
    #                 k1 = 1.1 # Weight factor of the contribution 1

    #                 # 2: Mean time to review a PR by reviewer respect to team repostiory MTTR.
    #                 k2 = 1 # Weight factor of the contribution 2

    #                 # 3: Mean length of PR respect to minimum value of PR length for a specific label.
    #                 k3 = 1.2 # Weight factor of the contribution 3

    #                 # 4: Number of commits respect to the total number of commits in the repository.
    #                 k4 = 1.4 # Weight factor of the contribution 4

    #                 # 5: Time since last review.
    #                 k5 = 1 # Weight factor of the contribution 5

    #                 last_review_author_time = inputs_plots[len(inputs_plots) - 1][3]
    #                 # TODO 6: Number of issue closed by a PR reviewed from an author respect to total number of issue closed.

    #                 final_score = (
    #                     k1 * (Number_PR_reviewed_author / Number_PR_reviewed)
    #                     * k2 *(MTTR / MTTR_author)
    #                     * k3 *(np.mean(PR_scores) / relative_score)
    #                     * k4 *(total_number_commits_author/ total_number_commits)
    #                     * k5 *(((last_review_author_time - first_PR_approved_time).total_seconds())/((now_time - first_PR_approved_time).total_seconds()))
    #                 )

    #                 contributor_reviewer.append([
    #                     author,
    #                     Number_PR_reviewed_author,
    #                     str(timedelta(seconds=MTTR_author)),
    #                     mean_PR_length,
    #                     total_number_commits_author,
    #                     total_number_commits_author/total_number_commits*100,
    #                     inputs_plots[len(inputs_plots) - 1][0].strftime("%m/%d/%Y, %H:%M:%S"),
    #                     final_score])

    #                 bot_decision_score.append((author, final_score))

    #                 author_reviewer_statistics[author] = Number_PR_reviewed_for_author

    #                 author_contribution_scores[author] = [
    #                         author,
    #                         k1 * (Number_PR_reviewed_author / Number_PR_reviewed),
    #                         k2 *(MTTR / MTTR_author),
    #                         k3 *(np.mean(PR_scores) / relative_score),
    #                         k4 *(total_number_commits_author/ total_number_commits),
    #                         "n/a",
    #                         k5 *(((last_review_author_time - first_PR_approved_time).total_seconds())/((now_time - first_PR_approved_time).total_seconds())),
    #                         final_score,
    #                 ]

    #                 human_percentage += (total_number_commits_author/ total_number_commits)*100

    #             else:
    #                 if author in BOTS_NAMES:
    #                     bot_contributor.append([
    #                         author, 
    #                         "0", 
    #                         "n/a", 
    #                         "n/a",
    #                         total_number_commits_author, 
    #                         total_number_commits_author/total_number_commits*100,
    #                         "n/a",
    #                         "n/a"])
    #                     bot_percentage += (total_number_commits_author/ total_number_commits)*100
    #                 else:
    #                     contributor_never_reviewed.append([
    #                         author, 
    #                         "0", 
    #                         "n/a", 
    #                         "n/a",
    #                         total_number_commits_author, 
    #                         total_number_commits_author/total_number_commits*100,
    #                         "n/a",
    #                         "n/a"])
    #                     human_percentage += (total_number_commits_author/ total_number_commits)*100

    #         # Sort by score
    #         contributor_reviewer = sorted(contributor_reviewer, key=lambda x: x[7], reverse=True)

    #         for contributor in contributor_reviewer:
    #             # Show statistics
    #             _LOGGER.info(
    #                 "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #             )
    #             _LOGGER.info(
    #                 "{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:15} | {:^8.4f} |".format(
    #                     contributor[0], 
    #                     contributor[1], 
    #                     contributor[2], 
    #                     contributor[3],
    #                     contributor[4], 
    #                     contributor[5],
    #                     contributor[6],
    #                     contributor[7]
    #                 )
    #             )

    #             if detailed_statistics:
    #                 _LOGGER.info(
    #                     "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #                 )
    #                 _LOGGER.info("{:20} -> % {}".format("Reviewed for", 'PR reviewed'))
    #                 for reviewed_for, percentage in author_reviewer_statistics[contributor[0]].items():
    #                     if reviewed_for != author and percentage > 0:
    #                         _LOGGER.info("{:20} -> {:.3f}%".format(reviewed_for, percentage))

    #             if analyze_single_scores:
    #                 _LOGGER.info(
    #                     "{:20} --> {:^9.4f} | {:^25.4f} | {:^9.4f} | {:^12.4f} | {:^14}  | {:^20.4f} | {:^8.4f} |".format(
    #                         author_contribution_scores[contributor[0]][0],
    #                         author_contribution_scores[contributor[0]][1],
    #                         author_contribution_scores[contributor[0]][2],
    #                         author_contribution_scores[contributor[0]][3],
    #                         author_contribution_scores[contributor[0]][4],
    #                         author_contribution_scores[contributor[0]][5],
    #                         author_contribution_scores[contributor[0]][6],
    #                         author_contribution_scores[contributor[0]][7],
    #                     )
    #                 )
    #         _LOGGER.info(
    #             "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #         )

    #         if not analyze_single_scores and not filter_contributors:
    #             for contributor in contributor_never_reviewed:
    #                 _LOGGER.info(
    #                     "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #                 )
    #                 _LOGGER.info("{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:^20} | {:^8} |".format(
    #                     contributor[0], 
    #                     contributor[1], 
    #                     contributor[2], 
    #                     contributor[3],
    #                     contributor[4], 
    #                     contributor[5],
    #                     contributor[6],
    #                     contributor[7]))
    #             _LOGGER.info(
    #                 "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #             )

    #             for contributor in bot_contributor:
    #                 _LOGGER.info(
    #                     "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #                 )
    #                 _LOGGER.info("{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:^20} | {:^8} |".format(
    #                     contributor[0], 
    #                     contributor[1], 
    #                     contributor[2], 
    #                     contributor[3],
    #                     contributor[4], 
    #                     contributor[5],
    #                     contributor[6],
    #                     contributor[7]))

    #         ##############################################################################
    #         ################ MTTR in Time per Author in Project ###########################
    #         ##############################################################################
    #         if use_median:
    #             ax1.set(
    #                 xlabel="PR created date",
    #                 ylabel="Median Time to Review (h)",
    #                 title=f"MTTR in Time per author per project: {project[1] + '/' + project[0]}",
    #             )
    #         else:
    #             ax1.set(
    #                 xlabel="PR created date",
    #                 ylabel="Mean Time to Review (h)",
    #                 title=f"MTTR in Time per author per project: {project[1] + '/' + project[0]}",
    #             )
    #         # Shrink current axis by 20%
    #         box = ax.get_position()
    #         ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    #         # Put a legend to the right of the current axis
    #         ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #         ax1.grid()
    #         author_results_mttr = knowledge_results_repo.joinpath(f"MTTR-in-time-{project[1] + '-' + project[0] + '-authors'}.png")
    #         fig1.savefig(author_results_mttr)
    #         ##############################################################################

    #         ##############################################################################
    #         ################ TTR in Time per Author in Project ###########################
    #         ##############################################################################
    #         ax2.set(
    #             xlabel="PR created date",
    #             ylabel="Time to Review (h)",
    #             title=f"TTR in Time per author per project: {project[1] + '/' + project[0]}",
    #         )
    #         ax2.legend()
    #         ax2.grid()
    #         author_results_ttr = knowledge_results_repo.joinpath(f"{project[1] + '-' + project[0] + '-authors'}.png")
    #         fig2.savefig(author_results_ttr)
    #         plt.close()
    #         ##############################################################################

    #     # Sort results by PR ID
    #     bot_decision_score_sorted = sorted(bot_decision_score, key=lambda x: (x[1]), reverse=True)
    #     _LOGGER.info(
    #         "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #     )
    #     requested_reviewers = number_reviewer
    #     while len(bot_decision_score_sorted) < requested_reviewers:
    #         _LOGGER.warning(f"Too many reviewers requested: {requested_reviewers}")
    #         requested_reviewers -= 1
    #     else:
    #         _LOGGER.info(f"Number of reviewers identified: {requested_reviewers}")
    #         _LOGGER.info(f"Reviewers: {[reviewer[0] for reviewer in bot_decision_score_sorted[:requested_reviewers]]}")

    #     _LOGGER.info(
    #         "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #     )
    #     _LOGGER.info("{:20} --> {:^5.3f}% |".format(
    #                     "Human % Tot commits", 
    #                     human_percentage)
    #                     )

    #     _LOGGER.info("{:20} --> {:^5.3f}% |".format(
    #                     "Bot % Tot commits", 
    #                     bot_percentage)
    #                     )


    # else:
    #     _LOGGER.info(
    #         "-----------------------------------------------------------------------------------------------------------------------------------------------"
    #     )
    #     _LOGGER.info(f"No previous knowledge from repo {project[1] + '/' + project[0]}")
    #     _LOGGER.info(f"To create knowledge, use create_bot_knowledge.py")
