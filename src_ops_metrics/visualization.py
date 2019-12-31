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
import pandas as pd

from create_bot_knowledge import load_previous_knowledge
from utils import check_directory
from utils import convert_num2label, convert_score2num


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

    tfr_per_pr = {}  # Time to First Review (TTFR) [hr]
    ttr_per_pr = {}   # Time to Review (TTR) [hr]

    mtfr_in_time = {}  # Median TTFR [hr]
    mttr_in_time = {}  # Mean TTR [hr]

    tfr_in_time = {}  # TTFR in time [hr]
    ttr_in_time = {}  # TTR in time [hr]

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
                        review_info_per_reviewer[review["author"]] = []
                        review_info_per_reviewer[review["author"]].append(review["submitted_at"])
                    else:
                        review_info_per_reviewer[review["author"]].append(review["submitted_at"])

            for reviewer, reviewer_info in review_info_per_reviewer.items():
                dt_first_review = datetime.fromtimestamp(reviewer_info[0])

                if reviewer not in tfr_per_pr.keys():
                    tfr_per_pr[reviewer] = []
                    tfr_per_pr[reviewer].append((dt_first_review - dt_created).total_seconds() / 3600)
                    tfr_in_time[reviewer] = []
                    tfr_in_time[reviewer].append(
                        (
                            dt_created,
                            pr_id,
                            (dt_first_review - dt_created).total_seconds() / 3600,
                            pr["size"])
                    )
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

                if dt_approved:
                    if reviewer not in ttr_per_pr.keys():
                        ttr_per_pr[reviewer] = []
                        ttr_per_pr[reviewer].append((dt_approved[0] - dt_created).total_seconds() / 3600)
                        ttr_in_time[reviewer] = []
                        ttr_in_time[reviewer].append(
                            (
                                dt_created,
                                pr_id,
                                (dt_approved[0] - dt_created).total_seconds() / 3600,
                                pr["size"])
                        )
                    else:
                        ttr_per_pr[reviewer].append((dt_approved[0] - dt_created).total_seconds() / 3600)
                        ttr_in_time[reviewer].append(
                            (
                                dt_created,
                                pr_id,
                                (dt_approved[0] - dt_created).total_seconds() / 3600,
                                pr["size"])
                        )

            for reviewer in tfr_per_pr.keys():
                if reviewer not in mtfr_in_time.keys():
                    mtfr_in_time[reviewer] = []
                    mtfr_in_time[reviewer].append((dt_created, pr_id, np.median(tfr_per_pr[reviewer])))
                    mttr_in_time[reviewer] = []
                    mttr_in_time[reviewer].append((dt_created, pr_id, np.median(ttr_per_pr[reviewer])))
                else:
                    mtfr_in_time[reviewer].append((dt_created, pr_id, np.median(tfr_per_pr[reviewer])))
                    mttr_in_time[reviewer].append((dt_created, pr_id, np.median(ttr_per_pr[reviewer])))


            # else:
            #     dt_merged = datetime.fromtimestamp(pr["merged_at"])
            #     ttr_per_pr.append((dt_merged - dt_created).total_seconds() / 3600)

            #     ttr_in_time.append(
            #         (
            #             dt_created,
            #             pr_id,
            #             (dt_merged - dt_created).total_seconds() / 3600,
            #             pr["size"])
            #     )
            #     mttr_in_time.append((dt_created, pr_id, np.median(ttr_per_pr)))

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
        contributors_reviews_data[reviewer]["MTFR_in_time"] = mtfr_in_time[reviewer]
        contributors_reviews_data[reviewer]["MTTR_in_time"] = mttr_in_time[reviewer]

    # # Check if the author reviewed any PR from another team member
    # if author_ttr_per_pr:
    #     author_mttr = np.median(author_ttr_per_pr)
    #     author_prs_reviewed_number = len(author_ttr_per_pr)

    #     author_prs_size = [
    #         ttr_result[4]
    #         for ttr_result in ttr_in_time
    #         if ttr_result[3] == contributor
    #     ]

    #     # Encode Pull Request Size
    #     author_prs_size_encoded = [convert_score2num(label=pr_size) for pr_size in author_prs_size]
    #     author_pr_median_size, assigned_score = convert_num2label(
    #         score=np.median(author_prs_size_encoded)
    #         )
    #     # print(author_pr_median_size, assigned_score)

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

    tfr_per_pr = []  # Time to First Review (TTFR) [hr]
    ttr_per_pr = []  # Time to Review (TTR) [hr]

    mtfr_in_time = []  # Median TTFR [hr]
    mttr_in_time = []  # Mean TTR [hr]

    tfr_in_time = []  # TTFR in time [hr]
    ttr_in_time = []  # TTR in time [hr]

    contributors = [] 

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
                # Take maximum to consider approved by more than one person
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

        if pr["created_by"] not in contributors:
            contributors.append(pr["created_by"])

    return tfr_in_time, ttr_in_time, mtfr_in_time, mttr_in_time, contributors


def remove_outliers(extracted_data: List[Any], columns: List[str], quantity: str):
    """Remove outliers."""
    range_value = 1.5

    processed_data = []

    # Consider PR length
    if len(extracted_data[0]) > 3:
        for pull_request_length in ["XS", "S", "M", "L", "XL", "XXL"]:
            subset_data = [pr for pr in extracted_data if pr[3] == pull_request_length]
            df = pd.DataFrame(subset_data, columns=columns)
            q = df[f'{quantity}'].quantile([0.25, 0.75])
            Q1 = q[0.25]
            Q3 = q[0.75]
            IQR = Q3 - Q1
            outliers = df[
                (df[f'{quantity}'] < (Q1 - range_value * IQR)) | (df[f'{quantity}'] > (Q3 + range_value * IQR))
                ]
            print()
            print("Outliers for", f'{quantity}', f"{pull_request_length}")
            print(outliers)
            filtered_df = df[
                (df[f'{quantity}'] > (Q1 - range_value * IQR)) & (df[f'{quantity}'] < (Q3 + range_value * IQR))
                ]

            processed_data = processed_data + filtered_df.values.tolist()

    else:
        df = pd.DataFrame(extracted_data, columns=columns)
        q = df[f'{quantity}'].quantile([0.25, 0.75])
        Q1 = q[0.25]
        Q3 = q[0.75]
        IQR = Q3 - Q1
        outliers = df[
            (df[f'{quantity}'] < (Q1 - range_value * IQR)) | (df[f'{quantity}'] > (Q3 + range_value * IQR))
            ]
        print()
        print("Outliers for", f'{quantity}')
        print(outliers)
        filtered_df = df[
            (df[f'{quantity}'] > (Q1 - range_value * IQR)) & (df[f'{quantity}'] < (Q3 + range_value * IQR))
            ]
        
        processed_data = processed_data + filtered_df.values.tolist()

    return processed_data


def create_per_pr_plot(
    *,
    result_path: Path,
    project: str,
    x_array: List[Any],
    y_array: List[Any],
    x_label: str,
    y_label: str,
    title: str,
    output_name: str
):
    """Create processed data in time per project plot."""
    fig, ax = plt.subplots()

    x = x_array
    y = y_array

    ax.plot(x, y, "ro")
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
        tfr_in_time, ttr_in_time, mtfr_in_time, mttr_in_time, _ = post_process_project_data(data=data)

    # TFR
        mtfr_in_time_processed = remove_outliers(
                quantity="MTFR",
                extracted_data=mtfr_in_time,
                columns=['Datetime', 'PR ID', "MTFR"]
                )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in mtfr_in_time_processed],
            y_array=[el[2] for el in mtfr_in_time_processed],
            x_label="PR created date",
            y_label="Median Time to First Review (h)",
            title=f"MTTFR in Time per project: {project}",
            output_name="MTTFR-in-time")


        tfr_in_time_processed = remove_outliers(
                quantity="TTFR",
                extracted_data=tfr_in_time,
                columns=['Datetime', 'PR ID', "TTFR", "PR Length"]
                )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in tfr_in_time_processed],
            y_array=[el[2] for el in tfr_in_time_processed],
            x_label="PR created date",
            y_label="Time to First Review (h)",
            title=f"TTFR in Time per project: {project}",
            output_name="TTFR-in-time")

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in tfr_in_time_processed],
            y_array=[el[2] for el in tfr_in_time_processed],
            x_label="PR id",
            y_label="Time to First Review (h)",
            title=f"TTFR per PR id per project: {project}",
            output_name="TTFR-per-PR")

        tfr_in_time_processed_sorted = sorted(tfr_in_time_processed, key = lambda x: convert_score2num(x[3]), reverse=False)
        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[3] for el in tfr_in_time_processed_sorted],
            y_array=[el[2] for el in tfr_in_time_processed_sorted],
            x_label="PR length",
            y_label="Time to First Review (h)",
            title=f"TTFR in Time per PR length: {project}",
            output_name="TTFR-per-PR-length")

    # TTR
        mttr_in_time_processed = remove_outliers(
                quantity="MTTR",
                extracted_data=mttr_in_time,
                columns=['Datetime', 'PR ID', "MTTR"]
                )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in mttr_in_time_processed],
            y_array=[el[2] for el in mttr_in_time_processed],
            x_label="PR created date",
            y_label="Mean Time to Review (h)",
            title=f"MTTR in Time per project: {project}",
            output_name="MTTR-in-time")

        ttr_in_time_processed = remove_outliers(
                        quantity="TTR",
                        extracted_data=ttr_in_time,
                        columns=['Datetime', 'PR ID', "TTR", "PR Length"]
                        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in ttr_in_time_processed],
            y_array=[el[2] for el in ttr_in_time_processed],
            x_label="PR created date",
            y_label="Time to Review (h)",
            title=f"TTR in Time per project: {project}",
            output_name="TTR-in-time")

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in ttr_in_time_processed],
            y_array=[el[2] for el in ttr_in_time_processed],
            x_label="PR id",
            y_label="Time to Review (h)",
            title=f"TTR per PR id per project: {project}",
            output_name="TTR-per-PR")

        ttr_in_time_processed_sorted = sorted(ttr_in_time_processed, key = lambda x: convert_score2num(x[3]), reverse=False)
        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[3] for el in ttr_in_time_processed_sorted],
            y_array=[el[2] for el in ttr_in_time_processed_sorted],
            x_label="PR length",
            y_label="Time to Review (h)",
            title=f"TTR in Time per PR length: {project}",
            output_name="TTR-per-PR-length")

