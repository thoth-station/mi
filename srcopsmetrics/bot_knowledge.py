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
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules
from typing import List, Optional

from srcopsmetrics.entities import Entity, NOT_FOR_INSPECTION
from srcopsmetrics.exceptions import NotKnownEntitiesError
from srcopsmetrics.github_knowledge import GitHubKnowledge
from srcopsmetrics import utils
from srcopsmetrics import entities

from srcopsmetrics import github_handling

import inspect

_LOGGER = logging.getLogger(__name__)

github_knowledge = GitHubKnowledge()


def _get_all_entities():
    """Return all of the currently implemented entities."""
    entities_classes = []

    for pkg in iter_modules(entities.__path__):
        if pkg.name in NOT_FOR_INSPECTION:
            continue

        module = import_module(f"srcopsmetrics.entities.{pkg.name}")
        for name, klazz in inspect.getmembers(module, inspect.isclass):
            if name != "Entity" and issubclass(klazz, Entity):
                entities_classes.append(klazz)

    _LOGGER.info("########################")
    _LOGGER.info("Detected entities:\n%s", " # ".join([e.name() for e in entities_classes]))
    _LOGGER.info("########################")
    return entities_classes


def analyse_projects(repositories: List[str], is_local: bool = False, entities: Optional[List[str]] = None) -> None:
    """Run Issues (that are not PRs), PRs, PR Reviews analysis on specified projects.

    Arguments:
        projects {List[Tuple[str, str]]} -- one tuple should be in format (project_name, repository_name)
        is_local {bool} -- if set to False, Ceph will be used
        entities {Optional[List[str]]} -- entities that will be analysed. If not specified, all are used.

    """
    path = Path.cwd().joinpath("./srcopsmetrics/bot_knowledge")
    for repo in repositories:
        _LOGGER.info("######################## Analysing %s ########################\n" % repo)
        github_repo = github_handling.connect_to_source(repo)

        project_path = path.joinpath("./" + github_repo.full_name)
        utils.check_directory(project_path)

        allowed_entities = _get_all_entities()

        specified_entities = []
        if entities:
            specified_entities = [e for e in allowed_entities if e.__name__ in entities]
            if specified_entities == []:
                raise NotKnownEntitiesError(
                    message="", specified_entities=entities, available_entities=allowed_entities
                )

        inspected_entities = specified_entities or allowed_entities

        for entity in inspected_entities:
            _LOGGER.info("%s inspection" % entity.__name__)
            github_knowledge.analyse_entity(
                github_repo=github_repo, project_path=project_path, entity_cls=entity, is_local=is_local
            )
            _LOGGER.info("\n")


def visualize_project_results(project: str, is_local: bool = False):
    """Visualize results for a project."""
    raise NotImplementedError("This functionality is currently unavailable")
