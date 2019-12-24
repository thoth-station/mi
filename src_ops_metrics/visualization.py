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

"""Collection of function to visualize statistics from GitHub Project."""

import logging
from typing import Tuple, Dict, Any, List
from pathlib import Path
from datetime import timedelta
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from create_bot_knowledge import load_previous_knowledge
from utils import check_directory


_LOGGER = logging.getLogger(__name__)


def retrieve_knowledge(knowledge_path: Path, project: str) -> Dict[str, Any]:
    """Retrieve knowledge collected for a project."""
    project_knowledge_path = knowledge_path.joinpath("./" + f"{project}")
    pulls_data_path = project_knowledge_path.joinpath("./pull_requests.json")

    return load_previous_knowledge(project, pulls_data_path, "PullRequest")


def post_process_contributors_data(data: Dict[str, Any]):
    """Post process of data for contributors in a project repository."""
    pr_ids = sorted([int(k) for k in data.keys()])

    contributors_reviews_data = {}

    for pr_id in pr_ids:
        pr = data[str(pr_id)]
        initial_number_review = 1
        if pr["reviews"] and pr["size"]:
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

    for reviewer in contributors_reviews_data.keys():
        number_reviews = 0
        for reviews in contributors_reviews_data[reviewer]["reviews"].values():
            number_reviews += len(reviews)

        contributors_reviews_data[reviewer]["number_reviews"] = number_reviews


    return contributors_reviews_data



def post_process_project_data(data: Dict[str, Any]):
    """Post process of data for a given project repository.

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

    ttr_per_pr = []  # [hr]
    mttr_in_time = []  # [hr]
    ttr_in_time = []  # [hr]

    contributors = [] 

    for pr_id in pr_ids:
        pr = data[str(pr_id)]

        if pr["reviews"] and pr["size"]:
            dt_created = datetime.fromtimestamp(pr["created_at"])

            pr_reviewed_dt = [
                datetime.fromtimestamp(review["submitted_at"])
                for review in pr["reviews"].values()
                if review["state"] == "APPROVED"
            ]

            if pr_reviewed_dt:
                dt_approved = max(pr_reviewed_dt)
                ttr_per_pr.append((dt_approved - dt_created).total_seconds() / 3600)

            ttr_in_time.append(
                (
                    dt_created,
                    str(pr_id),
                    (dt_approved - dt_created).total_seconds() / 3600,)
            )

            mttr_in_time.append((dt_created, str(pr_id), np.median(ttr_per_pr)))

        if pr["created_by"] not in contributors:
            contributors.append(pr["created_by"])

    return ttr_in_time, mttr_in_time, contributors


def create_in_time_per_project_plot(
    *,
    result_path: Path,
    project: str,
    processed_data=List[Tuple[datetime, str, float]],
    x_label: str,
    y_label: str,
    title: str,
    output_name: str
):
    """Create processed data in time per project plot."""
    # Plot results
    fig, ax = plt.subplots()

    pr_created_time_per_id = [el[0] for el in processed_data]
    data_in_time_per_id = [el[2] for el in processed_data]

    ax.plot(pr_created_time_per_id, data_in_time_per_id, "-ro")
    plt.gcf().autofmt_xdate()
    ax.set(
        xlabel=x_label,
        ylabel=y_label,
        title=title,
    )
    ax.grid()

    check_directory(result_path.joinpath(project))
    team_results = result_path.joinpath(f"{project}/{output_name}.png")
    fig.savefig(team_results)
    plt.close()


def visualize_results(project: str):
    """Visualize results for a project."""
    knowledge_path = Path.cwd().joinpath("./src_ops_metrics/Bot_Knowledge")
    result_path = Path.cwd().joinpath("./src_ops_metrics/Knowledge_Statistics")

    data = retrieve_knowledge(knowledge_path=knowledge_path, project=project)

    if data:
        ttr_in_time, mttr_in_time = post_process_project_data(data=data)

        create_in_time_per_project_plot(
            result_path=result_path,
            project=project,
            processed_data=mttr_in_time,
            x_label="PR created date",
            y_label="Median Time to Review (h)",
            title=f"MTTR in Time per project: {project}",
            output_name="MTTR-in-time")

        create_in_time_per_project_plot(
            result_path=result_path,
            project=project,
            processed_data=ttr_in_time,
            x_label="PR created date",
            y_label="Time to Review (h)",
            title=f"TTR in Time per project: {project}",
            output_name="TTR-in-time")
