#!/usr/bin/env python3
# Copyright (C) 2021 Dominik Tuchyna
#
# This file is part of thoth-station/mi - Meta-information Indicators.
#
# thoth-station/mi - Meta-information Indicators is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thoth-station/mi - Meta-information Indicators is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with thoth-station/mi - Meta-information Indicators.  If not, see <http://www.gnu.org/licenses/>.

"""Metrics for MI."""

import os
from datetime import datetime
from pathlib import Path

import time
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from github import Github

from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import PullRequest
from srcopsmetrics.utils import check_directory

from typing import Dict

_LOGGER = logging.getLogger(__name__)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


class Metrics:
    """Metrics used in MI."""

    def __init__(self, repository: str, visuaize: bool = False):
        """Initialize with collected knowledge."""
        gh_repo = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50).get_repo(repository)

        self.repo_name = repository
        self.prs = PullRequest(gh_repo).load_previous_knowledge(is_local=True)
        self.issues = Issue(gh_repo).load_previous_knowledge(is_local=True)
        self.visualize = visuaize

    def get_aggregated_pull_requests_with_known_metrics(self) -> pd.DataFrame:
        """Aggregate analysed data, calculate known metrics from it and return DataFrame.

        Known metrics (meaning they can be calculated while looking on single Pull
        Request) are currently tta, ttm and ttfr (see entity README for more information).
        """
        data = []
        overall_ttfr = []
        overall_ttm = []

        for pr in self.prs.values():

            if not pr["merged_at"]:
                continue

            created_at = int(pr["created_at"])

            ttm = int(pr["merged_at"]) - created_at

            reviewers = [pr["reviews"][r]["author"] for r in pr["reviews"]]
            review_times = [int(pr["reviews"][r]["submitted_at"]) for r in pr["reviews"]]
            ttfr = min(review_times) - created_at if review_times else None

            reviews = [r for r in pr["reviews"].values()]
            approvals = [r["submitted_at"] for r in reviews if r["state"] == "APPROVED"]
            tta = min(approvals) - created_at if approvals else None

            overall_ttfr.append(ttfr)
            overall_ttm.append(ttm)

            labels = [k for k in pr["labels"].keys()]

            data.append([created_at, pr["created_by"], pr["size"], labels, reviewers, ttm, ttfr, tta])

        aggregated = pd.DataFrame(data)
        aggregated.columns = ["date", "author", "size", "labels", "reviewers", "ttm", "ttfr", "tta"]

        factor = aggregated["ttm"]
        normal = factor.between(factor.quantile(0.05), factor.quantile(0.95))
        return aggregated[normal].sort_values(by=["date"]).reset_index(drop=True)

    def save_graph_for_metrics(self, metrics_name: str, time_metrics_name: str):
        """Save graph for known metrics, time metrics and their scores."""
        score_fit = self.get_least_square_polynomial_fit(time_metrics_name)

        one_week_ahead_timestamp = int(time.time()) + 3600 * 24 * 7

        trendline_pts = np.linspace(
            self.pr_metrics.loc[0, "date"].astype(int),
            one_week_ahead_timestamp,
            len(self.pr_metrics.index) + 7,  # because we are making one week ahead prediction
        )

        plt.xlabel("Pull requests creation date")
        plt.ylabel(f"Metrics {metrics_name} and {time_metrics_name} represented in hours")

        plt.xticks(rotation=45, ha="right")
        plt.plot(
            self.pr_metrics["datetime"],
            self.pr_metrics[metrics_name].apply(lambda x: x / 3600),
            ".",
            label=metrics_name,
        )
        plt.plot(
            self.pr_metrics["datetime"],
            self.pr_metrics[time_metrics_name].apply(lambda x: x / 3600),
            "--",
            label=time_metrics_name,
        )
        plt.plot(
            [datetime.fromtimestamp(t) for t in trendline_pts],
            score_fit(trendline_pts) / 3600,
            "-",
            label=f"{metrics_name} score",
        )
        plt.legend(loc="upper left")

        path = f"./srcopsmetrics/knowledge_statistics/{self.repo_name}"
        check_directory(Path(path))
        plt.savefig(f"{path}/{metrics_name}", dpi=300)
        _LOGGER.info("Saved visualization %s", path)
        plt.clf()

    def get_least_square_polynomial_fit(self, time_metrics_name: str, degree: int = 3):
        """Apply least square polynomial fit on time metrics data."""
        # TODO: score should be calculated from e.g. weekly stats, not overall
        # TODO: what degree would be best?
        return np.poly1d(np.polyfit(self.pr_metrics["date"], self.pr_metrics[time_metrics_name], degree))

    def compute_predictions(self, time_metrics_name: str, days_ahead: int = 7) -> np.array:
        """Compute estimation of the mean metrics in time for future score.

        Return numpy.array with prediciton for all the available dates
        in self.pr_metrics plus specified days_ahead
        """
        score = self.get_least_square_polynomial_fit(time_metrics_name)
        return score(
            self.pr_metrics["date"].append(pd.Series([int(time.time()) * 3600 * 24 for i in range(1, days_ahead + 1)]))
        )

    def evaluate_scores_for_pull_requests(self) -> Dict[str, int]:
        """Get scores for Pull Requests.

        Current supported metrics are tta, ttm and tffr, with their time counterparts
        being calculated along the scores as well.

        Scores are based on calculating the difference between the
        last known metric and the last prediction of fitted polynomial on metrics.
        Therefore, if the score is negative, we expect repository health to worsen in following week,
        on the other hand if the score is positive, we expect the health to be better.
        """
        self.pr_metrics = self.get_aggregated_pull_requests_with_known_metrics()[["date", "ttm", "tta", "ttfr"]].copy()

        self.pr_metrics["mttm_time"] = float()
        self.pr_metrics["mtta_time"] = float()
        self.pr_metrics["mttfr_time"] = float()

        for idx in self.pr_metrics.index:
            self.pr_metrics.loc[idx, "mttm_time"] = np.median(self.pr_metrics["ttm"][: idx + 1])
            self.pr_metrics.loc[idx, "mtta_time"] = np.nanmedian(self.pr_metrics["tta"][: idx + 1])
            self.pr_metrics.loc[idx, "mttfr_time"] = np.nanmedian(self.pr_metrics["ttfr"][: idx + 1])

        self.pr_metrics["datetime"] = self.pr_metrics.apply(lambda x: datetime.fromtimestamp(x["date"]), axis=1)

        if self.visualize:
            self.save_graph_for_metrics("ttm", "mttm_time")
            self.save_graph_for_metrics("tta", "mtta_time")
            self.save_graph_for_metrics("ttfr", "mttfr_time")

        metrics = {"mttm_time", "mtta_time", "mttfr_time"}
        scores = {k: 0 for k in metrics}
        for metric in metrics:
            prediction = self.compute_predictions(metric)[-1]
            last_known_metric = self.pr_metrics.loc[len(self.pr_metrics.index) - 1, "mttm_time"]
            scores[metric] = last_known_metric - prediction

        return scores
