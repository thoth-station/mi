#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Francesco Murdaca
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

"""Connect and store knowledge for the bots from GitHub."""

import logging
import os
import json

from typing import List
from typing import Tuple
from pathlib import Path

from github import Github
from ogr.services.github import GithubService
from ogr.abstract import Issue, IssueComment, IssueStatus, PullRequest, PRComment, PRStatus, CommitComment

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


_UPDATE_KNOWLEDGE = bool(int(os.getenv("UPDATE_KNOWLEDGE", 0)))

PROJECTS = [
    # AiCoE Team
    # ("log-anomaly-detector", "aicoe"),

    # # Thoth Team
    # ("amun-api", "thoth-station"),
    # ("common", "thoth-station"),
    # ("core", "thoth-station"),
    # ("cve-update-job", "thoth-station"),
    # ("graph-refresh-job", "thoth-station"),
    # ("graph-sync-job", "thoth-station"),
    # ("init-job", "thoth-station"),
    # ("kebechet", "thoth-station"),
    # ("management-api", "thoth-station"),
    # ("metrics-exporter", "thoth-station"),
    # ("notebooks", "thoth-station"),
    # ("package-analyzer", "thoth-station"),
    # ("package-releases-job", "thoth-station"),
    # ("performance", "thoth-station"),
    # ("python", "thoth-station"),
    # ("solver", "thoth-station"),
    # ("storages", "thoth-station"),
    # ("thamos", "thoth-station"),
    # ("thoth-ops", "thoth-station"),
    # ("user-api", "thoth-station"),
]


def connect_to_source(project: Tuple[str, str]):
    """Connect to GitHub.

    :param project: Tuple source repo and repo name.
    """
    # TODO: It should use only one library for source.

    # Connect using ogr
    service = GithubService(token=_GITHUB_ACCESS_TOKEN)

    # Connect using PyGitHub
    g = Github(_GITHUB_ACCESS_TOKEN)
    repo_name = project[1] + "/" + project[0]
    repo = g.get_repo(repo_name)

    return service, repo


def extract_knowledge_from_repository(project: Tuple[str, str], update_knowledge: bool = False):

    service, repo = connect_to_source(project=project)

    ogr_project = service.get_project(repo=project[0], namespace=project[1])
    _LOGGER.info(f"------------------------------------------------------------------------------------")
    _LOGGER.info("Considering repo: %r" % (project[1] + "/" + project[0]))

    if not update_knowledge:
        current_path = Path().cwd()
        source_knowledge_repo = current_path.joinpath("./Bot_Knowledge")

        if not source_knowledge_repo.exists():
            os.mkdir(source_knowledge_repo)

        source_knowledge_file = source_knowledge_repo.joinpath(f'{project[1] + "-" + project[0]}.json')

        if source_knowledge_file.exists():
            _LOGGER.info(f"There is already knowledge from repo {project[1] + '/' + project[0]}")
            _LOGGER.info(f"To update knowledge from a repo, use update_knowledge=True")
            return 0

        else:
            _LOGGER.info(f"No previous knowledge from repo {project[1] + '/' + project[0]}")
            _LOGGER.info(f"Starting to collect knowledge...")
            # Retrieve list of ids of PULL REQUESTS (CLOSED)
            pull_requests = ogr_project.get_pr_list(status=PRStatus.closed)

    if update_knowledge:
        current_path = Path().cwd()
        source_knowledge_repo = current_path.joinpath("./Bot_Knowledge")

        if not source_knowledge_repo.exists():
            os.mkdir(source_knowledge_repo)
            _LOGGER.info(f"No knowledge from any repo has ever been created use update_knowledge=False first.")
            return 0
        else:
            pass

        source_knowledge_file = source_knowledge_repo.joinpath(f'{project[1] + "-" + project[0]}.json')

        if source_knowledge_file.exists():
            # Retrieve list of ids of PULL REQUESTS (CLOSED)
            pull_requests = ogr_project.get_pr_list(status=PRStatus.closed)

            with open(source_knowledge_file, "r") as fp:
                data = json.load(fp)

            pr_id_known = [int(pr_id) for pr_id in data["results"].keys()]
            _LOGGER.debug(f"Known PR ids {pr_id_known}")

            pull_requests_ids = [pr.id for pr in pull_requests]
            _LOGGER.debug(f"PR ids {pr_id_known}")

            pull_requests_unknown_ids = list(set(pull_requests_ids) - set(pr_id_known))
            _LOGGER.debug(f"Unknown PR ids {pull_requests_unknown_ids}")

            pull_requests = [pr for pr in pull_requests if pr.id in pull_requests_unknown_ids]
        else:
            _LOGGER.info(f"No previous knowledge from repo {project[1] + '/' + project[0]}")
            _LOGGER.info(f"To create knowledge from a new repo, use update_knowledge=False")
            return 0

    if pull_requests:

        if update_knowledge:
            results = data["results"]

        else:
            results = {}

        pr_n = 1
        for pr in pull_requests:
            _LOGGER.info(f"Analyzing PR {pr_n}/{len(pull_requests)}")
            _LOGGER.debug(f"PR ID: {pr.id}")
            pull = repo.get_pull(pr.id)
            _LOGGER.debug(f"PR commits number: {pull.commits}")
            commits = pull.commits
            # TODO: Use commits to extract information.
            # commits = [commit for commit in pull.get_commits()]
            reviews = pull.get_reviews()
            labels = pull.get_labels()
            author = str(pull.user.login)

            # Consider time of approved PR
            try:
                step = 0
                while reviews[step].state != "APPROVED":
                    step += 1
                pull_requested_approved = reviews[step].submitted_at
                results[str(pr.id)] = {
                    "PR_labels": [label.name for label in labels],
                    "PR_created": pull.created_at.timestamp(),
                    "PR_approved": pull_requested_approved.timestamp(),
                    "PR_approved_by": str(reviews[step].user.login),
                    "PR_TTR": pull_requested_approved.timestamp() - pull.created_at.timestamp(),
                    "PR_author": author,
                    "PR_commits_number": commits
                }
            except:
                # No review has been submitted (e.g. automatically merged)
                results[str(pr.id)] = {
                    "PR_labels": [label.name for label in labels],
                    "PR_created": pull.created_at.timestamp(),
                    "PR_approved": None,
                    "PR_approved_by": None,
                    "PR_TTR": None,
                    "PR_author": author,
                    "PR_commits_number": commits
                }
                pass

            pr_n += 1

        current_path = Path().cwd()
        source_knowledge_repo = current_path.joinpath("./Bot_Knowledge")
        source_knowledge_file = source_knowledge_repo.joinpath(f'{project[1] + "-" + project[0]}.json')

        if update_knowledge:
            _LOGGER.info(f"Updating knowledge for: {project[1] + '/' + project[0]}")

        project_results = {"name": project[1] + "/" + project[0], "results": results}
        with open(source_knowledge_file, "w") as fp:
            json.dump(project_results, fp)

    else:
        _LOGGER.info(f"No new knowledge from repo {project[1] + '/' + project[0]}")

    return 0


if __name__ == "__main__":
    if not PROJECTS:
        _LOGGER.warning("Please insert one project in PROJECTS variable.")

    for project in PROJECTS:
        extract_knowledge_from_repository(project=project, update_knowledge=_UPDATE_KNOWLEDGE)
