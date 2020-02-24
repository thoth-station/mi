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
import click
import os

from srcopsmetrics.bot_knowledge import analyse_projects
from srcopsmetrics.bot_knowledge import visualize_project_results
from srcopsmetrics.evaluate_scores import ReviewerAssigner


_LOGGER = logging.getLogger("aicoe-src-ops-metrics")
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option(
    "--project",
    "-p",
    type=str,
    required=True,
    help="Project to be analyzed (e.g thoth-station/performance).",
)
@click.option(
    "--create-knowledge",
    "-c",
    is_flag=True,
    help="Create knowledge from a project repository.",
)
@click.option(
    "--is-local",
    "-l",
    is_flag=True,
    help="Use local for knowledge loading and storing.",
)
@click.option("--create-knowledge", "-c", is_flag=True, help="Create knowledge from a project repository.")
@click.option(
    "--visualize-statistics",
    "-v",
    is_flag=True,
    help="Visualize statistics on the project repository knowledge collected.",
)
@click.option(
    "--reviewer-reccomender", "-r", is_flag=True, help="Assign reviewers based on previous knowledge collected."
)
def cli(
    project: str,
    create_knowledge: bool,
    is_local: bool,
    visualize_statistics: bool,
    reviewer_reccomender: bool
):
    """Command Line Interface for SrcOpsMetrics."""
    if create_knowledge:
        projects = project.split(',')
        analyse_projects(
            projects=[repo.split("/") for repo in projects],
            is_local=is_local
        )

    if visualize_statistics:
        visualize_project_results(project=project, is_local=is_local)

    if reviewer_reccomender:
        reviewer_assigner = ReviewerAssigner()
        reviewer_assigner.evaluate_reviewers_scores(project=project, is_local=is_local)


if __name__ == "__main__":
    cli()
