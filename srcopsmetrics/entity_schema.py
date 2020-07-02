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

from voluptuous import Schema, Any


class Schemas:
    """Schemas that describes how knowledge should be analysed and stored."""

    Issue = Schema(
        {
            "created_by": str,
            "created_at": int,
            "closed_by": Any(str, None),
            "closed_at": Any(int, None),
            "labels": [str],
            "interactions": {str: int},
        }
    )

    Issues = Schema({str: Issue,})

    PullRequestReview = Schema({"author": str, "words_count": int, "submitted_at": int, "state": str,})

    PullRequestReviews = Schema({str: PullRequestReview,})

    PullRequest = Schema(
        {
            "size": str,
            "labels": [str],
            "created_by": str,
            "created_at": int,
            # "approved_at": pr_approved,
            # "approved_by": pr_approved_by,
            # "time_to_approve": time_to_approve,
            "closed_at": Any(int, None),
            "closed_by": Any(str, None),
            "merged_at": Any(int, None),
            "commits_number": int,
            "referenced_issues": [int],
            "interactions": {str: int},
            "reviews": PullRequestReviews,
            "requested_reviewers": [str],
        }
    )

    PullRequests = Schema({str: PullRequest,})

    ContentFile = Schema({"name": str, "path": str, "content": str})  # TODO: Adjust content type

    ContentFiles = Schema({str: ContentFile,})
