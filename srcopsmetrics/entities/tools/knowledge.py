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

"""Knowledge extraction tools/functions."""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from github import Github, PaginatedList
from github.Issue import Issue

_LOGGER = logging.getLogger(__name__)

STANDALONE_LABELS = {"size"}

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


class GitHubKnowledge:
    """Class that represents statical tools used in knowledge analysis."""

    @staticmethod
    def get_repositories(repository: Optional[str] = None, organization: Optional[str] = None) -> List[str]:
        """Get overall repositories to be inspected.

        :param repository:str:
        :param organization:str:

        :rtype: List of all repositories (repository + repositories in organization)
        """
        repos = []
        gh = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50)

        if repository is not None:
            repos.append(gh.get_repo(repository).full_name)

        if organization is not None:
            repositories = gh.get_organization(organization).get_repos()
            if repositories.totalCount == 0:
                _LOGGER.warn("Organization does not contain any repository")
            for r in repositories:
                repos.append(r.full_name)

        _LOGGER.info("Overall repositories found: %d" % len(repos))
        return repos

    @staticmethod
    def assign_pull_request_size(lines_changes: int) -> str:
        """Assign size of PR is label is not provided."""
        if lines_changes > 1000:
            return "XXL"
        elif lines_changes >= 500 and lines_changes <= 999:
            return "XL"
        elif lines_changes >= 100 and lines_changes <= 499:
            return "L"
        elif lines_changes >= 30 and lines_changes <= 99:
            return "M"
        elif lines_changes >= 10 and lines_changes <= 29:
            return "S"
        elif lines_changes >= 0 and lines_changes <= 9:
            return "XS"
        else:
            _LOGGER.error("Unrecognizable lines changed number %s, using NaN as size label", lines_changes)
            return "NaN"

    @staticmethod
    def get_labeled_size(labels: List[str]) -> Optional[str]:
        """Extract size label from list of labels.

        Size label is in form 'size/<SIZE>', where <SIZE> can be
        XS, S, L, etc...
        """
        for label in labels:
            if label.startswith("size"):
                return label.split("/")[1]
        _LOGGER.error("Size label not found")
        return None

    @staticmethod
    def get_non_standalone_labels(labels: List[str]):
        """Get non standalone labels by filtering them from all of the labels."""
        return [label for label in labels if label not in STANDALONE_LABELS]

    @staticmethod
    def get_only_new_entities(old_data: Dict[str, Any], new_data: PaginatedList) -> PaginatedList:
        """Get new entities (whether PRs or other Issues).

        The comparisson is made on IDs between previously collected
        entities and all currently present entities on GitHub.

        Arguments:PaginatedList
            old_data {Dict[str, Any]} -- previously collected knowledge
            new_data {PaginatedList} -- current entities present on GitHub
                            (acquired by GitHub API)

        Returns:
            List[PaginatedList] -- filtered new data without the old ones

        """
        old_knowledge_ids = [int(id) for id in old_data.keys()]
        _LOGGER.debug("Currently gathered ids %s" % old_knowledge_ids)

        new_knowledge_ids = [pr.number for pr in new_data]

        only_new_ids = set(new_knowledge_ids) - set(old_knowledge_ids)
        if len(only_new_ids) == 0:
            _LOGGER.info("No new knowledge found for update")
        else:
            _LOGGER.info("Updating with %s new IDs" % len(only_new_ids))
            _LOGGER.debug("New ids to be examined are %s" % only_new_ids)
        return [x for x in new_data if x.number in only_new_ids]

    @staticmethod
    def get_interactions(comments) -> Dict:
        """Get overall word count for comments per author."""
        interactions = {comment.user.login: 0 for comment in comments}
        for comment in comments:
            # we count by the num of words in comment
            interactions[comment.user.login] += len(comment.body.split(" "))
        return interactions

    @staticmethod
    def get_labels(issue: Issue) -> Dict[str, Dict[str, Union[int, str]]]:
        """Get non standalone labels by filtering them from all of the labels."""
        labels: Dict[str, Dict[str, Union[int, str]]] = {}

        for event in issue.get_timeline():

            if event.event != "labeled":
                continue

            label = event.__dict__.get("_rawData")["label"]
            if label["name"] in labels.keys():
                continue

            labels[label["name"]] = {
                "color": label["color"],
                "labeled_at": int(event.created_at.timestamp()),
                "labeler": event.actor.login,
            }

        return labels
