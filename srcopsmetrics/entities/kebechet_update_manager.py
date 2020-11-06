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

import logging
import typing

from github.Issue import \
    Issue
from github.PaginatedList import \
    PaginatedList
from voluptuous.schema_builder import (
    Schema)

from voluptuous import Any

from srcopsmetrics.entities import \
    Entity

THOTH_YAML_PATH = "./thoth.yaml"

UPDATE_TYPES_AND_KEYWORDS = {
    "automatic": "Automatic update of dependency",
    "failure_notification": "Failed to update dependencies to their latest version",
    "initial_lock": "Initial dependency lock",
}

BOTS = {
    "sesheta",
}

_LOGGER = logging.getLogger(__name__)


class KebechetUpdateManager(Entity):
    """ThothYaml entity used for kebechet manager detection."""

    entity_schema = Schema(
        {
            "request_type": str,  # manual, automatic, failed
            "request_created": int,
            "bot_first_response": Any(None, int),
            "closed_at": int,
            "merged_at": Any(None, int),
        }
    )

    def analyse(self) -> PaginatedList:
        """Override :func:`~Entity.analyse`."""
        return [i for i in self.get_only_new_entities() if i.number not in self.previous_knowledge]

    def store(self, update_request: Issue):
        """Override :func:`~Entity.store`."""
        _LOGGER.info("ID: %s", update_request.number)
        responses = self.__class__.get_bot_responses(update_request)

        self.stored_entities[str(update_request.number)] = {
            "request_type": self.__class__.get_request_type(update_request),
            "request_created": int(update_request.created_at.timestamp()),
            "bot_first_response": responses[0],
            "closed_at": int(update_request.closed_at.timestamp()),
            "merged_at": self.__class__.get_merged_at(update_request),
        }

    @staticmethod
    def get_merged_at(update_request: Issue) -> typing.Optional[int]:
        if update_request.pull_request:
            int(update_request.as_pull_request().merged_at.timestamp())
        return None

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return [
            issue for issue in self.repository.get_issues(state="closed") if self.__class__.is_update_request(issue)
        ]

    @staticmethod
    def is_update_request(issue: Issue) -> bool:
        """Find out if issue is a form of update request or not."""
        if not issue.pull_request:
            return issue.title == "Kebechet update"

        for keyword in UPDATE_TYPES_AND_KEYWORDS.values():
            if keyword in issue.title:
                return True

        return False

    @staticmethod
    def get_request_type(issue: Issue) -> str:
        """Get the type of the update request."""
        for request_type, keyword in UPDATE_TYPES_AND_KEYWORDS.items():
            if keyword in issue.title:
                return request_type

        _LOGGER.info(f"Update request not recognized, issue num.{issue.number}")
        return "not_recognized"

    @staticmethod
    def get_bot_responses(issue: Issue) -> typing.List[typing.Optional[int]]:
        """Get timestamps for all bot comments in issue."""
        responses = []
        for comment in issue.get_comments():
            if comment.user.login in BOTS:
                responses.append(int(comment.created_at.timestamp()))
        return responses if len(responses) != 0 else [None]
