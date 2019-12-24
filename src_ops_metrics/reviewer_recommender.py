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

from pathlib import Path
from collections import Counter

from visualization import retrieve_knowledge
from visualization import post_process_project_data, post_process_contributors_data

_LOGGER = logging.getLogger(__name__)

BOTS_NAMES = [
    "sesheta",
    "dependencies[bot]",
    "dependabot[bot]",
    ]


def convert_score2num(label: str) -> int:
    """Convert label string to numerical value."""
    if label == "XXL":
        return 1
    # lines_changes > 1000:
    #     return "size/XXL"
    elif label == "XL":
        return 0.7
    # elif lines_changes >= 500 and lines_changes <= 999:
    #     return "size/XL"
    elif label == "L":
        return 0.4
    # elif lines_changes >= 100 and lines_changes <= 499:
    #     return "size/L"
    elif label == "M":
        return 0.09
    # elif lines_changes >= 30 and lines_changes <= 99:
    #     return "size/M"
    elif label == "S":
        return 0.02
    # elif lines_changes >= 10 and lines_changes <= 29:
    #     return "size/S"
    elif label == "XS":
        return 0.01
    # elif lines_changes >= 0 and lines_changes <= 9:
    #     return "size/XS"
    else:
        _LOGGER.error("%s is not a recognized size" % label)


def convert_num2label(score: float) -> str:
    """Convert PR length to string label."""
    if score > 0.9:
        pull_request_size = "size/XXL"
        # lines_changes > 1000:
        #     return "size/XXL"
        assigned_score = 0.9

    elif score > 0.7 and score < 0.9:
        pull_request_size = "size/XL"
        # elif lines_changes >= 500 and lines_changes <= 999:
        #     return "size/XL"
        assigned_score = np.mean([0.7, 0.9])

    elif score >= 0.4 and score < 0.7:
        pull_request_size = "size/L"
        # elif lines_changes >= 100 and lines_changes <= 499:
        #     return "size/L"
        assigned_score = np.mean([0.4, 0.7])

    elif score >= 0.09 and score < 0.4:
        pull_request_size = "size/M"
        # elif lines_changes >= 30 and lines_changes <= 99:
        #     return "size/M"
        assigned_score = np.mean([0.09, 0.4])

    elif score >= 0.02 and score < 0.09:
        pull_request_size = "size/S"
        # elif lines_changes >= 10 and lines_changes <= 29:
        #     return "size/S"
        assigned_score = np.mean([0.02, 0.09])

    elif score >= 0.01 and score < 0.02:
        pull_request_size = "size/XS"
        # elif lines_changes >= 0 and lines_changes <= 9:
        #     return "size/XS"
        assigned_score = np.mean([0.01, 0.02])

    else:
        _LOGGER.error("%s cannot be mapped, it's out of range [%f, %f]" % (
            score,
            0.01,
            0.9
            )
            )

    return pull_request_size, assigned_score


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

    ttr_in_time , mttr_in_time, contributors = post_process_project_data(data=data)

    # Project statistics
    project_total_commits_number = sum([pr["commits_number"] for pr in data.values()])
    project_prs_number = len(data)
    project_prs_reviewed_number = len(mttr_in_time)
    project_mttr = mttr_in_time[-1][2]

    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    _LOGGER.info("{:40} --> {:^12} |{:^18} | {:^9} | {:^26} |".format(
        "Project",
        "N.PR Created",
        "N. Commits created",
        "N. PR rev",
        "Median Time to Review (MTTR)"))

    _LOGGER.info(
        "{:40} --> {:^12} |{:^18} | {:^9} | {:^26} |".format(
            project,
            project_prs_number,
            project_total_commits_number,
            project_prs_reviewed_number,
            str(timedelta(seconds=project_mttr))
        )
    )
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )

    authors = sorted(contributors)

    _LOGGER.info("")
    _LOGGER.info(
        "{:^20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^15} | {:^20} | {:^8} |".format(
            "Author reviews", "N. PR rev", "MTTR", "MLenPR", "N. commits c", "% Tot Commits c", "Time last rev", "Score"
        )
    )

    #         # Reviewer Analysis
    #         fig1, ax1 = plt.subplots()
    #         plt.gcf().autofmt_xdate()

    #         # Reviewer Analysis
    #         fig2, ax2 = plt.subplots()
    #         plt.gcf().autofmt_xdate()

    #         first_PR_approved_time = inputs_plots[0][3]
    #         now_time = datetime.now()

    #         bot_decision_score = []
    #         contributor_reviewer = []
    #         bot_contributor = []
    #         author_contribution_scores = {}
    #         author_reviewer_statistics = {}
    #         contributor_never_reviewed = []
    #         human_percentage = 0
    #         bot_percentage = 0

    # Authors (Contributors that reviewed and that didn't reviewed)
    contributors_reviews_data = post_process_contributors_data(data=data)

    for author in authors:
        _LOGGER.info(f"Analyzing contributor: {author}")

        author_total_commits_number = sum([
            pr["commits_number"]
            for pr in data.values()
            if pr["created_by"] == author])

        author_total_prs_number = 0
        for pr in data.values():
            if pr["created_by"] == author:
                author_total_prs_number += 1

        author_ttr_per_pr = [
            ttr_result[2]
            for ttr_result in ttr_in_time
            if ttr_result[3] == author
        ]

        # Check if the author reviewed any PR from another team member
        if author_ttr_per_pr:
            author_mttr = np.median(author_ttr_per_pr)
            author_prs_reviewed_number = len(author_ttr_per_pr)

            author_prs_size = [
                ttr_result[4]
                for ttr_result in ttr_in_time
                if ttr_result[3] == author
            ]

            # Encode Pull Request Size
            author_prs_size_encoded = [convert_score2num(label=pr_size) for pr_size in author_prs_size]
            author_pr_median_size, assigned_score = convert_num2label(
                score=np.median(author_prs_size_encoded)
                )
            print(author_pr_median_size, assigned_score)

    #                 PR_scores = []
    #                 for PR_labels in PRs_labels:
    #                     if PR_labels:
    #                         scores = []
    #                         for label in PR_labels:
    #                             scores.append(convert_label2num(label=label))
    #                         PR_scores.append(max(scores))
    #                     else:
    #                         pass

    #                 # Evaluate map of number of PR reviewer by reviewer per author of PR.
    #                 Number_PR_reviewed_for_author = {}
    #                 for reviewed in authors:
    #                     Number_PR_reviewed_for_author[reviewed] = (
    #                         len(
    #                             [
    #                                 pr
    #                                 for pr in data["results"].values()
    #                                 if pr["PR_approved"]
    #                                 and pr["PR_author"] == reviewed
    #                                 and pr["PR_approved_by"] == author
    #                             ]
    #                         )
    #                         / Number_PR_reviewed_author
    #                         * 100
    #                     )

    #                 if PR_scores:
    #                     if use_median:
    #                         mean_PR_length, relative_score = convert_score2label(mean_score=np.mean(PR_scores))
    #                     else:
    #                         mean_PR_length, relative_score = convert_score2label(mean_score=np.mean(PR_scores))
    #                 else:
    #                     mean_PR_length = "size/XS"
    #                     relative_score = 0.01
    #                     PR_scores = 0.01

    #                 ##############################################################################
    #                 ###################### MTTR in Time per Project ##############################
    #                 ##############################################################################
    #                 MTTR_author_time = []
    #                 pr_list_ttr = []
    #                 keys_list = sorted([int(k) for k in data["results"].keys()])
    #                 for key in keys_list:
    #                     pr = data["results"][str(key)]
    #                     if pr["PR_approved"] and pr["PR_approved_by"] == author:
    #                         dt_created = datetime.fromtimestamp(pr["PR_created"])
    #                         dt_approved = datetime.fromtimestamp(pr["PR_approved"])
    #                         pr_list_ttr.append((dt_approved - dt_created).total_seconds() / 3600)
    #                         if use_median:
    #                             MTTR_author_time.append(
    #                                 (
    #                                     datetime.fromtimestamp(pr["PR_created"]),
    #                                     np.median(pr_list_ttr),
    #                                     str(key),
    #                                 )
    #                             )
    #                         else:
    #                             MTTR_author_time.append(
    #                                 (
    #                                     datetime.fromtimestamp(pr["PR_created"]),
    #                                     np.mean(pr_list_ttr),
    #                                     str(key),
    #                                 )
    #                             )

    #                 # Sort results by PR ID
    #                 MTTR_author_time = sorted(MTTR_author_time, key=lambda x: int(x[2]))

    #                 PR_created_time_per_id = [el[0] for el in MTTR_author_time]
    #                 MTTR_time_per_id = [el[1] for el in MTTR_author_time]

    #                 if len(PR_created_time_per_id) != len(MTTR_author_time):
    #                     _LOGGER.warning(
    #                         f"PR_created_time_per_id {len(PR_created_time_per_id)}"
    #                         f"and MTTR_time_per_id {len(MTTR_time_per_id)} do not have the same length!"
    #                     )
    #                     raise Exception(
    #                         f"PR_created_time_per_id {len(PR_created_time_per_id)}"
    #                         f"and MTTR_time_per_id {len(MTTR_time_per_id)} do not have the same length!"
    #                     )

    #                 ax1.plot(PR_created_time_per_id, MTTR_time_per_id, "-o", label=author)

    #                 ##############################################################################

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
