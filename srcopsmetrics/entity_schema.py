#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright(C) 2020 Dominik Tuchyna, Francesco Murdaca
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

"""Schema definition for knowledge collected."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from voluptuous import Schema

IssueSchema = Schema(
    {
        int: Schema(
            {
                "created_by": str,
                "created_at": int,
                "closed_by": str,
                "closed_at": int,
                "labels": List[str],
                "interactions": Dict[str, int],
            }
        )
    }
)

PullRequestReviewsSchema = Schema(
    {
        int: Schema(
            {
                "author": str,
                "words_count": int,
                "submitted_at": int,
                "state": str
            }
        )
    }
)

PullRequestSchema = Schema(
    {
        int: Schema(
            {
                "size": str,
                "labels": List[str],
                "created_by": str,
                "created_at": int,
                # "approved_at": pr_approved,
                # "approved_by": pr_approved_by,
                # "time_to_approve": time_to_approve,
                "closed_at": int,
                "closed_by": str,
                "merged_at": int,
                "commits_number": int,
                "referenced_issues": List[int],
                "interactions": Dict[str, int],
                "reviews": PullRequestReviewsSchema,
                "requested_reviewers": List[str],
            }
        )
    }
)
