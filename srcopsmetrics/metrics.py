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

import numpy as np
import pandas as pd
from github import Github
from github.Repository import Repository

from srcopsmetrics.entities.issue import Issue
from srcopsmetrics.entities.pull_request import (
    PullRequest)
from srcopsmetrics.storage import KnowledgeStorage

import os

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

class Metrics:

    """Metrics used in MI."""

    def __init__(self, repository: str):
        """Initialize with collected knowledge."""
        gh_repo = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50).get_repo( repository )

        self.prs = PullRequest(gh_repo).load_previous_knowledge(is_local=True)
        self.issues = Issue(gh_repo).load_previous_knowledge(is_local=True)

    def aggregate_pull_requests(self):
        # cols: AUTHOR PR_SIZE PR_LABELS PR_MERGE_TIME REVIEWERS TTFR
        data = []
        for pr in self.prs.values():

            if not pr["merged_at"]:
                continue

            created_at = int(pr["created_at"])

            ttm = int(pr["merged_at"]) - created_at

            reviewers = [pr["reviews"][r]["author"] for r in pr["reviews"]]

            # first_review_time = min( [ int(pr["reviews"][r]["submitted_at"]) for r in pr["reviews"] ] )
            review_times = [ int(pr["reviews"][r]["submitted_at"]) for r in pr["reviews"] ]
            ttfr = min( review_times ) - created_at if review_times else None

            data.append( [pr["created_by"], pr["size"], pr["labels"], ttm, reviewers, ttfr] )

        aggregated = pd.DataFrame(data)
        aggregated.columns = [ 'author', 'size', 'labels', 'ttm', 'reviewers', 'ttfr' ]
        print(aggregated)

    def aggregate_issues(self):
        # cols: LABELS AUTHOR CLOSE_TIME
        pass
