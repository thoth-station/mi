#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright(C) 2020 Francesco Murdaca, Dominik Tuchyna
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

"""A base class for collecting bot knowledge from GitHub."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from github import ContentFile, Github, PaginatedList
from github.Repository import Repository

from srcopsmetrics.iterator import KnowledgeAnalysis
from srcopsmetrics.entities import Entity

_LOGGER = logging.getLogger(__name__)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

STANDALONE_LABELS = {"size"}


class GitHubKnowledge:
    """Class of methods entity extraction from GitHub."""

    _FILENAME_ENTITY = {"Issue": "issues", "PullRequest": "pull_requests", "ContentFile": "content_file"}

    def connect_to_source(self, project: Tuple[str, str]) -> Repository:
        """Connect to GitHub.

        :param project: Tuple source repo and repo name.
        """
        # Connect using PyGitHub
        g = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50)
        repo_name = project[0] + "/" + project[1]
        repo = g.get_repo(repo_name)

        return repo

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

    def store_content_file(self, file_content: ContentFile, results: Dict[str, Dict[str, Any]]):
        """Analyse pull request and save its desired features to results.

        Arguments:
            file_content {ContentFile} -- Content File type to be stored.
            results {Dict[str, Dict[str, Any]]} -- dictionary where all the currently
                                                ContentFiles are stored and where the given ContentFile
                                                will be stored.

        """
        results["content_files"] = {
            "name": file_content[0],
            "path": file_content[1],
            "content": file_content[2],
        }

    def analyse_entity(
        self, github_repo: Repository, project_path: Path, entity_cls: Type[Entity], is_local: bool = False
    ):
        """Load old knowledge and update it with the newly analysed one and save it.

        Arguments:
            github_repo {Repository} -- Github repo that will be analysed
            project_path {Path} -- The main directory where the knowledge will be stored
            github_type {str} -- Currently can be: "Issue", "PullRequest", "ContentFile"
            is_local {bool} -- If true, the local store will be used for knowledge loading and storing.

        """
        entity = entity_cls(repository=github_repo)

        with KnowledgeAnalysis(entity=entity, is_local=is_local) as analysis:
            analysis.init_previous_knowledge()
            analysis.run()
            analysis.save_analysed_knowledge()
