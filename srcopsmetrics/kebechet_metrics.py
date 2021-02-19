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

"""Kebechet repository metrics evaluation."""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from github import Github

from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import PullRequest
from srcopsmetrics.storage import KnowledgeStorage

BOT_NAMES = {"sesheta"}

UPDATE_TYPES_AND_KEYWORDS = {
    "automatic": "Automatic update of dependency",
    "failure_notification": "Failed to update dependencies to their latest version",
    "initial_lock": "Initial dependency lock",
}

_LOGGER = logging.getLogger(__name__)
_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


class KebechetMetrics:
    """Kebechet Metrics inspected by MI."""

    def __init__(self, repository: str, today: bool = False):
        """Initialize with collected knowledge."""
        gh_repo = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50).get_repo(repository)

        self.repo_name = repository
        self.prs = PullRequest(gh_repo).load_previous_knowledge(is_local=True)
        self.issues = Issue(gh_repo).load_previous_knowledge(is_local=True)
        self.today = today

    def _get_least_square_polynomial_fit(self, x_series: pd.Series, y_series: pd.Series, degree: int = 3):
        """Apply least square polynomial fit on time metrics data."""
        return np.poly1d(np.polyfit(x_series, y_series, degree))

    def _compute_predictions(self, x_series: pd.Series, y_series: pd.Series, days_ahead: int = 7) -> np.array:
        """Compute estimation of the mean metrics in time for future score.

        Return numpy.array with prediciton for all the available dates
        in self.pr_metrics plus specified days_ahead
        """
        score = self._get_least_square_polynomial_fit(x_series, y_series)
        return score(x_series.append(pd.Series([int(time.time()) * 3600 * 24 for i in range(1, days_ahead + 1)])))

    @staticmethod
    def _get_responded_time(issue) -> Optional[int]:
        for comment in issue["comments"]:
            if comment["author"] in BOT_NAMES:
                return int(comment["created_at"])
        return None

    @staticmethod
    def _get_update_manager_request_type(issue) -> Optional[str]:
        """Get the type of the update request."""
        if issue["title"] == "Kebechet update":
            return "manual"

        for request_type, keyword in UPDATE_TYPES_AND_KEYWORDS.items():
            if keyword in issue["title"]:
                return request_type

        return None

    def _get_update_manager_issues(self):
        data = []
        for issue in self.issues.values():
            issue_type = KebechetMetrics._get_update_manager_request_type(issue)
            if not issue_type:
                continue

            created_at = int(issue["created_at"])
            response = self._get_responded_time(issue)
            ttre = response - created_at if response else None

            closed_at = int(issue["closed_at"]) if issue["closed_at"] else None
            closed_by = issue["closed_by"] if issue["closed_by"] else None
            closed_by_bot = closed_by in BOT_NAMES if closed_by else False
            ttci = closed_at - created_at if closed_at else None

            data.append([created_at, issue_type, ttre, ttci, closed_by_bot])

        df = pd.DataFrame(data)
        df.columns = ["date", "type", "ttre", "ttci", "closed_by_bot"]

        return df.sort_values(by=["date"]).reset_index(drop=True)

    def _get_update_manager_pull_requests(self):
        data = []
        for pr in self.prs.values():
            pr_type = KebechetMetrics._get_update_manager_request_type(pr)
            if not pr_type:
                continue

            created_at = int(pr["created_at"])

            ttm = int(pr["merged_at"]) - created_at if pr["merged_at"] else None

            # TODO: include stats of reviewers?
            # reviewers = [pr["reviews"][r]["author"] for r in pr["reviews"]]
            review_times = [int(pr["reviews"][r]["submitted_at"]) for r in pr["reviews"]]
            ttfr = min(review_times) - created_at if review_times else None

            reviews = [r for r in pr["reviews"].values()]
            approvals = [r["submitted_at"] for r in reviews if r["state"] == "APPROVED"]
            tta = min(approvals) - created_at if approvals else None

            rejected = 1 if ttm is None and pr["closed_at"] is not None else 0
            closed_by_bot = 1 if rejected is not None and pr["closed_by"] in BOT_NAMES else 0
            merged_by_kebechet_bot = 1 if closed_by_bot and not rejected else 0
            rejected_by_kebechet_bot = 1 if closed_by_bot and rejected else 0

            data.append([created_at, pr_type, ttm, ttfr, tta, merged_by_kebechet_bot, rejected_by_kebechet_bot])

        df = pd.DataFrame(data)
        df.columns = ["date", "type", "ttm", "ttfr", "tta", "merged_by_kebechet_bot", "rejected_by_kebechet_bot"]

        return df.sort_values(by=["date"]).reset_index(drop=True)

    def get_overall_stats_update_manager(self):
        """Return stats over whole repository age."""
        prs = self._get_update_manager_pull_requests()

        stats: Dict[str, Any] = {}
        stats["created_pull_requests"] = len(prs)

        stats["rejected"] = len(prs[np.isnan(prs["ttm"])])
        stats["rejected_by_kebechet_bot"] = len(prs[prs["rejected_by_kebechet_bot"] == 1])
        stats["rejected_by_other"] = stats["rejected"] - stats["rejected_by_kebechet_bot"]

        stats["merged"] = len(prs) - stats["rejected"]
        stats["merged_by_kebechet_bot"] = len(prs[prs["merged_by_kebechet_bot"] == 1])
        stats["merged_by_other"] = stats["merged"] - stats["merged_by_kebechet_bot"]

        return stats

    def get_daily_stats_update_manager(self):
        """Get daily stats.

        If self.today set to true, return only stats for current day.
        """
        prs = self._get_update_manager_pull_requests()
        prs["days"] = prs.apply(lambda x: datetime.fromtimestamp(x["date"]).date(), axis=1)

        stats: Dict[datetime, Any] = {}
        day_range = [datetime.now().date()] if self.today else prs["days"].unique()
        for date in day_range:
            prs_day = prs[prs["days"] == date]

            day = {}
            day["created_pull_requests"] = len(prs_day)

            day["rejected"] = len(prs_day[np.isnan(prs_day["ttm"])])
            day["rejected_by_kebechet_bot"] = len(prs_day[prs_day["rejected_by_kebechet_bot"] == 1])
            day["rejected_by_other"] = day["rejected"] - day["rejected_by_kebechet_bot"]

            day["merged"] = len(prs_day) - day["rejected"]
            day["merged_by_kebechet_bot"] = len(prs_day[prs_day["merged_by_kebechet_bot"] == 1])
            day["merged_by_other"] = day["merged"] - day["merged_by_kebechet_bot"]

            if self.today:
                return day

            stats[str(date)] = day

        return stats

    def evaluate_and_store_kebechet_metrics(self, is_local: bool):
        """Calculate and store metrics for every kebechet manager in repository."""
        for get_stats in [self.update_manager]:
            stats = get_stats()

            path = f"./srcopsmetrics/metrics/{self.repo_name}/kebechet_{get_stats.__name__}"
            if self.today:
                curr_day = datetime.now().date()
                path += f"_{str(curr_day)}"
            path += ".json"

            KnowledgeStorage(is_local=is_local).save_knowledge(file_path=Path(path), data=stats)

    def update_manager(self):
        """Calculate and store update manager metrics."""
        overall_stats = self.get_overall_stats_update_manager()
        daily_stats = self.get_daily_stats_update_manager()
        return {"overall": overall_stats, "daily": daily_stats}

    def label_bot_manager(self):
        """Calculate and store label bot manager metrics."""
        raise NotImplementedError

    def thoth_advise(self):
        """Calculate and store thoth advise manager metrics."""
        raise NotImplementedError

    def thoth_provenance(self):
        """Calculate and store promenance manager metrics."""
        raise NotImplementedError

    def pipfile_requirements(self):
        """Calculate and store pipfile requirements manager metrics."""
        raise NotImplementedError