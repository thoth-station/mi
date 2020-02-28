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

from github import Github

_LOGGER = logging.getLogger("aicoe-src-ops-metrics")
logging.basicConfig(level=logging.INFO)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

@click.command()
@click.option(
    "--repository",
    "-r",
    type=str,
    required=False,
    help="Repository to be analysed (e.g thoth-station/performance)",
)
@click.option(
    "--organization",
    "-o",
    type=str,
    required=False,
    help="All repositories of an Organization to be analysed",
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
    "--reviewer-reccomender", "-R", is_flag=True, help="Assign reviewers based on previous knowledge collected."
)
def cli(
    repository: str,
    organization: str,
    create_knowledge: bool,
    is_local: bool,
    visualize_statistics: bool,
    reviewer_reccomender: bool
):
    """Command Line Interface for SrcOpsMetrics."""
    repos = []
    gh = Github(login_or_token=_GITHUB_ACCESS_TOKEN, timeout=50)
    
    if repository is not None:
        repos.append(gh.get_repo(repository).full_name)

    if organization is not None:
        for r in gh.get_organization(organization).get_repos():
            repos.append(r.full_name)

    _LOGGER.info("Overall repositories found: %d" % len(repos))
    if create_knowledge:
        analyse_projects(
            projects=[repo.split("/") for repo in repos],
            is_local=is_local
        )

    if visualize_statistics:
        visualize_project_results(project=project, is_local=is_local)

    if reviewer_reccomender:
        reviewer_assigner = ReviewerAssigner()
        reviewer_assigner.evaluate_reviewers_scores(project=project, is_local=is_local)


if __name__ == "__main__":
    cli()
