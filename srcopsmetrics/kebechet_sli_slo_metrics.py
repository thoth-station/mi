# Copyright (C) 2022 Dominik Tuchyna
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

"""SLI/SLO metrics for Kebechet managers."""

from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Tuple

from srcopsmetrics.entities.thoth_sli_slo import ThothSliSlo
from srcopsmetrics.kebechet_metrics import KebechetMetrics
from srcopsmetrics.storage import get_merge_path

import numpy as np

USAGE_TIMESTAMPS_DATAFRAME_COLUMNS = ["repository_name", "manager_name", "timestamp"]


def _get_timestamp_from_series(series: pd.Series) -> pd.Series:
    return series.values.astype(np.int64) // 10**9


class KebechetSliSloMetrics:
    """SLI/SLO metrics agregation class for Kebechet managers."""

    def __init__(self, repositories: List[str], is_local: bool = False):
        """Initialize with all kebechet repositories and data location flag."""
        self.repositories = repositories
        self.is_local = is_local

    def _get_usage_sli_update_manager(self, kebechet_metrics):
        is_used_pulls = 0 if kebechet_metrics._get_update_manager_pull_requests().empty else 1
        is_used_issues = 0 if kebechet_metrics._get_update_manager_issues().empty else 1
        return {
            "is_used_in_issues": is_used_issues,
            "is_used_in_pull_requests": is_used_pulls,
        }

    def _get_usage_sli_version_manager(self, kebechet_metrics):
        is_used = 0 if kebechet_metrics._get_version_manager_issues().empty else 1
        return {"is_used": is_used}

    def _get_usage_sli_advise_manager(self, kebechet_metrics):
        is_used = 0 if kebechet_metrics._get_advise_manager_pull_requests().empty else 1
        return {
            "is_used": is_used,
        }

    def _evaluate_sli_slo(self, repository):

        kebechet_metrics = KebechetMetrics(repository, is_local=self.is_local)

        # get sli/slo for managers
        usage_sli_update = self._get_usage_sli_update_manager(kebechet_metrics)
        usage_sli_version = self._get_usage_sli_version_manager(kebechet_metrics)
        usage_sli_advise = self._get_usage_sli_advise_manager(kebechet_metrics)

        # merge data into one dataframe with unique indeces
        data = {
            "advise": usage_sli_advise,
            "version": usage_sli_version,
            "update": usage_sli_update,
            "missing_issue_metrics": kebechet_metrics.issues.empty,
            "missing_pull_request_metrics": kebechet_metrics.pull_requests.empty
        }

        return data

    def _get_sli_slo_for_all_managers(self) -> Tuple[Any, Any]:
        """Return a tuple of overall aggregated metrics and overall sli metrics for each repository."""
        overall_sli_slo_data: Dict[str, Any] = {
            "advise": {"repository_usage_count": 0},
            "version": {"repository_usage_count": 0},
            "update": {"repository_usage_count": 0},
            "overall_repositories": len(self.repositories),
            "repositories_missing_issue_metric": 0,
            "repositories_missing_pull_request_metric": 0,
        }

        # raw data per repository
        raw_sli_slo_data = {}

        for repo in self.repositories:

            # for each repo evaluate sli slo
            data = self._evaluate_sli_slo(repo)

            # add data to overall dict
            raw_sli_slo_data[repo] = data

            # add data to overall manager metrics count
            overall_sli_slo_data["advise"]["repository_usage_count"] += data["advise"]["is_used"]
            overall_sli_slo_data["version"]["repository_usage_count"] += data["version"]["is_used"]
            overall_sli_slo_data["repositories_missing_issue_metric"] += data["missing_issue_metrics"]
            overall_sli_slo_data["repositories_missing_pull_request_metric"] += data["missing_pull_request_metrics"]

            # TODO: update manager & other
            overall_sli_slo_data["update"]["repository_usage_count"] += (
                data["update"]["is_used_in_issues"] or data["update"]["is_used_in_pull_requests"]
            )

        return (overall_sli_slo_data, raw_sli_slo_data)

    def _store_metrics(self, metrics, data_file_name):
        """Store on ceph or locally as csv."""
        sli_slo_entity = ThothSliSlo(repository_name=data_file_name)
        sli_slo_entity.stored_entities = pd.DataFrame(metrics)

        path = Path(get_merge_path())
        data_file_name += ".csv"

        sli_slo_entity.save_knowledge(
            file_path=path.joinpath(data_file_name),
            is_local=self.is_local,
            as_csv=True,
            from_dataframe=True,
            from_singleton=True,
        )

    def evaluate_and_store_sli_slo_kebechet_metrics(self):
        """Evaluate SLI/SLO for all kebechet repositories and store data."""
        sli_slo_metrics, _ = self._get_sli_slo_for_all_managers()
        self._store_metrics(sli_slo_metrics, "kebechet_sli_slo")

    def _evaluate_usage(self, repository: str, usage_data: pd.DataFrame):
        """Evaluate usage timestamps across all managers for specific repository.

        Add usage timestamps to the passed dataframe
        """
        kebechet_metrics = KebechetMetrics(repository, is_local=self.is_local)

        advise = pd.DataFrame(columns=USAGE_TIMESTAMPS_DATAFRAME_COLUMNS)
        advise.timestamp = kebechet_metrics._get_advise_manager_pull_requests().created_at
        advise["manager_name"] = "advise"

        version = pd.DataFrame(columns=USAGE_TIMESTAMPS_DATAFRAME_COLUMNS)
        version.timestamp = kebechet_metrics._get_version_manager_issues().created_at
        version["manager_name"] = "version"

        update = pd.DataFrame(columns=USAGE_TIMESTAMPS_DATAFRAME_COLUMNS)
        update.timestamp = kebechet_metrics._get_update_manager_issues().created_at
        # TODO add PRs
        version["manager_name"] = "version"

        data_list = [
            advise,
            version,
        ]
        # add repo column and convert datetime to timestamps
        for data in data_list:
            data.repository_name = repository
            data.timestamp = _get_timestamp_from_series(data.timestamp)

        data_list.append(usage_data)
        return pd.concat(data_list)

    def _get_usage_counts_for_all_managers(self) -> Any:
        """Return usage timestamps for each repository."""
        data = pd.DataFrame(columns=USAGE_TIMESTAMPS_DATAFRAME_COLUMNS)

        for repo in self.repositories:

            # for each repo evaluate sli slo
            data = self._evaluate_usage(repo, data)

        return data

    def evaluate_and_store_usage_timestamp_sli_slo_kebechet_metrics(self):
        """Evaluate ans save SLI usage counts for all kebechet repositories."""
        usage_counts = self._get_usage_counts_for_all_managers()
        self._store_metrics(usage_counts, "kebechet_usage_counts")
