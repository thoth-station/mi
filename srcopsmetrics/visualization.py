#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2019, 2020 Francesco Murdaca, Dominik Tuchyna
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
import os
import itertools

from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

from srcopsmetrics.utils import check_directory
from srcopsmetrics.utils import convert_num2label
from srcopsmetrics.utils import convert_score2num

from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.enums import DeveloperActionEnum
from srcopsmetrics.enums import StatisticalQuantityEnum
from srcopsmetrics.pre_processing import PreProcessing
from srcopsmetrics.entity_schema import IssueSchema
from srcopsmetrics.entity_schema import PullRequestSchema

from plotly.offline import init_notebook_mode, iplot

USE_NOTEBOOK = os.getenv("JUPYTER")

_LOGGER = logging.getLogger(__name__)

pre_processing = PreProcessing()


class Visualization:
    """"Class for visualizing knowledge collected for the bot."""

    _DEVELOPER_ACTION = {"Open": "opened", "Close": "closed"}

    _STATISTICAL_FUNCTION_MAP = {"Median": np.median, "Average": np.average}

    def __init__(self, *, use_notebook: Optional[str] = None):
        """Initialize Visualization class for bot."""
        self.use_notebook = use_notebook or os.getenv("JUPYTER")
        if self.use_notebook:
            _LOGGER.info("Initiate notebook for offline plot")
            init_notebook_mode(connected=True)

    def evaluate_and_remove_outliers(self, data: Dict[str, Any], quantity: str):
        """Evaluate and remove outliers."""
        RANGE_VALUES = 1.5

        df = pd.DataFrame.from_dict(data)
        q = df[f"{quantity}"].quantile([0.25, 0.75])
        Q1 = q[0.25]
        Q3 = q[0.75]
        IQR = Q3 - Q1
        outliers = df[(df[f"{quantity}"] < (Q1 - RANGE_VALUES * IQR)) | (df[f"{quantity}"] > (Q3 + RANGE_VALUES * IQR))]
        _LOGGER.info("Outliers for %r" % quantity)
        _LOGGER.info("Outliers: %r" % outliers)
        filtered_df = df[
            (df[f"{quantity}"] > (Q1 - RANGE_VALUES * IQR)) & (df[f"{quantity}"] < (Q3 + RANGE_VALUES * IQR))
        ]

        return filtered_df

    def analyze_outliers(self, data: Dict[str, Any], quantity: str, columns: Optional[List[str]] = None):
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

        #         filtered_df = self.evaluate_and_remove_outliers(data=subset_data, quantity=quantity)
        #         processed_data += filtered_df.values.tolist()

        #     return processed_data

        filtered_df = self.evaluate_and_remove_outliers(data=data, quantity=quantity)
        processed_data += filtered_df.values.tolist()

        return processed_data

    def create_per_pr_plot(
        self,
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
        # plt.show()
        plt.close()

    def visualize_pr_data(self, project: str, result_path: Path, pr_data: Dict[str, Any]):
        """Visualize results from Pull Requests for a project."""
        projects_reviews_data = pre_processing.pre_process_prs_project_data(data=pr_data)
        prs_ids = projects_reviews_data["ids"]
        prs_created_dts = projects_reviews_data["created_dts"]
        prs_lengths = projects_reviews_data["PRs_size"]

        ttfr = projects_reviews_data["TTFR"]
        mttfr = projects_reviews_data["MTTFR"]

        # MTTFR
        data = {"ids": prs_ids, "MTTFR": mttfr}
        mttfr_per_pr_processed = self.analyze_outliers(quantity="MTTFR", data=data)

        self.create_per_pr_plot(
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
        data = {"ids": prs_ids, "created_dts": prs_created_dts, "TTFR": ttfr, "lengths": prs_lengths}

        tfr_in_time_processed = self.analyze_outliers(quantity="TTFR", data=data)

        self.create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in tfr_in_time_processed],
            y_array=[el[2] for el in tfr_in_time_processed],
            x_label="PR created date",
            y_label="Time to First Review (h)",
            title=f"TTFR in Time per project: {project}",
            output_name="TTFR-in-time",
        )

        self.create_per_pr_plot(
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
        self.create_per_pr_plot(
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
        data = {"created_dts": prs_created_dts, "MTTR": mttr}
        mttr_in_time_processed = self.analyze_outliers(quantity="MTTR", data=data)

        self.create_per_pr_plot(
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
        data = {"ids": prs_ids, "created_dts": prs_created_dts, "TTR": ttr, "lengths": prs_lengths}
        ttr_in_time_processed = self.analyze_outliers(quantity="TTR", data=data)

        self.create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[1] for el in ttr_in_time_processed],
            y_array=[el[2] for el in ttr_in_time_processed],
            x_label="PR created date",
            y_label="Time to Review (h)",
            title=f"TTR in Time per project: {project}",
            output_name="TTR-in-time",
        )

        self.create_per_pr_plot(
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
        self.create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[3] for el in ttr_in_time_processed_sorted],
            y_array=[el[2] for el in ttr_in_time_processed_sorted],
            x_label="PR length",
            y_label="Time to Review (h)",
            title=f"TTR in Time per PR length: {project}",
            output_name="TTR-per-PR-length",
        )

    def visualize_issue_data(
        self, project: str, result_path: Path, issues_data: Dict[str, Any], pr_data: Dict[str, Any]
    ):
        """Visualize results from Issues for a project."""
        project_issues_data = pre_processing.pre_process_issues_project_data(data=issues_data)
        issues_created_dts = project_issues_data["created_dts"]
        issues_ttci = project_issues_data["TTCI"]

        # TTCI
        data = {"created_dts": issues_created_dts, "TTCI": issues_ttci}
        ttci_per_issue_processed = self.analyze_outliers(quantity="TTCI", data=data)
        self.create_per_pr_plot(
            result_path=result_path,
            project=project,
            x_array=[el[0] for el in ttci_per_issue_processed],
            y_array=[el[1] for el in ttci_per_issue_processed],
            x_label="Issue created date",
            y_label="Median Time to Close Issue (h)",
            title=f"TTCI in Time per project: {project}",
            output_name="TTCI-in-time",
        )

        overall_opened_issues = pre_processing.pre_process_issues_creators(issues_data=issues_data)
        self._visualize_issues_per_developer(overall_opened_issues, title="Number of opened issues per each developer")

        overall_closed_issues = pre_processing.pre_process_issues_closers(issues_data=issues_data, pr_data=pr_data)
        self._visualize_issues_per_developer(overall_closed_issues, title="Number of closed issues per each developer")

        overall_issues_interactions = pre_processing.pre_process_issue_interactions(issues_data=issues_data)
        overall_issue_types_creators = pre_processing.pre_process_issue_labels_to_issue_creators(
            issues_data=issues_data
        )
        overall_issue_types_closers = pre_processing.pre_process_issue_labels_to_issue_closers(
            issues_data=issues_data, pull_requests_data=pr_data
        )

        self._visualize_top_x_issues_types_wrt_developers(
            overall_types_data=overall_issue_types_creators, developer_action=DeveloperActionEnum.OPEN.value
        )
        self._visualize_top_x_issues_types_wrt_developers(
            overall_types_data=overall_issue_types_closers, developer_action=DeveloperActionEnum.CLOSE.value
        )
        self._visualize_top_X_issues_types_wrt_project(
            overall_types_data=overall_issue_types_creators, developer_action=DeveloperActionEnum.OPEN.value
        )

        self._visualize_top_x_issue_interactions(overall_issues_interactions)

        self._visualize_ttci_wrt_labels(issues_data=issues_data)

        self._visualize_ttci_wrt_pr_length(issues_data=issues_data, pr_data=pr_data)

    def visualize_developer_activity(self, project: str, developer: str):
        """Create plots that are focused on a single contributor."""
        knowledge_path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")

        pr_data = pre_processing.retrieve_knowledge(
            knowledge_path=knowledge_path, project=project, entity_type=EntityTypeEnum.PULL_REQUEST.value
        )
        issues_data = pre_processing.retrieve_knowledge(
            knowledge_path=knowledge_path, project=project, entity_type=EntityTypeEnum.ISSUE.value
        )

        overall_issues_interactions = pre_processing.pre_process_issue_interactions(issues_data=issues_data)
        overall_issue_types_creators = pre_processing.pre_process_issue_labels_to_issue_creators(
            issues_data=issues_data
        )
        overall_issue_types_closers = pre_processing.pre_process_issue_labels_to_issue_closers(
            issues_data=issues_data, pull_requests_data=pr_data
        )

        self._visualize_issue_interactions(
            overall_issues_interactions=overall_issues_interactions, author_login_id=developer
        )
        self._visualize_issues_types_given_developer(
            overall_issue_types_creators, author_login_id=developer, developer_action=DeveloperActionEnum.OPEN.value
        )
        self._visualize_issues_types_given_developer(
            overall_issue_types_closers, author_login_id=developer, developer_action=DeveloperActionEnum.CLOSE.value
        )

    def visualize_projects_ttci_comparison(self, projects: List[str], is_local: bool = False):
        """Visualize TTCI in form of graph for given projects inside one plot."""
        knowledge_path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")

        projects_data = []
        for project in projects:
            issues_data = pre_processing.retrieve_knowledge(
                knowledge_path=knowledge_path,
                project=project,
                entity_type=EntityTypeEnum.ISSUE.value,
                is_local=is_local,
            )

            project_issues_data = pre_processing.pre_process_issues_project_data(data=issues_data)
            issues_created_dts = project_issues_data["created_dts"]
            issues_ttci = project_issues_data["TTCI"]

            data = {"created_dts": issues_created_dts, "TTCI": issues_ttci}
            ttci_per_issue_processed = self.analyze_outliers(quantity="TTCI", data=data)

            projects_data.append(ttci_per_issue_processed)

        self.create_ttci_multiple_projects_plot(projects_data=projects_data, projects=projects)

    @staticmethod
    def create_ttci_multiple_projects_plot(projects_data: List, projects: List) -> None:
        """Create processed data in time per project plot."""
        for project_data, project_name in zip(projects_data, projects):
            x = [el[0] for el in project_data]
            y = [el[1] for el in project_data]

            plt.plot(x, y, label=project_name)

        plt.xlabel("Issue created date")
        plt.ylabel("Median Time to Close Issue (h)")
        plt.title(f"Median TTCI throughout time per project")

        plt.grid()
        plt.legend()
        plt.show()

    @staticmethod
    def _visualize_issues_per_developer(overall_issue_data: Dict, title: str):
        """For each author visualize number of issues opened or closed by them."""
        df = pd.DataFrame()
        df["authors"] = overall_issue_data.keys()
        df["issues"] = overall_issue_data.values()
        fig = px.bar(df, x="authors", y="issues", title=title, color="authors")
        fig.show()

    @staticmethod
    def _visualize_issue_interactions(overall_issues_interactions: Dict, author_login_id: str):
        """For given author visualize interactions between him and all of the other authors in repository."""
        author_interactions = overall_issues_interactions[author_login_id]

        df = pd.DataFrame()
        df["developers"] = [interactioner for interactioner in author_interactions.keys()]
        df["interactions"] = [author_interactions[interactioner] for interactioner in author_interactions.keys()]

        fig = px.bar(
            df,
            x="developers",
            y="interactions",
            title=f"Interactions w.r.t. issues between {author_login_id} and the others in repository",
            color="developers",
        )
        fig.show()

    @staticmethod
    def _visualize_top_x_issue_interactions(overall_issues_interactions: Dict, top_x: int = 5):
        """Visualze top X most interactions in issues in repository."""
        top_interactions_list = []
        for author in overall_issues_interactions.keys():
            for interactioner in overall_issues_interactions[author].keys():
                top_interactions_list.append(
                    (author, interactioner, overall_issues_interactions[author][interactioner])
                )

        top_interactions_list = sorted(top_interactions_list, key=lambda tup: tup[2], reverse=True)
        top_x_interactions = top_interactions_list[:top_x]

        df = pd.DataFrame()
        df["developers"] = [f"{interaction[0]}/{interaction[1]}" for interaction in top_x_interactions]
        df["interactions"] = [interaction[2] for interaction in top_x_interactions]

        fig = px.bar(
            df,
            x="developers",
            y="interactions",
            title=f"Top {top_x} overall interactions w.r.t. issues in form of <issue_creator>/<issue_commenter>",
            color="developers",
        )
        fig.show()

    @staticmethod
    def _visualize_issues_types_given_developer(overall_types_data: Dict, author_login_id: str, developer_action: str):
        """For given author visualize (categorically by labels) number of opened issues by him."""
        issue_types_data = overall_types_data[author_login_id]
        action = self._DEVELOPER_ACTION[developer_action]

        df = pd.DataFrame()
        df["labels"] = [label for label in issue_types_data.keys()]
        df["issues_count"] = [count for count in issue_types_data.values()]

        fig = px.bar(
            df,
            x="labels",
            y="issues_count",
            title=f"Overall number of {action} issues for {author_login_id} by their label",
            color="labels",
        )
        fig.show()

    def _visualize_top_x_issues_types_wrt_developers(
        self, overall_types_data: Dict, developer_action: str, top_x: int = 5
    ):
        """Visualize top X issue types that had been opened or closed for given repository w.r.t to developer."""
        top_labels_list = []
        for author in overall_types_data.keys():
            for label in overall_types_data[author].keys():
                top_labels_list.append((author, label, overall_types_data[author][label]))

        top_labels_list = sorted(top_labels_list, key=lambda tup: tup[2], reverse=True)
        top_x_labels = top_labels_list[:top_x]

        df = pd.DataFrame()
        df["developer_label"] = [f"{label[0]} -> {label[1]}" for label in top_x_labels]
        df["count"] = [label[2] for label in top_x_labels]

        action = self._DEVELOPER_ACTION[developer_action]

        fig = px.bar(
            df,
            x="developer_label",
            y="count",
            title=f"Top {top_x} overall {action} issue types in form of <{developer_action}> -> <issue_label>",
            color="developer_label",
        )
        fig.show()

    def _visualize_top_X_issues_types_wrt_project(
        self, overall_types_data: Dict, developer_action: str, top_x: int = 5
    ):
        """Visualize overall top X issue types that had been opened || closed for given repository w.r.t to project."""
        top_labels_list = {}
        for author in overall_types_data.keys():
            for label in overall_types_data[author].keys():
                if label not in top_labels_list:
                    top_labels_list[label] = 0
                top_labels_list[label] += overall_types_data[author][label]

        top_x_labels = zip([label for label in top_labels_list.keys()], [count for count in top_labels_list.values()])
        top_x_labels = sorted(top_x_labels, reverse=True, key=lambda tup: tup[1])

        df = pd.DataFrame()
        df["label"] = [tup[0] for tup in top_x_labels][:top_x]
        df["count"] = [tup[1] for tup in top_x_labels][:top_x]

        action = self._DEVELOPER_ACTION[developer_action]

        fig = px.bar(
            df, x="label", y="count", title=f"Top {top_x} overall {action} issue types for project", color="label"
        )
        fig.show()

    @staticmethod
    def _visualize_ttci_wrt_pr_length(issues_data: IssueSchema, pr_data: PullRequestSchema) -> None:
        """For each pull request size label visualize its TTCI.

        Time To Close Issue is summed with respect to all of the Issues
        the Pull requests with given size label have closed.

        :param issues_data:IssueSchema:
        :param pr_data:PullRequestSchema:
        :rtype: None
        """
        pr_size_issues = pre_processing.pre_process_issues_closed_by_pr_size(issues_data=issues_data, pr_data=pr_data)
        df = pd.DataFrame()

        sizes = []
        ttcis = []
        for size in pr_size_issues.keys():
            for ttci in pr_size_issues[size]:
                sizes.append(size)
                ttcis.append(ttci)

        df["size"] = sizes
        df["TTCI"] = ttcis

        fig = px.scatter(df, x="size", y="TTCI", color="size")
        fig.show()

    def _visualize_ttci_wrt_labels(
        self, issues_data: IssueSchema, statistical_quantity: str = StatisticalQuantityEnum.MEDIAN.value
    ) -> None:
        """For each label visualize its Time To Close Issue.

        :param issues_data:IssueSchema:
        :param statistical_quantity:str: Either 'Median' or 'Average'
        :rtype: None
        """
        issues_labels = pre_processing.pre_process_issue_labels_with_ttci(issues_data=issues_data)
        processed_labels = {}
        for label in issues_labels.keys():
            processed_labels[label] = issues_labels[label][0]

        statistical_method = self._STATISTICAL_FUNCTION_MAP[statistical_quantity]

        df = pd.DataFrame()
        df["label"] = [label for label in processed_labels.keys()]
        df["TTCI"] = [statistical_method(label_ttcis) for label_ttcis in processed_labels.values()]

        fig = px.bar(df, x="label", y="TTCI", title=f"{statistical_quantity} TTCI w.r.t. issue labels", color="label")
        fig.update_layout(yaxis_title="Average Time To Close Issue (hrs)", xaxis_title="Label name")
        fig.show()
