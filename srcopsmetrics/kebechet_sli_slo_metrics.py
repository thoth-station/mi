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

from typing import Any, List, Tuple

from srcopsmetrics.entities.thoth_sli_slo import ThothSliSlo
from srcopsmetrics.kebechet_metrics import KebechetMetrics
from srcopsmetrics.storage import get_merge_path


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
        }

        return data

    def _get_sli_slo_for_all_managers(self) -> Tuple[Any, Any]:
        """Return a tuple of overall aggregated metrics and overall sli metrics for each repository."""
        overall_sli_slo_data = {
            "advise": 0,
            "version": 0,
            "update": 0,
            "repository_count": len(self.repositories),
        }

        # raw data per repository
        raw_sli_slo_data = {}

        for repo in self.repositories:

            # for each repo evaluate sli slo
            data = self._evaluate_sli_slo(repo)

            # add data to overall dict
            raw_sli_slo_data[repo] = data

            # add data to overall manager metrics count
            overall_sli_slo_data["advise"] += data["advise"]["is_used"]
            overall_sli_slo_data["version"] += data["version"]["is_used"]
            overall_sli_slo_data["update"] += (
                data["update"]["is_used_in_issues"] or data["update"]["is_used_in_pull_requests"]
            )

        return (overall_sli_slo_data, raw_sli_slo_data)

    def _store_metrics(self, metrics):
        """Store on ceph or locally."""
        sli_slo_entity = ThothSliSlo(repository_name="kebechet_sli_slo")
        sli_slo_entity.stored_entities = metrics

        path = get_merge_path()
        file_name = "kebechet_sli_slo.json"

        sli_slo_entity.save_knowledge(
            file_path=path.joinpath(file_name),
            is_local=self.is_local,
            as_csv=False,
            from_dataframe=False,
            from_singleton=True,
        )

    def evaluate_and_store_sli_slo_kebechet_metrics(self):
        """Evaluate SLI/SLO for all kebechet repositories and store data."""
        (sli_slo_metrics,) = self._get_sli_slo_for_all_managers()
        self._store_metrics(sli_slo_metrics)
