# Copyright (C) 2020 Dominik Tuchyna
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

"""ThothYaml entity class."""

from typing import Any

import yaml
from github.ContentFile import ContentFile
from github.Issue import Issue
from github.Repository import Repository
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity

THOTH_YAML_PATH = "./thoth.yaml"

UPDATE_KEYWORDS = {
    "Automatic update of dependency",
    "Failed to update dependencies to their latest version",
    "Initial dependency lock"}


class KebechetUpdateManager(Entity):
    """ThothYaml entity used for kebechet manager detection."""

    entity_schema = Schema(
        {
            "type": str,            # manual, automatic, failed
            "request_created": int,
            "sesheta_comment": int,
            "request_closed:": int,  # timestamp
            "request_state": str,
        }
    )

    def __init__(self, repository: Repository):
        """Initialize with repo and prev knowledge."""
        self.stored = {}
        self.repository = repository

    def analyse(self) -> List[GithubContentFile]:
        """Override :func:`~Entity.analyse`."""

    def store(self, update_issue: Issue):
        """Override :func:`~Entity.store`."""

        self.stored[update_issue.number] = {
            "type": ,            # manual, automatic, failed
            "request_created": int,
            "sesheta_comment": int,
            "request_closed:": int,  # timestamp
            "request_state": str,
        }

    def stored_entities(self):
        """Override :func:`~Entity.stored_entities`."""
        return self.stored

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return [issue in self.repository.get_issues(state='closed')
                if (not issue.pull_request and issue.title="Kebechet update")
                or self.is_update_manager(issue.title)]

    @staticmethod
    def is_update_manager(issue_title):
        for keyword in UPDATE_KEYWORDS:
            if keyword in issue_title:
                return True
