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

from pathlib import Path
from typing import Tuple, Dict, Any, List

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from utils import check_directory
from utils import convert_num2label, convert_score2num
from pre_processing import retrieve_knowledge


_LOGGER = logging.getLogger(__name__)


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
        tfr_in_time, ttr_in_time, mtfr_in_time, mttr_in_time, _ = pre_process_project_data(data=data)

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

