#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

"""Collection of function to visualize statistics from GitHub Project."""

import logging

from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools

import plotly.express as px

from srcopsmetrics.utils import check_directory
from srcopsmetrics.utils import convert_num2label, convert_score2num
from srcopsmetrics.pre_processing import retrieve_knowledge
from srcopsmetrics.pre_processing import pre_process_prs_project_data, pre_process_issues_project_data, preprocess_issues_closers, preprocess_issues_creators, preprocess_issue_interactions, preprocess_issue_labels_to_issue_closers


_LOGGER = logging.getLogger(__name__)


def evaluate_and_remove_outliers(data: Dict[str, Any], quantity: str):
    """Evaluate and remove outliers."""
    RANGE_VALUES = 1.5

    df = pd.DataFrame.from_dict(data)
    q = df[f"{quantity}"].quantile([0.25, 0.75])
    Q1 = q[0.25]
    Q3 = q[0.75]
    IQR = Q3 - Q1
    outliers = df[
        (df[f"{quantity}"] < (Q1 - RANGE_VALUES * IQR)) | (df[f"{quantity}"] > (Q3 + RANGE_VALUES * IQR))
    ]
    _LOGGER.info("Outliers for %r" % quantity)
    _LOGGER.info("Outliers: %r" % outliers)
    filtered_df = df[
        (df[f"{quantity}"] > (Q1 - RANGE_VALUES * IQR)) & (df[f"{quantity}"] < (Q3 + RANGE_VALUES * IQR))
    ]

    return filtered_df


def analyze_outliers(data: Dict[str, Any], quantity: str, columns: Optional[List[str]] = None):
    """Analyze outliers."""
    processed_data = []
    # # Consider PR length
    # if "lengths" in data.keys():
    #     subset_data = dict.fromkeys(data.keys(), [])
    #     for size in ["XS", "S", "M", "L", "XL", "XXL"]:
    #         for pr_id, created_dt, quantity_value, pr_length in itertools.zip_longest(
    #             data["ids"],
    #             data["created_dts"],
    #             data[quantity],
    #             data["lengths"]):
    #             if pr_length==size:
    #                 subset_data["ids"] += [pr_id]
    #                 subset_data["created_dts"].append(created_dt)
    #                 subset_data[quantity].append(quantity_value)
    #                 subset_data["lengths"].append(pr_length)

    #         filtered_df = evaluate_and_remove_outliers(data=subset_data, quantity=quantity)
    #         processed_data += filtered_df.values.tolist()

    #     return processed_data

    filtered_df = evaluate_and_remove_outliers(data=data, quantity=quantity)
    processed_data += filtered_df.values.tolist()

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
    output_name: str,
):
    """Create processed data in time per project plot."""
    fig, ax = plt.subplots()

    x = x_array
    y = y_array

    ax.plot(x, y, "ro")
    plt.gcf().autofmt_xdate()
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    ax.grid()

    check_directory(result_path.joinpath(project))
    team_results = result_path.joinpath(f"{project}/{output_name}.png")
    fig.savefig(team_results)
    plt.close()


def visualize_results(project: str):
    """Visualize results for a project."""
    knowledge_path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    result_path = Path.cwd().joinpath("./srcopsmetrics/knowledge_statistics")

    pr_data = retrieve_knowledge(knowledge_path=knowledge_path, project=project, entity_type="PullRequest")

    if pr_data:
        projects_reviews_data = pre_process_prs_project_data(data=pr_data)
        prs_ids = projects_reviews_data["ids"]
        prs_created_dts = projects_reviews_data["created_dts"]
        prs_lengths = projects_reviews_data["PRs_size"]

        ttfr = projects_reviews_data["TTFR"]
        mttfr = projects_reviews_data["MTTFR"]

        # MTTFR
        data = {
            "ids": prs_ids,
            "MTTFR": mttfr
        }
        mttfr_per_pr_processed = analyze_outliers(
            quantity="MTTFR", data=data
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in mttfr_per_pr_processed],
            y_array=[el[1] for el in mttfr_per_pr_processed],
            x_label="PR created date",
            y_label="Median Time to First Review (h)",
            title=f"MTTFR in Time per project: {project}",
            output_name="MTTFR-in-time",
        )

        # TTFR
        data = {
            "ids": prs_ids,
            "created_dts": prs_created_dts,
            "TTFR": ttfr,
            "lengths": prs_lengths
        }

        tfr_in_time_processed = analyze_outliers(
            quantity="TTFR", data=data
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in tfr_in_time_processed],
            y_array=[el[2] for el in tfr_in_time_processed],
            x_label="PR created date",
            y_label="Time to First Review (h)",
            title=f"TTFR in Time per project: {project}",
            output_name="TTFR-in-time",
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in tfr_in_time_processed],
            y_array=[el[2] for el in tfr_in_time_processed],
            x_label="PR id",
            y_label="Time to First Review (h)",
            title=f"TTFR per PR id per project: {project}",
            output_name="TTFR-per-PR",
        )

        tfr_in_time_processed_sorted = sorted(
            tfr_in_time_processed, key=lambda x: convert_score2num(x[3]), reverse=False
        )
        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[3] for el in tfr_in_time_processed_sorted],
            y_array=[el[2] for el in tfr_in_time_processed_sorted],
            x_label="PR length",
            y_label="Time to First Review (h)",
            title=f"TTFR in Time per PR length: {project}",
            output_name="TTFR-per-PR-length",
        )

        ttr = projects_reviews_data["TTR"]
        mttr = projects_reviews_data["MTTR"]
        # MTTR
        data = {
            "created_dts": prs_created_dts,
            "MTTR": mttr,
        }
        mttr_in_time_processed = analyze_outliers(
            quantity="MTTR", data=data
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in mttr_in_time_processed],
            y_array=[el[1] for el in mttr_in_time_processed],
            x_label="PR created date",
            y_label="Mean Time to Review (h)",
            title=f"MTTR in Time per project: {project}",
            output_name="MTTR-in-time",
        )

        # TTR
        data = {
            "ids": prs_ids,
            "created_dts": prs_created_dts,
            "TTR": ttr,
            "lengths": prs_lengths
        }
        ttr_in_time_processed = analyze_outliers(
            quantity="TTR", data=data
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in ttr_in_time_processed],
            y_array=[el[2] for el in ttr_in_time_processed],
            x_label="PR created date",
            y_label="Time to Review (h)",
            title=f"TTR in Time per project: {project}",
            output_name="TTR-in-time",
        )

        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in ttr_in_time_processed],
            y_array=[el[2] for el in ttr_in_time_processed],
            x_label="PR id",
            y_label="Time to Review (h)",
            title=f"TTR per PR id per project: {project}",
            output_name="TTR-per-PR",
        )

        ttr_in_time_processed_sorted = sorted(
            ttr_in_time_processed, key=lambda x: convert_score2num(x[3]), reverse=False
        )
        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[3] for el in ttr_in_time_processed_sorted],
            y_array=[el[2] for el in ttr_in_time_processed_sorted],
            x_label="PR length",
            y_label="Time to Review (h)",
            title=f"TTR in Time per PR length: {project}",
            output_name="TTR-per-PR-length",
        )
    

    issues_data = retrieve_knowledge(knowledge_path=knowledge_path, project=project, entity_type="Issue")
    if issues_data:
        project_issues_data = pre_process_issues_project_data(data=issues_data)
        issues_created_dts = project_issues_data["created_dts"]
        issues_ttci = project_issues_data["TTCI"]

        # TTCI
        data = {
            "created_dts": issues_created_dts,
            "TTCI": issues_ttci,
        }
        ttci_per_issue_processed = analyze_outliers(
            quantity="TTCI", data=data
        )
        create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in ttci_per_issue_processed],
            y_array=[el[1] for el in ttci_per_issue_processed],
            x_label="Issue created date",
            y_label="Median Time to Close Issue (h)",
            title=f"TTCI in Time per project: {project}",
            output_name="TTCI-in-time",
        )

    overall_opened_issues = preprocess_issues_creators(issues_data=issues_data)
    visualize_issues_per_developer(overall_opened_issues, title='Number of opened issues per each developer')

    overall_closed_issues = preprocess_issues_closers(issues_data=issues_data, pull_reviews_data=pr_data)
    visualize_issues_per_developer(overall_closed_issues, title='Number of closed issues per each developer')

    overall_issues_interactions = preprocess_issue_interactions(issues_data=issues_data)
    visualize_issue_interactions(overall_issues_interactions=overall_issues_interactions, author_login_id='fridex')

    visualize_top_x_issue_interactions(overall_issues_interactions)

    overall_issue_types_openers = preprocess_issue_labels_to_issue_closers(issues_data=issues_data, pull_requests_data=pr_data)
    visualize_issues_types_opened_by_developer(overall_issue_types_openers, author_login_id='fridex')

def visualize_issues_per_developer(overall_issue_data: Dict, title: str):
    """For each author visualize number of issues opened or closed by them."""
    df = pd.DataFrame()
    df['authors'] = overall_issue_data[0]
    df['issues'] = overall_issue_data[1]
    fig = px.bar(df, x='authors', y='issues', title=title, color='authors')
    fig.show()


def visualize_issue_interactions(overall_issues_interactions: Dict, author_login_id: str):
    """For given author visualize interactions between him and all of the other authors in repository."""
    author_interactions = overall_issues_interactions[author_login_id]

    df = pd.DataFrame()
    df['developers'] = [interactioner for interactioner in author_interactions.keys()]
    df['interactions'] = [author_interactions[interactioner] for interactioner in author_interactions.keys()]

    fig = px.bar(df, x='developers', y='interactions', title=f'Interactions w.r.t. issues between {author_login_id} and the others in repository', color='developers')
    fig.show()


def visualize_top_x_issue_interactions(overall_issues_interactions: Dict, top_x: int = 5):
    """Visualze top X most interactions in issues in repository."""
    top_interactions_list = []
    for author in overall_issues_interactions.keys():
        for interactioner in overall_issues_interactions[author].keys():
            top_interactions_list.append( (author, interactioner, overall_issues_interactions[author][interactioner]) )
    
    top_interactions_list = sorted(top_interactions_list, key=lambda tup: tup[2], reverse=True)
    top_x_interactions = top_interactions_list[:top_x]

    df = pd.DataFrame()
    df['developers'] = [f'{interaction[0]}/{interaction[1]}' for interaction in top_x_interactions]
    df['interactions'] = [interaction[2] for interaction in top_x_interactions]

    fig = px.bar(df, x='developers', y='interactions', title=f'Top {top_x} overall interactions w.r.t. issues in form of <issue_creator>/<issue_commenter>', color='developers')
    fig.show()


def projects_ttci_comparisson(projects: List[str]):
    """Visualize TTCI in form of graph for given projects inside one plot."""
    # for project in projects:
    #     issues_data = retrieve_knowledge(knowledge_path=knowledge_path, project=project, entity_type="Issue")

    #     project_issues_data = pre_process_issues_project_data(data=issues_data)
    #     issues_created_dts = project_issues_data["created_dts"]
    #     issues_ttci = project_issues_data["TTCI"]

    #     data = {
    #         "created_dts": issues_created_dts,
    #         "TTCI": issues_ttci,
    #     }
    #     ttci_per_issue_processed = analyze_outliers(
    #         quantity="TTCI", data=data
    #     )
    # TODO: decide on how this metrics should be implemented


def visualize_issues_types_opened_by_developer(overall_openers_data, author_login_id: str):
    """For given author visualize (categorically by labels) number of opened issues by him."""
    opener_data = overall_openers_data[author_login_id]

    df = pd.DataFrame()
    df['labels'] = [label for label in opener_data.keys()]
    df['issues_count'] = [count for count in opener_data.values()]

    fig = px.bar(df, x='labels', y='issues_count', title=f'Overall number of closed issues for {author_login_id} by their label', color='labels')
    fig.show()


def developer_issues_types_closed(project: str, author_login_id: str):
    """For given author visualize (categorically by labels) number of closed issues by him."""
    pass


def project_top_10_issues_type_opened(project: str):
    """Visualize top 10 issue types that are being opened for given repository."""
    pass


def developers_top_10_issues_type_opened(project: str):
    pass


def developers_top_10_issues_type_closed(project: str):
    pass
