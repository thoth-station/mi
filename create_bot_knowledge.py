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

from typing import List, Tuple, Dict, Optional, Union, Set
from pathlib import Path


from ogr.services.github import GithubService
from ogr.abstract import PRComment, PRStatus, CommitComment, GitProject

from github import Github, GithubObject, Issue, IssueComment, PullRequest, PullRequestReview
from github.Repository import Repository

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

PROJECTS = os.getenv("PROJECTS") #[
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
#]


def connect_to_source(project: Tuple[str, str]) -> Tuple[GithubService, Repository]:
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


def check_directory(knowledge_dir: Path):
    """Check if directory for bot knowledge exists. If not, create one."""
    if not knowledge_dir.exists():
        _LOGGER.info("No knowledge from any repo has ever been created, creating new directory at %s" % knowledge_dir)
        os.makedirs(knowledge_dir)


issue_keywords = {'close',
                  'closes',
                  'closed',
                  'fix',
                  'fixes', 
                  'fixed',
                  'resolve', 
                  'resolves', 
                  'resolved'}


standalone_labels = {'size'}

def get_labeled_size(labels: List[str]) -> str:
    for label in labels:
        if label.startswith('size'):
            return label.split('/')[1]

def get_non_standalone_labels(labels: List[str]):
    return [label for label in labels if label not in standalone_labels]

def analyse_issues(pull_request: PullRequest) -> Set[int]:
    #left for later if we want to further process the issues or not
    return get_referenced_issues(pull_request)

def get_referenced_issues(pull_request : PullRequest) -> Set[int]:
    issues_referenced = []
    for comment in pull_request.get_issue_comments():
        message = comment.body.split(' ')
        for idx, word in enumerate(message):
            if word in issue_keywords:
                try:
                    _LOGGER.info('      ...found keyword referencing issue')
                    referenced_issue_number = message[idx+1]
                    assert(referenced_issue_number).startswith('https')
                    # last element of url is always the issue number
                    issues_referenced.append(referenced_issue_number.split('/')[-1])
                    _LOGGER.info('      ...referenced issue number present')
                    # we assure that this was really referenced issue
                    # and not just a keyword without number
                except:
                    _LOGGER.info('      ...referenced issue number absent')

    return issues_referenced


def get_only_new_entities(old_data: json, new_data) -> List:
    old_knowledge_ids = [int(id) for id in old_data.keys()]
    _LOGGER.debug("Currently gathered ids %s" % old_knowledge_ids)

    new_knowledge_ids = [pr.number for pr in new_data]

    only_new_ids = set(new_knowledge_ids) - set(old_knowledge_ids)
    if len(only_new_ids) == 0:
        _LOGGER.info("No new knowledge found for update")
    else:
        _LOGGER.debug("New ids to be examined are %s" % only_new_ids)

    return [x for x in new_data if x.number in only_new_ids]


def load_previous_knowledge(file_path: Path):
    if not file_path.exists() or os.path.getsize(file_path) == 0:
        _LOGGER.info('No previous knowledge found for %s' % os.path.basename(file_path))
        return {}

    with open(file_path, 'r') as f:
        data = json.load(f)
    results = data['results']
    _LOGGER.info('Found previous %s knowledge of size %d' % (os.path.basename(file_path), len(results)))
    return results
    
def save_knowledge(file_path: Path, data):
    results = {'results': data}

    with open(file_path, 'w') as f:
        json.dump(results, f)
    _LOGGER.info('Saved new knowledge file %s of size %d' % (os.path.basename(file_path), len(data)))

def get_interactions(comments):
    interactions = {comment.user.login:0 for comment in comments}
    for comment in comments:
        #we count by the num of words in comment
        interactions[comment.user.login] += len(comment.body.split(' '))
    return interactions

def analyze_issue(issue: Issue, data):
    if issue.pull_request is not None:
        return #we analyze issues and prs differentely

    created_at = issue.created_at.timestamp()
    closed_at = issue.closed_at.timestamp()
    time_to_close = closed_at - created_at

    labels = [label.name for label in issue.get_labels()]

    data[issue.number] = {
        "created_by": issue.user.login,
        "created_at": created_at,
        "closed_by": issue.closed_by.login,
        "closed_at": closed_at,
        "labels": get_non_standalone_labels(labels),
        "time_to_close": time_to_close,
        "interactions": get_interactions(issue.get_comments()),
    }

    # TODO: think about saving comments
    # would it be valuable?


def issues_analysis(project: Repository, project_knowledge: Path):
    """Analysis of every closed issue in repository
    
    Arguments:
        project {Repository} -- currently the PyGithub lib is used because of its functionality
                                ogr unfortunatelly did not provide enough to properly analyze issues
        
        project_knowledge {Path} -- project directory where the issues knowledge will be stored
    """
    _LOGGER.info('-------------Issues (that are not PR) Analysis-------------')
    data_path = project_knowledge.joinpath('./issues.json')

    data = load_previous_knowledge(data_path)
    current_issues = [issue for issue in project.get_issues(state='closed') if issue.pull_request is None]
    new_issues = get_only_new_entities(data, current_issues)
    
    if len(new_issues) == 0:
        return

    for idx, issue in enumerate(new_issues, 1):
        _LOGGER.info("Analysing ISSUE no. %d/%d" % (idx, len(new_issues)))
        analyze_issue(issue, data)

    save_knowledge(data_path, data)


def analyze_pull_request(pull: PullRequest, results: Dict[str, Dict[str, Union[Optional[str], float]]]):
    """Analyse pull request and save its desired features to results."""
    commits = pull.commits
    # TODO: Use commits to extract information.
    # commits = [commit for commit in pull.get_commits()]

    created_at = pull.created_at.timestamp()
    closed_at = pull.closed_at.timestamp()

    # Get the review approvation if it exists
    # approvation = next((review for review in reviews if review.state == 'APPROVED'), None)
    # pr_approved = approvation.submitted_at.timestamp() if approvation is not None else None
    # pr_approved_by = pull.approved_by.name if approvation is not None else None
    # time_to_approve = pr_approved - created_at if approvation is not None else None

    merged_at = pull.merged_at.timestamp() if pull.merged_at is not None else None
    
    labels = [label.name for label in pull.get_labels()]

    results[str(pull.number)] = {
        "size": get_labeled_size(labels),
        "labels": get_non_standalone_labels(labels),
        "created_by": pull.user.login,
        "created_at": created_at,
        #"approved_at": pr_approved,
        #"approved_by": pr_approved_by,
        #"time_to_approve": time_to_approve,
        "closed_at": closed_at,
        "closed_by": pull.as_issue().closed_by.login,
        "time_to_close": closed_at - created_at,
        "merged_at": merged_at,
        "commits_number": commits, 
        "referenced_issues": get_referenced_issues(pull),
        "interactions" : get_interactions(pull.get_comments()),
    }

def pull_request_analysis(project: Repository, project_knowledge: Path):
    """Analysis of every closed pullrequest in repository
    
    Arguments:
        project {Repository} -- currently the PyGithub lib is used because of its functionality
                                ogr unfortunatelly did not provide enough to properly analyze issues
        
        project_knowledge {Path} -- project directory where the issues knowledge will be stored
    """
    _LOGGER.info('-------------Pull Requests Analysis (including its Reviews)-------------')

    pulls_data_path = project_knowledge.joinpath('./pull_requests.json')
    pullrevs_data_path = project_knowledge.joinpath('./pull_request_reviews.json')

    prev_pulls = load_previous_knowledge(pulls_data_path)
    prev_pullrevs = load_previous_knowledge(pullrevs_data_path)

    current_pulls = project.get_pulls(state='closed')
    new_pulls = get_only_new_entities(prev_pulls, current_pulls)

    if len(new_pulls) == 0:
        return

    for idx, pullrequest in enumerate(new_pulls, 1):
        _LOGGER.info("Analysing PULL REQUEST no. %d/%d" % (idx, len(new_pulls)))
        analyze_pull_request(pullrequest, prev_pulls)
        analyze_pull_request_reviews(pullrequest.get_reviews(), prev_pullrevs)

    save_knowledge(pulls_data_path, prev_pulls)
    save_knowledge(pullrevs_data_path, prev_pullrevs)


def analyze_pull_request_reviews(reviews: PullRequestReview, results):
    _LOGGER.info("  -num of reviews found: %d" % reviews.totalCount)
    
    for idx, review in enumerate(reviews, 1):
        _LOGGER.info("      -analysing review no. %d/%d" % (idx, reviews.totalCount))
        results[review.id] = {
            "author": review.user.name,
            "words_count": len(review.body.split(' ')),
            "submitted_at": review.submitted_at.timestamp(),
            "state": review.state,
        }


if __name__ == "__main__":
    if not PROJECTS:
        _LOGGER.warning("Please insert one project in PROJECTS variable.")

    path = Path.cwd().joinpath('./Bot_Knowledge')
    for project in PROJECTS:
        #extract_knowledge_from_repository(project=project)
        
        service, pygithub = connect_to_source(project=project)

        project_path = path.joinpath('./' + pygithub.full_name)

        git_project = service.get_project(repo=project[0], namespace=project[1])

        check_directory(project_path)
        
        issues_analysis(pygithub, project_path)
        pull_request_analysis(pygithub, project_path)