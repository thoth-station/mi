#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright(C) 2019, 2020 Francesco Murdaca, Dominik Tuchyna
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

"""This is the CLI for SrcOpsMetrics to create, visualize, use bot knowledge."""

import logging
import os
from typing import List, Optional

import click

from srcopsmetrics.bot_knowledge import analyse_projects, visualize_project_results
from srcopsmetrics.enums import EntityTypeEnum, StoragePath
from srcopsmetrics.evaluate_scores import ReviewerAssigner
from srcopsmetrics.github_knowledge import GitHubKnowledge
from srcopsmetrics.processing import Processing
from srcopsmetrics.storage import KnowledgeStorage
from srcopsmetrics.utils import remove_previously_processed

_LOGGER = logging.getLogger("aicoe-src-ops-metrics")
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option(
    "--repository", "-r", type=str, required=False, help="Repository to be analysed (e.g thoth-station/performance)",
)
@click.option(
    "--organization", "-o", type=str, required=False, help="All repositories of an Organization to be analysed",
)
@click.option(
    "--create-knowledge",
    "-c",
    is_flag=True,
    help=f"""Create knowledge from a project repository.
            Storage location is {StoragePath.KNOWLEDGE.value}
            Removes all previously processed storage""",
)
@click.option(
    "--process-knowledge",
    "-p",
    is_flag=True,
    help=f"""Process knowledge into more explicit information from collected knowledge.
            Storage location is {StoragePath.PROCESSED.value}""",
)
@click.option(
    "--is-local", "-l", is_flag=True, help="Use local for knowledge loading and storing.",
)
@click.option(
    "--entities",
    "-e",
    multiple=True,
    type=str,
    required=False,
    help="""Entities to be analysed for a repository.
            If not specified, all entities will be analysed.
            Current entities available are:
            """
    + "\n".join([entity.value for entity in EntityTypeEnum]),
)
@click.option(
    "--visualize-statistics",
    "-v",
    is_flag=True,
    help="""Visualize statistics on the project repository knowledge collected.
            Dash application is launched and can be accesed at http://127.0.0.1:8050/""",
)
@click.option(
    "--reviewer-reccomender", "-R", is_flag=True, help="Assign reviewers based on previous knowledge collected."
)
def cli(
    repository: Optional[str],
    organization: Optional[str],
    create_knowledge: bool,
    process_knowledge: bool,
    is_local: bool,
    entities: Optional[List[str]],
    visualize_statistics: bool,
    reviewer_reccomender: bool,
):
    """Command Line Interface for SrcOpsMetrics."""
    os.environ["IS_LOCAL"] = "True" if is_local else "False"

    repos = GitHubKnowledge.get_repositories(repository=repository, organization=organization)

    if create_knowledge:
        analyse_projects(projects=[repo.split("/") for repo in repos], is_local=is_local, entities=entities)

        for repo in repos:
            remove_previously_processed(repo)

    for project in repos:
        os.environ["PROJECT"] = project

        if process_knowledge:
            remove_previously_processed(project)
            issues = KnowledgeStorage(is_local=is_local).load_previous_knowledge(
                project_name=project, knowledge_type=EntityTypeEnum.ISSUE.value
            )
            prs = KnowledgeStorage(is_local=is_local).load_previous_knowledge(
                project_name=project, knowledge_type=EntityTypeEnum.PULL_REQUEST.value
            )
            Processing(issues=issues, pull_requests=prs).regenerate()

        if visualize_statistics:
            visualize_project_results(project=project, is_local=is_local)

        if reviewer_reccomender:
            reviewer_assigner = ReviewerAssigner()
            reviewer_assigner.evaluate_reviewers_scores(project=project, is_local=is_local)

    if visualize_statistics and repository is not None:
        visualize_project_results(project=repository, is_local=is_local)
    elif visualize_statistics and organization is not None:
        # TODO
        raise NotImplementedError


if __name__ == "__main__":
    cli()
