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

from datetime import datetime
import numpy as np
import pandas as pd
from github import Github
from github.Repository import Repository

from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import (
    PullRequest)
from srcopsmetrics.storage import KnowledgeStorage

import os
import matplotlib.pyplot as plt

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

class Metrics:

    """Metrics used in MI."""

    def __init__(self, repository: str):
        """Initialize with collected knowledge."""
        gh_repo = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50).get_repo( repository )

        self.prs = PullRequest(gh_repo).load_previous_knowledge(is_local=True)
        self.issues = Issue(gh_repo).load_previous_knowledge(is_local=True)

    def get_aggregated_pull_requests(self):
        # cols: AUTHOR PR_SIZE PR_LABELS PR_MERGE_TIME REVIEWERS TTFR
        data = []
        overall_ttfr = []
        overall_ttm = []

        for pr in self.prs.values():

            if not pr["merged_at"]:
                continue

            created_at = int(pr["created_at"])

            ttm = int(pr["merged_at"]) - created_at

            reviewers = [pr["reviews"][r]["author"] for r in pr["reviews"]]
            review_times = [ int(pr["reviews"][r]["submitted_at"]) for r in pr["reviews"] ]
            ttfr = min( review_times ) - created_at if review_times else None

            reviews = [ r for r in pr["reviews"].values() ]
            approvals = [ r["submitted_at"] for r in reviews if r["state"] == "APPROVED" ]
            tta = min( approvals ) - created_at if approvals else None

            overall_ttfr.append( ttfr )
            overall_ttm.append( ttm )

            labels = [k for k in pr["labels"].keys()]

            data.append( [ created_at, pr["created_by"], pr["size"], labels, reviewers, ttm, ttfr, tta] )

        aggregated = pd.DataFrame(data)
        aggregated.columns = [ 'date', 'author', 'size', 'labels', 'reviewers', 'ttm', 'ttfr', 'tta' ]

        factor = aggregated['ttm']
        normal = factor.between( factor.quantile(.05), factor.quantile(.95) )
        return aggregated[normal].sort_values(by=['date']).reset_index(drop=True)


    def get_aggregated_issues(self):
        # cols: LABELS AUTHOR CLOSE_TIME
        pass


    def get_metrics_for_prs(self):
        metrics = self.get_aggregated_pull_requests()[ ['date', 'ttm', 'tta', 'ttfr' ] ].copy()

        metrics[ 'mttm_time'] = None
        metrics[ 'mtta_time' ] = None
        metrics[ 'mttfr_time' ] = None

        for idx in metrics.index:
            metrics.loc[idx, 'mttm_time'] = np.median( metrics['ttm'][:idx+1] )
            metrics.loc[idx, 'mtta_time'] = np.median( metrics['tta'][:idx+1] )
            metrics.loc[idx, 'mttfr_time'] = np.median( metrics['ttfr'][:idx+1] )

        ttm_score = np.poly1d( np.polyfit(metrics['date'], metrics['ttm'], 10) )
        print( f"should be minimal: {1301294.0 - ttm_score(1592385103)}" )
        print( metrics )
        # pd.Series( metrics['ttm'], index=metrics['date']).plot()
        # plt.show()
        # ts = pd.Series(metrics['ttm'], index=pd.date_range("1/1/2000", periods=1000))
        # ts = ts.cumsum()
        metrics[ 'datetime' ] = metrics.apply( lambda x: datetime.fromtimestamp( x['date'] ), axis=1 )
        trendline_pts = np.linspace( metrics.loc[0, 'date'].astype( int ), metrics.loc[ len(metrics.index)-1, 'date'].astype( int ), 100)
        plt.plot(   metrics['datetime'], metrics['ttm'].apply(lambda x: x/3600), '.',
                    metrics['datetime'], metrics['mttm_time'].apply(lambda x: x/3600), '--',
                    [datetime.fromtimestamp(t) for t in trendline_pts], ttm_score( trendline_pts ) / 3600, '-')

        # ts.plot()
        plt.show()




    def get_metrics_for_issues(self):
        aggregated = pd.DataFrame(data) #mean time to comment
        aggregated.columns = [ 'ttci', 'mttci_time', 'ttc', 'mttc_time' ]



