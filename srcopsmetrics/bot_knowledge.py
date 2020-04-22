#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2019 Francesco Murdaca, Dominik Tuchyna
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

"""Create, Visualize, Use bot knowledge from different Software Development Platforms."""

import json
import logging
import os
from pathlib import Path
from typing import List, Tuple

from github.PullRequest import PullRequest

from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.github_knowledge import GitHubKnowledge
from srcopsmetrics.processing import Processing
from srcopsmetrics.storage import KnowledgeStorage
from srcopsmetrics.utils import check_directory
from srcopsmetrics.visualization import Visualization

_LOGGER = logging.getLogger(__name__)

github_knowledge = GitHubKnowledge()


def analyse_projects(projects: List[Tuple[str, str]], is_local: bool = False) -> None:
    """Run Issues (that are not PRs), PRs, PR Reviews analysis on specified projects.

    Arguments:
        projects {List[Tuple[str, str]]} -- one tuple should be in format (project_name, repository_name)
    """
    path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    for project in projects:
        _LOGGER.info(
            "######################## Analysing %s ########################\n" % "/".join(project))
        github_repo = github_knowledge.connect_to_source(project=project)

        project_path = path.joinpath("./" + github_repo.full_name)
        check_directory(project_path)

        _LOGGER.info("Issues inspection")
        github_knowledge.analyse_entity(
            github_repo, project_path, EntityTypeEnum.ISSUE.value, is_local)

        _LOGGER.info("Pull requests inspection")
        github_knowledge.analyse_entity(
            github_repo, project_path, EntityTypeEnum.PULL_REQUEST.value, is_local)

        _LOGGER.info("Content Files inspection")
        github_knowledge.analyse_entity(
            github_repo, project_path, EntityTypeEnum.CONTENT_FILE.value, is_local)


def visualize_project_results(project: str, is_local: bool = False):
    """Visualize results for a project."""
    result_path = Path.cwd().joinpath("./srcopsmetrics/knowledge_statistics")

    storage = KnowledgeStorage(is_local=is_local)

    pr_data = storage.load_previous_knowledge(project_name=project, knowledge_type=EntityTypeEnum.PULL_REQUEST.value)
    issues_data = storage.load_previous_knowledge(project_name=project, knowledge_type=EntityTypeEnum.ISSUE.value)

    processing = Processing(issues=issues_data, pull_requests=pr_data)
    viz = Visualization(processing=processing)

    viz.visualize_pr_data(project=project, result_path=result_path, pr_data=pr_data)
    viz.visualize_issue_data(project=project, result_path=result_path)