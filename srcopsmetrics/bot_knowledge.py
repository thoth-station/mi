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

from typing import List, Tuple, Optional

from github.PullRequest import PullRequest

from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.github_knowledge import GitHubKnowledge
from srcopsmetrics.processing import Processing
from srcopsmetrics.utils import check_directory
from srcopsmetrics.visualization import Visualization
from srcopsmetrics.storage import KnowledgeStorage
from srcopsmetrics.report import Report
from srcopsmetrics.exceptions import NotKnownEntities

_LOGGER = logging.getLogger(__name__)

github_knowledge = GitHubKnowledge()


def analyse_projects(
    projects: List[Tuple[str, str]], is_local: bool = False, entities: Optional[List[str]] = None
) -> None:
    """Run Issues (that are not PRs), PRs, PR Reviews analysis on specified projects.

    Arguments:
        projects {List[Tuple[str, str]]} -- one tuple should be in format (project_name, repository_name)
        is_local {bool} -- if set to False, Ceph will be used
        entities {Optional[List[str]]} -- entities that will be analysed. If not specified, all are used.
    """
    path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    for project in projects:
        _LOGGER.info("######################## Analysing %s ########################\n" % "/".join(project))
        github_repo = github_knowledge.connect_to_source(project=project)

        project_path = path.joinpath("./" + github_repo.full_name)
        check_directory(project_path)

        allowed_entities = [e.value for e in EntityTypeEnum]

        if entities:
            check_entities = [i for i in entities if i not in allowed_entities]
            if check_entities:
                raise NotKnownEntities(f"There are Entities requested which are not known: {check_entities}")

        entities = entities or allowed_entities

        for entity in entities:
            _LOGGER.info("%s inspection" % entity)
            github_knowledge.analyse_entity(github_repo, project_path, entity, is_local)


def visualize_project_results(project: str, is_local: bool = False):
    """Visualize results for a project."""
    report = Report(project_name=project)
    report.generate_health_report()
    report.launch()
