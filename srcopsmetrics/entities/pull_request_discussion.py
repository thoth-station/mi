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

"""Pull Request Discussion Entity."""


from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from voluptuous.schema_builder import Schema

from srcopsmetrics.entities import Entity


class PullRequestDiscussion(Entity):
    """Pull Request Discussion Entity class."""

    entity_schema = Schema([{"user": str, "text": str, "created_at": int, "reactions": list}])

    def analyse(self) -> PaginatedList:
        """Override :func:`~Entity.analyse`."""
        return self.get_only_new_entities()

    def store(self, github_entity: PullRequest):
        """Override :func:`~Entity.store`."""
        self.stored_entities[str(github_entity.number)] = self.__class__.get_conversations(github_entity)

    @staticmethod
    def get_conversations(pull_request: PullRequest):
        """Get conversations for a pull_request."""
        conversations = []
        for c in pull_request.get_issue_comments():
            comment = {
                "user": c.user.login,
                "text": c.body,
                "created_at": int(c.created_at.timestamp()),
                "reactions": [r.content for r in c.get_reactions()],
            }
            conversations.append(comment)
        return conversations

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        return self.repository.get_pulls(state="closed")
