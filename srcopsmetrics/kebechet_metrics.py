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
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from github import Github

from srcopsmetrics import utils
from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import PullRequest
from srcopsmetrics.entities.tools.storage import KnowledgeStorage
from srcopsmetrics.storage import get_merge_path

BOT_NAMES = {"sesheta"}

UPDATE_TYPES_AND_KEYWORDS = {
    "manual": "Kebechet update",
    "automatic": "Automatic update of dependency",
    "failure_notification": "Failed to update dependencies to their latest version",
    "initial_lock": "Initial dependency lock",
}

_LOGGER = logging.getLogger(__name__)
_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


def get_update_manager_request_type(title: str) -> Optional[str]:
    """Get the type of the update request."""
    if title == UPDATE_TYPES_AND_KEYWORDS["manual"]:
        return "manual"

    for request_type, keyword in UPDATE_TYPES_AND_KEYWORDS.items():
        if keyword in title:
            return request_type

    return None


class KebechetMetrics:
    """Kebechet Metrics inspected by MI."""

    def __init__(self, repository: str, is_local: bool = False, day: Optional[date] = None):
        """Initialize with collected knowledge."""
        gh_repo = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50).get_repo(repository)

        self.repo_name = repository
        self.prs = PullRequest(gh_repo).load_previous_knowledge(is_local=is_local)
        self.issues = Issue(gh_repo).load_previous_knowledge(is_local=is_local)
        self.day = day
        self.is_local = is_local
        self.root_dir = get_merge_path()

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

    def _get_update_manager_pull_requests(self) -> pd.DataFrame:

        if self.prs.empty:
            return pd.DataFrame()

        self.prs["type"] = self.prs["title"].apply(lambda x: get_update_manager_request_type(x))

        requests = self.prs[~self.prs["type"].isnull()].copy()

        requests["ttm"] = requests.merged_at.sub(requests.created_at)
        requests["tta"] = requests.first_approve_at - requests.created_at
        requests["ttfr"] = requests.created_at - requests.first_review_at

        not_merged = requests["merged_at"].isna()
        closed_by_bot = requests.closed_by.isin(BOT_NAMES)

        requests["merged_by_kebechet_bot"] = requests.merged_by.isin(BOT_NAMES)
        requests["rejected_by_kebechet_bot"] = not_merged & closed_by_bot

        return requests.sort_values(by=["created_at"]).reset_index(drop=True)

    def get_overall_stats_update_manager(self) -> Dict[str, Any]:
        """Return stats over whole repository age."""
        prs = self._get_update_manager_pull_requests()

        if prs.empty:
            return {}

        stats: Dict[str, Any] = {}
        stats["created_pull_requests"] = len(prs)

        stats["rejected"] = len(prs[np.isnan(prs["ttm"])])
        stats["rejected_by_kebechet_bot"] = len(prs[prs["rejected_by_kebechet_bot"] == 1])
        stats["rejected_by_other"] = stats["rejected"] - stats["rejected_by_kebechet_bot"]

        stats["merged"] = len(prs) - stats["rejected"]
        stats["merged_by_kebechet_bot"] = len(prs[prs["merged_by_kebechet_bot"] == 1])
        stats["merged_by_other"] = stats["merged"] - stats["merged_by_kebechet_bot"]

        median_time = prs["ttm"].median()
        stats["median_ttm"] = median_time.total_seconds() if not pd.isna(median_time) else 0

        return stats

    def get_daily_stats_update_manager(self) -> Dict[str, Any]:
        """Get daily stats.

        If self.day is set, return only stats for that day.
        """
        prs = self._get_update_manager_pull_requests()

        if prs.empty:
            return {}

        prs["date"] = pd.to_datetime(prs.created_at).dt.date

        stats: Dict[str, Any] = {}

        if self.day:
            prs = prs[prs.date == self.day]

        for specific_date in prs.date.unique():
            prs_day = prs[prs["days"] == specific_date]

            day = {}
            day["created_pull_requests"] = len(prs_day)

            day["rejected"] = len(prs_day[np.isnan(prs_day["ttm"])])
            day["rejected_by_kebechet_bot"] = len(prs_day[~prs_day["rejected_by_kebechet_bot"].isnull()])
            day["rejected_by_other"] = day["rejected"] - day["rejected_by_kebechet_bot"]

            day["merged"] = len(prs_day) - day["rejected"]
            day["merged_by_kebechet_bot"] = len(prs_day[~prs_day["merged_by_kebechet_bot"].isnull()])
            day["merged_by_other"] = day["merged"] - day["merged_by_kebechet_bot"]

            # TODO consider adding median_time to every day statistics (rolling windown maybe?)

            if self.day:
                median_time = prs[prs["days"] == self.day]["ttm"].median()
                day["median_ttm"] = median_time if not np.isnan(median_time) else 0
                return day

            stats[str(specific_date)] = day

        return stats

    def evaluate_and_store_kebechet_metrics(self):
        """Calculate and store metrics for every kebechet manager in repository."""
        for get_stats in [self.update_manager]:
            stats = get_stats()

            path = Path(f"./{self.root_dir}/{self.repo_name}/")
            utils.check_directory(path)

            file_name = f"kebechet_{get_stats.__name__}"
            if self.day:
                file_name += f"_{str(self.day)}"
            file_name += ".json"

            KnowledgeStorage(is_local=self.is_local).save_data(file_path=path.joinpath(file_name), data=stats)

    @staticmethod
    def merge_kebechet_metrics_per_day(day: date, is_local: bool = False):
        """Merge all the collected metrics under given parent directory."""
        overall_today = {
            "created_pull_requests": 0,
            "rejected": 0,
            "rejected_by_kebechet_bot": 0,
            "rejected_by_other": 0,
            "merged": 0,
            "merged_by_kebechet_bot": 0,
            "merged_by_other": 0,
        }
        ttms = []

        ks = KnowledgeStorage(is_local=is_local)
        for manager_name in ["update_manager"]:

            file_name = f"kebechet_{manager_name}_{str(day)}.json"

            for path in Path(Path(f"./{get_merge_path()}/")).rglob(f"*{file_name}"):
                if path.name == f"overall_{file_name}":
                    continue
                data = ks.load_data(file_path=path, as_json=True)
                for k in data["daily"]:
                    if k == "median_ttm":
                        ttms.append(data["daily"][k])
                    else:
                        overall_today[k] += data["daily"][k]

            ttm_median = np.nanmedian(ttms)
            overall_today["median_ttm"] = ttm_median if not np.isnan(ttm_median) else None

            path = Path(f"./{get_merge_path()}/overall_{file_name}")
            ks.save_data(path, overall_today)

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
