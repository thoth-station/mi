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

from srcopsmetrics.utils import check_directory
from srcopsmetrics.utils import convert_num2label, convert_score2num
from srcopsmetrics.pre_processing import retrieve_knowledge
from srcopsmetrics.pre_processing import pre_process_project_data


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

    data = retrieve_knowledge(knowledge_path=knowledge_path, project=project)

    if data:
        projects_reviews_data = pre_process_project_data(data=data)
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
