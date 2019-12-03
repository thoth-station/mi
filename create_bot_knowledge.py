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

PROJECTS = [
    # AiCoE Team
    # ("log-anomaly-detector", "aicoe"),

    # # Thoth Team
    ("amun-api", "thoth-station"),
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


def check_directory(knowledge_dir, update_knowledge: bool):
    if not knowledge_dir.exists():
        if update_knowledge:
            raise ValueError(f"No knowledge from any repo has ever been created, try using update_knowledge=False first.")

        os.mkdir(knowledge_dir)

def check_file(project_knowledge, update_knowledge: bool):
    if not update_knowledge:
        if project_knowledge.exists():
            raise ValueError(f"There is already knowledge from repo {project[1] + '/' + project[0]}",
                             f"To update knowledge from a repo, use update_knowledge=True")
            
    else:
        if not project_knowledge.exists():
            raise ValueError(f"No previous knowledge from repo {project[1] + '/' + project[0]}",
                             f"To create knowledge from a new repo, use update_knowledge=False")


def pull_analysis(pull, results):
    commits = pull.commits
    # TODO: Use commits to extract information.
    # commits = [commit for commit in pull.get_commits()]

    reviews = pull.get_reviews()
    label_names = [label.name for label in pull.get_labels()]
    author = str(pull.user.login)
    pr_created = pull.created_at.timestamp()

    # Get the review approvation if it exists
    approvation = next((review for review in reviews if review.state == 'APPROVED'), None)
    pr_approved = approvation.submitted_at.timestamp() if approvation is not None else None
    pr_approved_by = str(approvation.user.login) if approvation is not None else None
    pr_ttr = pr_approved - pr_created if approvation is not None else None
    
    results[str(pull.number)] = {
        "PR_labels": label_names,
        "PR_created": pr_created,
        "PR_approved": pr_approved,
        "PR_approved_by": pr_approved_by,
        "PR_TTR": pr_ttr,
        "PR_author": author,
        "PR_commits_number": commits
    }


def extract_knowledge_from_repository(project: Tuple[str, str], update_knowledge: bool = False):

    service, repo = connect_to_source(project=project)

    ogr_project = service.get_project(repo=project[0], namespace=project[1])
    _LOGGER.info(f"------------------------------------------------------------------------------------")
    _LOGGER.info("Considering repo: %r" % (project[1] + "/" + project[0]))

    current_path = Path().cwd()
    
    knowledge_dir = current_path.joinpath("./Bot_Knowledge")
    check_directory(knowledge_dir, update_knowledge)

    project_knowledge = knowledge_dir.joinpath(f'{project[1] + "-" + project[0]}.json')
    check_file(project_knowledge, update_knowledge)

    _LOGGER.info(f"Gathering ids of all closed PRs from {project[1] + '/' + project[0]} ...")
    pull_requests = ogr_project.get_pr_list(status=PRStatus.closed)

    if update_knowledge:
        with open(project_knowledge, "r") as fp:
            data = json.load(fp)

        current_prs = [int(pr_id) for pr_id in data["results"].keys()]
        _LOGGER.debug(f"Currently gathered PR ids {current_prs}")

        refreshed_prs = [pr.id for pr in pull_requests]

        only_new_prs = list(set(refreshed_prs) - set(current_prs))
        _LOGGER.debug(f"New PR ids are {only_new_prs}")

        #pull_requests = [pull_requests[id] for id in only_new_prs]
        pull_requests = [pr for pr in pull_requests if pr.id in only_new_prs]

    if not pull_requests:
        _LOGGER.info(f"No new knowledge from repo {project[1] + '/' + project[0]}")
        return

    results = data['results'] if update_knowledge else {}
    
    for pr_number, pr in enumerate(pull_requests, start=1):
        pull = repo.get_pull(pr.id)
        
        _LOGGER.info(f"Analyzing PR {pr_number}/{len(pull_requests)}")
        _LOGGER.debug(f"PR ID: {pr.id}")
        _LOGGER.debug(f"PR commits number: {pull.commits}")
        
        pull_analysis(pull, results)
    
    project_results = {"name": project[1] + "/" + project[0], "results": results}
    with open(project_knowledge, "w") as fp:
        json.dump(project_results, fp)

    _LOGGER.info(f"New knowledge file for {project[1] + '/' + project[0]} created")


if __name__ == "__main__":
    if not PROJECTS:
        _LOGGER.warning("Please insert one project in PROJECTS variable.")

    for project in PROJECTS:
        extract_knowledge_from_repository(project=project, update_knowledge=False)
