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

from srcopsmetrics.create_bot_knowledge import analyse_projects
from srcopsmetrics.visualization import visualize_results
from srcopsmetrics.evaluate_scores import evaluate_reviewers_scores


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
    "--use-ceph",
    "-C",
    is_flag=True,
    help="Use ceph for knowledge loading and storing.",
)
@click.option(
    "--visualize-statistics",
    "-v",
    is_flag=True,
    help="Visualize statistics on the project repository knowledge collected.",
)
@click.option(
    "--reviewer-reccomender",
    "-r",
    is_flag=True,
    help="Assign reviewers based on previous knowledge collected.",
)
def cli(
    project: str,
    create_knowledge: bool,
    use_ceph: bool,
    visualize_statistics: bool,
    reviewer_reccomender: bool
):
    """Command Line Interface for SrcOpsMetrics."""
    if create_knowledge:
        projects = project.split(',')
        analyse_projects(
            projects=[repo.split("/") for repo in projects],
            use_ceph=use_ceph,
        )

    if visualize_statistics:
        visualize_results(
            project=project
        )

    if reviewer_reccomender:
        evaluate_reviewers_scores(
            project=project

        )


if __name__ == "__main__":
    cli()
