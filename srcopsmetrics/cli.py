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

from srcopsmetrics.bot_knowledge import analyse_projects
from srcopsmetrics.enums import EntityTypeEnum, StoragePath
from srcopsmetrics.evaluate_scores import ReviewerAssigner
from srcopsmetrics.github_knowledge import GitHubKnowledge

_LOGGER = logging.getLogger("aicoe-src-ops-metrics")
logging.basicConfig(level=logging.INFO)


def get_entities_as_list(entities_raw: Optional[str]) -> List[str]:
    """Get passed entities as list."""
    if entities_raw and entities_raw != "":
        return entities_raw.split(",")

    return []


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
    type=str,
    required=False,
    help="""Entities to be analysed for a repository.
            For multiple entities please use format
            -e Foo,Bar,...
            If nothing specified, all entities will be analysed.
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
@click.option(
    "--knowledge-path",
    "-k",
    default=StoragePath.DEFAULT.value,
    required=False,
    help=f"""Environment variable named {StoragePath.LOCATION_VAR}
            with path where all the analysed and processed knowledge
            are stored. Default knowledge path is {StoragePath.DEFAULT.value}
            """,
)
def cli(
    repository: Optional[str],
    organization: Optional[str],
    create_knowledge: bool,
    process_knowledge: bool,
    is_local: bool,
    entities: Optional[str],
    visualize_statistics: bool,
    reviewer_reccomender: bool,
    knowledge_path: str,
):
    """Command Line Interface for SrcOpsMetrics."""
    os.environ["IS_LOCAL"] = "True" if is_local else "False"
    os.environ[StoragePath.LOCATION_VAR.value] = knowledge_path

    repos = GitHubKnowledge.get_repositories(repository=repository, organization=organization)

    entities_args = get_entities_as_list(entities)

    if create_knowledge:
        tupled_repos = [(lambda x: (x[0], x[1]))(repo.split("/")) for repo in repos]
        analyse_projects(projects=tupled_repos, is_local=is_local, entities=entities_args)

    for project in repos:
        os.environ["PROJECT"] = project

        if visualize_statistics:
            raise NotImplementedError
        if reviewer_reccomender:
            reviewer_assigner = ReviewerAssigner()
            reviewer_assigner.evaluate_reviewers_scores(project=project, is_local=is_local)

    if visualize_statistics and repository is not None:
        raise NotImplementedError
    elif visualize_statistics and organization is not None:
        raise NotImplementedError


if __name__ == "__main__":
    cli()
