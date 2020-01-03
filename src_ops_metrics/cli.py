#!/usr/bin/env python3
# project template
# Copyright(C) 2019, 2020 Francesco Murdaca
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

"""This is the main script of the template project."""

import logging

import click

from create_bot_knowledge import analyse_projects
from visualization import visualize_results
from reviewer_recommender import evaluate_reviewers


_LOGGER = logging.getLogger("aicoe-src-ops-metrics")
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option(
    "--project",
    type=str,
    required=True,
    help="Project to be analyzed (e.g thoth-station/performance).",
)
@click.option(
    "--create-knowledge",
    "-c",
    type=bool,
    default=False,
    show_default=True,
    required=False,
    help="Create knowledge from a project repository.",
)
@click.option(
    "--visualize-statistics",
    "-v",
    type=bool,
    default=False,
    show_default=True,
    required=False,
    help="Visualize statistics on the project repository knowledge collected.",
)
@click.option(
    "--reviewer-reccomender",
    "-r",
    type=bool,
    default=False,
    show_default=True,
    required=False,
    help="Assign reviewers based on previous knowledge collected.",
)
def cli(
    project: str,
    create_knowledge: bool,
    visualize_statistics: bool,
    reviewer_reccomender: bool
):
    """Command Line Interface for SrcOpsMetrics."""
    if create_knowledge:
        analyse_projects(
            projects=[project.split("/")],
        )

    if visualize_statistics:
        visualize_results(
            project=project
        )

    if reviewer_reccomender:
        evaluate_reviewers(
            project=project

        )


if __name__ == "__main__":
    cli()
