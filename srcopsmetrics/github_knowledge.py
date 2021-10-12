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
from typing import Any, Dict, List, Optional, Type

from github import ContentFile, Github
from github.Repository import Repository

from srcopsmetrics.entities import Entity
from srcopsmetrics.github_handling import GITHUB_TIMEOUT_SECONDS, github_handler
from srcopsmetrics.iterator import KnowledgeAnalysis

_LOGGER = logging.getLogger(__name__)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

STANDALONE_LABELS = {"size"}


class GitHubKnowledge:
    """Class of methods entity extraction from GitHub."""

    _FILENAME_ENTITY = {"Issue": "issues", "PullRequest": "pull_requests", "ContentFile": "content_file"}

    @github_handler
    def get_repositories(self, repository: Optional[str] = None, organization: Optional[str] = None) -> List[str]:
        """Get overall repositories to be inspected.

        :param repository:str:
        :param organization:str:

        :rtype: List of all repositories (repository + repositories in organization)
        """
        repos = []
        gh = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=GITHUB_TIMEOUT_SECONDS)

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
