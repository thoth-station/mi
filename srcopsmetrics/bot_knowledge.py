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

import logging
import os
import json

from typing import List
from typing import Tuple

from pathlib import Path

from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.github_knowledge import GitHubKnowledge
from srcopsmetrics.pre_processing import PreProcessing
from srcopsmetrics.visualization import Visualization
from srcopsmetrics.utils import check_directory

_LOGGER = logging.getLogger(__name__)

github_knowledge = GitHubKnowledge()
pre_processing = PreProcessing()
visualization = Visualization()


def analyse_projects(projects: List[Tuple[str, str]], is_local: bool = False) -> None:
    """Run Issues (that are not PRs), PRs, PR Reviews analysis on specified projects.

    Arguments:
        projects {List[Tuple[str, str]]} -- one tuple should be in format (project_name, repository_name)
    """
    path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    for project in projects:
        _LOGGER.info("######################## Start analysis %s ########################" % "/".join(project))
        github_repo = github_knowledge.connect_to_source(project=project)

        project_path = path.joinpath("./" + github_repo.full_name)
        check_directory(project_path)

        github_knowledge.analyse_entity(github_repo, project_path, EntityTypeEnum.ISSUE.value, is_local)
        github_knowledge.analyse_entity(github_repo, project_path, EntityTypeEnum.PULL_REQUEST.value, is_local)
        _LOGGER.info("######################## Analysis ended ########################")


def visualize_project_results(project: str, is_local: bool = False):
    """Visualize results for a project."""
    knowledge_path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    result_path = Path.cwd().joinpath("./srcopsmetrics/knowledge_statistics")

    pr_data = pre_processing.retrieve_knowledge(
        knowledge_path=knowledge_path, project=project, entity_type=EntityTypeEnum.PULL_REQUEST.value, is_local=is_local
    )
    if pr_data:
        visualization.visualize_pr_data(project=project, result_path=result_path, pr_data=pr_data)

        issues_data = pre_processing.retrieve_knowledge(
            knowledge_path=knowledge_path, project=project, entity_type=EntityTypeEnum.ISSUE.value, is_local=is_local
        )
        if issues_data:
            visualization.visualize_issue_data(
                project=project, result_path=result_path, issues_data=issues_data, pr_data=pr_data
            )
