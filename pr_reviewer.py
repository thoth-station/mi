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

"""Evaluate statistics on Bot Knowledge."""

import logging
import os
import time
from datetime import timedelta
from datetime import datetime
import numpy as np
import json
from typing import Tuple
import matplotlib
import matplotlib.pyplot as plt

from create_bot_knowledge import PROJECTS
from pathlib import Path
from collections import Counter

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BOTS_NAMES = [
    "sesheta",
    "dependencies[bot]",
    "dependabot[bot]",
]


def convert_label2num(label: str) -> int:
    """Conver label string in numerical value."""
    if label == "size/XXL":
        return 1
    # lines_changes > 1000:
    #     return "size/XXL"
    elif label == "size/XL":
        return 0.7
    # elif lines_changes >= 500 and lines_changes <= 999:
    #     return "size/XL"
    elif label == "size/L":
        return 0.4
    # elif lines_changes >= 100 and lines_changes <= 499:
    #     return "size/L"
    elif label == "size/M":
        return 0.09
    # elif lines_changes >= 30 and lines_changes <= 99:
    #     return "size/M"
    elif label == "size/S":
        return 0.02
    # elif lines_changes >= 10 and lines_changes <= 29:
    #     return "size/S"
    elif label == "size/XS":
        return 0.01
    # elif lines_changes >= 0 and lines_changes <= 9:
    #     return "size/XS"
    else:
        # Give the minimum score ("size/XS")
        return 0.01


def convert_score2label(mean_score: float) -> str:
    """Convert Mean PR score to string label."""
    if mean_score > 0.9:
        mean_PR_length = "size/XXL"
        # lines_changes > 1000:
        #     return "size/XXL"
        relative_score = 0.9

    elif mean_score > 0.7 and mean_score < 0.9:
        mean_PR_length = "size/XL"
        # elif lines_changes >= 500 and lines_changes <= 999:
        #     return "size/XL"
        relative_score = 0.7

    elif mean_score >= 0.4 and mean_score < 0.7:
        mean_PR_length = "size/L"
        # elif lines_changes >= 100 and lines_changes <= 499:
        #     return "size/L"
        relative_score = 0.4

    elif mean_score >= 0.09 and mean_score < 0.4:
        mean_PR_length = "size/M"
        # elif lines_changes >= 30 and lines_changes <= 99:
        #     return "size/M"
        relative_score = 0.09

    elif mean_score >= 0.02 and mean_score < 0.09:
        mean_PR_length = "size/S"
        # elif lines_changes >= 10 and lines_changes <= 29:
        #     return "size/S"
        relative_score = 0.02

    elif mean_score >= 0.01 and mean_score < 0.02:
        mean_PR_length = "size/XS"
        # elif lines_changes >= 0 and lines_changes <= 9:
        #     return "size/XS"
        relative_score = 0.01
    else:
        mean_PR_length = "size/XS"
        relative_score = 0.01

    return mean_PR_length, relative_score


def project_ttr_author_violin_plots(project_data):

    results = project_data['results']
    reviewers = {pr['PR_approved_by']
                 for pr in results.values() if pr['PR_approved_by'] is not None}

    ttrs = {key: [] for key in reviewers}
    for pr_review in results.values():
        if pr_review['PR_approved_by'] is None:
            continue

        ttrs[pr_review['PR_approved_by']].append(pr_review['PR_TTR'])

    fig, ax = plt.subplots(figsize=(5, 3))

    author_ttrs = [(author, ttrs[author]) for author in ttrs.keys()]
    author_ttrs = sorted(author_ttrs, key=lambda author: sum(author[1]))

    vplots = ax.violinplot([pair[1] for pair in author_ttrs],
                           showmedians=True,
                           showextrema=True)

    set_color_scheme(vplots)
    set_xlabels(ax, [pair[0] for pair in author_ttrs])

    plt.show()


def set_color_scheme(vplots):
    for plot in vplots['bodies']:
        plot.set_facecolor('#D43F3A')
        plot.set_edgecolor('black')
        plot.set_alpha(1)


def set_xlabels(ax, labels):
    ax.set_xlabel('Authors')
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels)


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
    current_path = Path().cwd()
    source_knowledge_repo = current_path.joinpath("./Bot_Knowledge")
    source_knowledge_file = source_knowledge_repo.joinpath(
        f'{project[1] + "-" + project[0]}.json')

    if not source_knowledge_file.exists():
        _LOGGER.info(
            "-----------------------------------------------------------------------------------------------------------------------------------------------"
        )
        _LOGGER.info(
            f"No previous knowledge from repo {project[1] + '/' + project[0]}")
        _LOGGER.info(f"To create knowledge, use create_bot_knowledge.py")
        return

    knowledge_results_repo = current_path.joinpath("./Knowledge_Results")

    if not knowledge_results_repo.exists():
        os.mkdir(knowledge_results_repo)

    with open(source_knowledge_file, "r") as fp:
        data = json.load(fp)

    project_ttr_author_violin_plots(data)

    # Team Analysis
    ##############################################################################
    ###################### MTTR in Time per Project ##############################
    ##############################################################################

    MTTR_time = []
    pr_list_ttr = []
    keys_list = sorted([int(k) for k in data["results"].keys()])
    for pr_nums, key in enumerate(keys_list):
        pr = data["results"][str(key)]
        if pr["PR_approved"]:
            dt_created = datetime.fromtimestamp(pr["PR_created"])
            dt_approved = datetime.fromtimestamp(pr["PR_approved"])
            pr_list_ttr.append(
                (dt_approved - dt_created).total_seconds() / 3600)

            MTTR_time.append(
                (
                    datetime.fromtimestamp(pr["PR_created"]),
                    np.median(pr_list_ttr) if use_median else np.mean(
                        pr_list_ttr),
                    str(key),
                )
            )

    # Plot results
    fig, ax = plt.subplots()

    # Sort results by PR ID
    MTTR_time = sorted(MTTR_time, key=lambda x: int(x[2]))

    PR_created_time_per_id = [el[0] for el in MTTR_time]
    MTTR_time_per_id = [el[1] for el in MTTR_time]

    if len(PR_created_time_per_id) != len(MTTR_time):
        raise Exception(
            f"PR_created_time_per_id {len(PR_created_time_per_id)}"
            f"and MTTR_time_per_id {len(MTTR_time_per_id)} do not have the same length!"
        )

    ax.plot(PR_created_time_per_id, MTTR_time_per_id, "-ro")
    plt.gcf().autofmt_xdate()

    ax.set(
        xlabel="PR created date",
        ylabel="Median Time to Review (h)" if use_median else "Mean Time to Review (h)",
        title=f"MTTR in Time per project: {project[1] + '/' + project[0]}",
    )
    ax.grid()

    team_results = knowledge_results_repo.joinpath(
        f"MTTR-in-time-{project[1] + '-' + project[0]}.png")
    fig.savefig(team_results)
    plt.close()

    ##############################################################################
    values = [pr["PR_TTR"]
              for pr in data["results"].values() if pr["PR_approved"]]
    MTTR = np.median(values) if use_median else np.mean(values)

    total_number_commits = sum([pr["PR_commits_number"]
                                for pr in data["results"].values()])
    total_number_PR = len([pr for pr in data["results"].values()])
    Number_PR_reviewed = len(
        [pr for pr in data["results"].values() if pr["PR_approved"]])
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    if use_median:
        _LOGGER.info("{:40} --> {:^12} |{:^18} | {:^9} | {:^26} |".format(
            "Project",
            "N.PR Created",
            "N. Commits created",
            "N. PR rev",
            "Median Time to Review (MTTR)"))
    else:
        _LOGGER.info("{:40} --> {:^12} |{:^18} | {:^9} | {:^26} |".format(
            "Project",
            "N.PR Created",
            "N. Commits created",
            "N. PR rev",
            "Mean Time to Review (MTTR)"))

    _LOGGER.info(
        "{:40} --> {:^12} |{:^18} | {:^9} | {:^26} |".format(
            project[1] + "/" + project[0], total_number_PR, total_number_commits, Number_PR_reviewed, str(
                timedelta(seconds=MTTR))
        )
    )
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    # PR Authors (who opened the PR?)
    authors = []
    for pr in data["results"].values():
        if pr["PR_author"] not in authors:
            authors.append(pr["PR_author"])
    authors = sorted(authors)

    _LOGGER.info("")
    _LOGGER.info(
        "{:^20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^15} | {:^20} | {:^8} |".format(
            "Author reviews", "N. PR rev", "MTTR", "MLenPR", "N. commits c", "% Tot Commits c", "Time last rev", "Score"
        )
    )

    ##############################################################################
    ###################### TTR in Time per Project ###############################
    ##############################################################################
    # Plot results
    fig, ax = plt.subplots()
    inputs_plots = []

    for key, pr in data["results"].items():

        if pr["PR_approved"]:
            dt_created = datetime.fromtimestamp(pr["PR_created"])
            dt_approved = datetime.fromtimestamp(pr["PR_approved"])
            _LOGGER.debug(dt_approved)
            _LOGGER.debug(dt_created)
            _LOGGER.debug((dt_approved - dt_created))
            _LOGGER.debug((dt_approved - dt_created).total_seconds() / 3600)
            _LOGGER.debug(timedelta(seconds=pr["PR_TTR"]))
            inputs_plots.append(
                [
                    datetime.fromtimestamp(pr["PR_created"]),
                    (dt_approved - dt_created).total_seconds() / 3600,
                    key,
                    datetime.fromtimestamp(pr["PR_approved"])
                ]
            )

    # Sort results by PR ID
    inputs_plots = sorted(inputs_plots, key=lambda x: int(x[2]))

    # Create Plot
    PR_created_time_per_id = [el[0] for el in inputs_plots]
    PR_TTR_per_id = [el[1] for el in inputs_plots]

    if len(PR_created_time_per_id) != len(PR_TTR_per_id):
        _LOGGER.warning(
            f"PR_created_time_per_id {len(PR_created_time_per_id)}"
            f"and PR_TTR_per_id {len(PR_TTR_per_id)} do not have the same length!"
        )
        raise Exception(
            f"PR_created_time_per_id {len(PR_created_time_per_id)}"
            f"and PR_TTR_per_id {len(PR_TTR_per_id)} do not have the same length!"
        )

    ax.plot(PR_created_time_per_id, PR_TTR_per_id, "-ko")
    plt.gcf().autofmt_xdate()

    ax.set(
        xlabel="PR created date",
        ylabel="Time to Review (h)",
        title=f"TTR in Time per project: {project[1] + '/' + project[0]}",
    )
    ax.grid()

    team_results = knowledge_results_repo.joinpath(
        f"{project[1] + '-' + project[0]}.png")
    fig.savefig(team_results)
    plt.close()

    ##############################################################################

    # Reviewer Analysis
    fig1, ax1 = plt.subplots()
    plt.gcf().autofmt_xdate()

    # Reviewer Analysis
    fig2, ax2 = plt.subplots()
    plt.gcf().autofmt_xdate()

    first_PR_approved_time = inputs_plots[0][3]
    now_time = datetime.now()

    bot_decision_score = []
    contributor_reviewer = []
    bot_contributor = []
    author_contribution_scores = {}
    author_reviewer_statistics = {}
    contributor_never_reviewed = []
    human_percentage = 0
    bot_percentage = 0

    # Authors (Contributors that reviewed and that didn't reviewed)
    for author in authors:
        _LOGGER.debug(f"Analyzing contributor {author}")
        total_number_commits_author = sum(
            [pr["PR_commits_number"] for pr in data["results"].values() if pr["PR_author"] == author])
        TTR_PR_reviewed_by_author = [
            pr["PR_TTR"]
            for pr in data["results"].values()
            if pr["PR_approved"] and pr["PR_approved_by"] == author
        ]

        # Check if the author reviewed any PR from another team member
        if TTR_PR_reviewed_by_author:
            if use_median:
                MTTR_author = np.median(TTR_PR_reviewed_by_author)
            else:
                MTTR_author = np.mean(TTR_PR_reviewed_by_author)

            Number_PR_reviewed_author = len(TTR_PR_reviewed_by_author)
            PRs_labels = [
                pr["PR_labels"]
                for pr in data["results"].values()
                if pr["PR_approved"] and pr["PR_approved_by"] == author
            ]

            PR_scores = []
            for PR_labels in PRs_labels:
                if PR_labels:
                    scores = []
                    for label in PR_labels:
                        scores.append(convert_label2num(label=label))
                    PR_scores.append(max(scores))
                else:
                    pass

            # Evaluate map of number of PR reviewer by reviewer per author of PR.
            Number_PR_reviewed_for_author = {}
            for reviewed in authors:
                Number_PR_reviewed_for_author[reviewed] = (
                    len(
                        [
                            pr
                            for pr in data["results"].values()
                            if pr["PR_approved"]
                            and pr["PR_author"] == reviewed
                            and pr["PR_approved_by"] == author
                        ]
                    )
                    / Number_PR_reviewed_author
                    * 100
                )

            if PR_scores:
                if use_median:
                    mean_PR_length, relative_score = convert_score2label(
                        mean_score=np.mean(PR_scores))
                else:
                    mean_PR_length, relative_score = convert_score2label(
                        mean_score=np.mean(PR_scores))
            else:
                mean_PR_length = "size/XS"
                relative_score = 0.01
                PR_scores = 0.01

            ##############################################################################
            ###################### MTTR in Time per Project ##############################
            ##############################################################################
            MTTR_author_time = []
            pr_list_ttr = []
            keys_list = sorted([int(k) for k in data["results"].keys()])
            for key in keys_list:
                pr = data["results"][str(key)]
                if pr["PR_approved"] and pr["PR_approved_by"] == author:
                    dt_created = datetime.fromtimestamp(pr["PR_created"])
                    dt_approved = datetime.fromtimestamp(pr["PR_approved"])
                    pr_list_ttr.append(
                        (dt_approved - dt_created).total_seconds() / 3600)
                    if use_median:
                        MTTR_author_time.append(
                            (
                                datetime.fromtimestamp(pr["PR_created"]),
                                np.median(pr_list_ttr),
                                str(key),
                            )
                        )
                    else:
                        MTTR_author_time.append(
                            (
                                datetime.fromtimestamp(pr["PR_created"]),
                                np.mean(pr_list_ttr),
                                str(key),
                            )
                        )

            # Sort results by PR ID
            MTTR_author_time = sorted(
                MTTR_author_time, key=lambda x: int(x[2]))

            PR_created_time_per_id = [el[0] for el in MTTR_author_time]
            MTTR_time_per_id = [el[1] for el in MTTR_author_time]

            if len(PR_created_time_per_id) != len(MTTR_author_time):
                _LOGGER.warning(
                    f"PR_created_time_per_id {len(PR_created_time_per_id)}"
                    f"and MTTR_time_per_id {len(MTTR_time_per_id)} do not have the same length!"
                )
                raise Exception(
                    f"PR_created_time_per_id {len(PR_created_time_per_id)}"
                    f"and MTTR_time_per_id {len(MTTR_time_per_id)} do not have the same length!"
                )

            ax1.plot(PR_created_time_per_id,
                     MTTR_time_per_id, "-o", label=author)

            ##############################################################################

            ##############################################################################
            ################ TTR in Time per Author in Project ###########################
            ##############################################################################

            # Plot results
            inputs_plots = []
            for key, pr in data["results"].items():

                if pr["PR_approved"] and pr["PR_approved_by"] == author:
                    # inputs_plots.append([key, pr["PR_TTR"]/(3600*24)])
                    dt_created = datetime.fromtimestamp(pr["PR_created"])
                    dt_approved = datetime.fromtimestamp(pr["PR_approved"])
                    inputs_plots.append(
                        [
                            datetime.fromtimestamp(pr["PR_created"]),
                            (dt_approved - dt_created).total_seconds() / 3600,
                            key,
                            datetime.fromtimestamp(pr["PR_approved"])
                        ]
                    )

            # Sort results by PR ID
            inputs_plots = sorted(inputs_plots, key=lambda x: int(x[2]))

            PR_created_time_per_id = [el[0] for el in inputs_plots]
            TTR_time_per_id = [el[1] for el in inputs_plots]

            if len(PR_created_time_per_id) != len(TTR_time_per_id):
                _LOGGER.warning(
                    f"PR_created_time_per_id {len(PR_created_time_per_id)}"
                    f"and TTR_time_per_id {len(TTR_time_per_id)} do not have the same length!"
                )
                raise Exception(
                    f"PR_created_time_per_id {len(PR_created_time_per_id)}"
                    f"and TTR_time_per_id {len(TTR_time_per_id)} do not have the same length!"
                )

            ax2.plot([el[0] for el in inputs_plots], [el[1]
                                                      for el in inputs_plots], "-o", label=author)

            ##############################################################################

            ##############################################################################
            ############################### Evaluate Score ###############################
            ##############################################################################

            # Relative scores contributions:
            # 1: Number of PR reviewed respect to total number of PR reviewed by the team.
            k1 = 1.1  # Weight factor of the contribution 1

            # 2: Mean time to review a PR by reviewer respect to team repostiory MTTR.
            k2 = 1  # Weight factor of the contribution 2

            # 3: Mean length of PR respect to minimum value of PR length for a specific label.
            k3 = 1.2  # Weight factor of the contribution 3

            # 4: Number of commits respect to the total number of commits in the repository.
            k4 = 1.4  # Weight factor of the contribution 4

            # 5: Time since last review.
            k5 = 1  # Weight factor of the contribution 5

            last_review_author_time = inputs_plots[len(inputs_plots) - 1][3]
            # TODO 6: Number of issue closed by a PR reviewed from an author respect to total number of issue closed.

            final_score = (
                k1 * (Number_PR_reviewed_author / Number_PR_reviewed)
                * k2 * (MTTR / MTTR_author)
                * k3 * (np.mean(PR_scores) / relative_score)
                * k4 * (total_number_commits_author / total_number_commits)
                * k5 * (((last_review_author_time - first_PR_approved_time).total_seconds())/((now_time - first_PR_approved_time).total_seconds()))
            )

            contributor_reviewer.append([
                author,
                Number_PR_reviewed_author,
                str(timedelta(seconds=MTTR_author)),
                mean_PR_length,
                total_number_commits_author,
                total_number_commits_author/total_number_commits*100,
                inputs_plots[len(inputs_plots) -
                             1][0].strftime("%m/%d/%Y, %H:%M:%S"),
                final_score])

            bot_decision_score.append((author, final_score))

            author_reviewer_statistics[author] = Number_PR_reviewed_for_author

            author_contribution_scores[author] = [
                author,
                k1 * (Number_PR_reviewed_author / Number_PR_reviewed),
                k2 * (MTTR / MTTR_author),
                k3 * (np.mean(PR_scores) / relative_score),
                k4 * (total_number_commits_author / total_number_commits),
                "n/a",
                k5 * (((last_review_author_time - first_PR_approved_time).total_seconds()
                       )/((now_time - first_PR_approved_time).total_seconds())),
                final_score,
            ]

            human_percentage += (total_number_commits_author /
                                 total_number_commits)*100

        else:
            if author in BOTS_NAMES:
                bot_contributor.append([
                    author,
                    "0",
                    "n/a",
                    "n/a",
                    total_number_commits_author,
                    total_number_commits_author/total_number_commits*100,
                    "n/a",
                    "n/a"])
                bot_percentage += (total_number_commits_author /
                                   total_number_commits)*100
            else:
                contributor_never_reviewed.append([
                    author,
                    "0",
                    "n/a",
                    "n/a",
                    total_number_commits_author,
                    total_number_commits_author/total_number_commits*100,
                    "n/a",
                    "n/a"])
                human_percentage += (total_number_commits_author /
                                     total_number_commits)*100

    # Sort by score
    contributor_reviewer = sorted(
        contributor_reviewer, key=lambda x: x[7], reverse=True)

    for contributor in contributor_reviewer:
        # Show statistics
        _LOGGER.info(
            "-----------------------------------------------------------------------------------------------------------------------------------------------"
        )
        _LOGGER.info(
            "{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:15} | {:^8.4f} |".format(
                contributor[0],
                contributor[1],
                contributor[2],
                contributor[3],
                contributor[4],
                contributor[5],
                contributor[6],
                contributor[7]
            )
        )

        if detailed_statistics:
            _LOGGER.info(
                "-----------------------------------------------------------------------------------------------------------------------------------------------"
            )
            _LOGGER.info("{:20} -> % {}".format("Reviewed for", 'PR reviewed'))
            for reviewed_for, percentage in author_reviewer_statistics[contributor[0]].items():
                if reviewed_for != author and percentage > 0:
                    _LOGGER.info(
                        "{:20} -> {:.3f}%".format(reviewed_for, percentage))

        if analyze_single_scores:
            _LOGGER.info(
                "{:20} --> {:^9.4f} | {:^25.4f} | {:^9.4f} | {:^12.4f} | {:^14}  | {:^20.4f} | {:^8.4f} |".format(
                    author_contribution_scores[contributor[0]][0],
                    author_contribution_scores[contributor[0]][1],
                    author_contribution_scores[contributor[0]][2],
                    author_contribution_scores[contributor[0]][3],
                    author_contribution_scores[contributor[0]][4],
                    author_contribution_scores[contributor[0]][5],
                    author_contribution_scores[contributor[0]][6],
                    author_contribution_scores[contributor[0]][7],
                )
            )
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )

    if not analyze_single_scores and not filter_contributors:
        for contributor in contributor_never_reviewed:
            _LOGGER.info(
                "-----------------------------------------------------------------------------------------------------------------------------------------------"
            )
            _LOGGER.info("{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:^20} | {:^8} |".format(
                contributor[0],
                contributor[1],
                contributor[2],
                contributor[3],
                contributor[4],
                contributor[5],
                contributor[6],
                contributor[7]))
        _LOGGER.info(
            "-----------------------------------------------------------------------------------------------------------------------------------------------"
        )

        for contributor in bot_contributor:
            _LOGGER.info(
                "-----------------------------------------------------------------------------------------------------------------------------------------------"
            )
            _LOGGER.info("{:20} --> {:^9} | {:^25} | {:^9} | {:^12} | {:^14.3f}% | {:^20} | {:^8} |".format(
                contributor[0],
                contributor[1],
                contributor[2],
                contributor[3],
                contributor[4],
                contributor[5],
                contributor[6],
                contributor[7]))

    ##############################################################################
    ################ MTTR in Time per Author in Project ###########################
    ##############################################################################
    if use_median:
        ax1.set(
            xlabel="PR created date",
            ylabel="Median Time to Review (h)",
            title=f"MTTR in Time per author per project: {project[1] + '/' + project[0]}",
        )
    else:
        ax1.set(
            xlabel="PR created date",
            ylabel="Mean Time to Review (h)",
            title=f"MTTR in Time per author per project: {project[1] + '/' + project[0]}",
        )
    # Shrink current axis by 20%
    box = ax.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.grid()
    author_results_mttr = knowledge_results_repo.joinpath(
        f"MTTR-in-time-{project[1] + '-' + project[0] + '-authors'}.png")
    fig1.savefig(author_results_mttr)
    ##############################################################################

    ##############################################################################
    ################ TTR in Time per Author in Project ###########################
    ##############################################################################
    ax2.set(
        xlabel="PR created date",
        ylabel="Time to Review (h)",
        title=f"TTR in Time per author per project: {project[1] + '/' + project[0]}",
    )
    ax2.legend()
    ax2.grid()
    author_results_ttr = knowledge_results_repo.joinpath(
        f"{project[1] + '-' + project[0] + '-authors'}.png")
    fig2.savefig(author_results_ttr)
    plt.close()
    ##############################################################################

    # Sort results by PR ID
    bot_decision_score_sorted = sorted(
        bot_decision_score, key=lambda x: (x[1]), reverse=True)
    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    requested_reviewers = number_reviewer
    while len(bot_decision_score_sorted) < requested_reviewers:
        _LOGGER.warning(f"Too many reviewers requested: {requested_reviewers}")
        requested_reviewers -= 1
    else:
        _LOGGER.info(f"Number of reviewers identified: {requested_reviewers}")
        _LOGGER.info(
            f"Reviewers: {[reviewer[0] for reviewer in bot_decision_score_sorted[:requested_reviewers]]}")

    _LOGGER.info(
        "-----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    _LOGGER.info("{:20} --> {:^5.3f}% |".format(
        "Human % Tot commits",
        human_percentage)
    )

    _LOGGER.info("{:20} --> {:^5.3f}% |".format(
        "Bot % Tot commits",
        bot_percentage)
    )


if __name__ == "__main__":
    if not PROJECTS:
        _LOGGER.warning(
            "Please insert one project in PROJECTS in create_bot_knowledge.py file.")

    for project in PROJECTS:
        evaluate_reviewers(
            project=project,
            number_reviewer=2,
            detailed_statistics=False,
            analyze_single_scores=False,
            filter_contributors=True,
            use_median=True
        )
