# Copyright (C) 2020 Dominik Tuchyna
#
# This file is part of thoth-station/mi - Meta-information Indicators.
#
# thoth-station/mi - Meta-information Indicators is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thoth-station/mi - Meta-information Indicators is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with thoth-station/mi - Meta-information Indicators.  If not, see <http://www.gnu.org/licenses/>.

"""Commit entity."""

from typing import List

from voluptuous.schema_builder import Schema
from voluptuous import Any

from srcopsmetrics.entities import Entity

from pydriller import Repository
from pydriller import Commit as GitCommit


class GeneratorWrapper:
    """
    Wrapper for pydriller generator.

    Used for mi logger to print out progressbar of commit
    extraction.
    """

    def __init__(self, generator, length):
        """Initialize with traverse_commits() generator and its length."""
        self.generator = generator
        self.length = length

    def __len__(self):
        """Return generator length initialized from a duplicate generator."""
        return self.length

    def __iter__(self):
        """Iterate through pydriller generator."""
        return self.generator


class Commit(Entity):
    """Commit entity class."""

    entity_schema = Schema(
        {
            "pull_request": Any(None, int),
            "patch": Schema({str: Any(None, str)}),
            "author": str,
            "message": str,
            "date": int,
            "additions": int,
            "deletions": int,
        }
    )

    def analyse(self):
        """Override :func:`~Entity.analyse`."""
        length = len([c for c in self.get_raw_github_data()])
        return GeneratorWrapper(self.get_raw_github_data(), length)

    def store(self, commit: GitCommit):
        """Override :func:`~Entity.store`."""
        if commit.hash in self.previous_knowledge:
            return

        github_commit = self.repository.get_commit(commit.hash)
        pull_request_ids = [pr.number for pr in github_commit.get_pulls()]
        author_login = (github_commit.author.login if github_commit.author else github_commit.commit.author.name,)

        patches = {}
        for mod in commit.modified_files:
            changed_methods = [method.name for method in mod.changed_methods]
            patches[mod.filename] = {
                "type": mod.change_type,
                "changed_methods": changed_methods,
                "patch_added": mod.diff_parsed["added"],
                "patch_deleted": mod.diff_parsed["deleted"],
            }

        self.stored_entities[commit.hash] = {
            "pull_request": pull_request_ids,
            "author": author_login,
            "message": commit.msg,
            "date": commit.committer_date.timestamp(),
            "additions": commit.insertions,
            "deletions": commit.deletions,
            "files": commit.files,
        }

    def get_raw_github_data(self) -> List[GitCommit]:
        """Override :func:`~Entity.get_raw_github_data`."""
        return Repository(self.repository.clone_url).traverse_commits()
