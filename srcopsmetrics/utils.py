#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019, 2020 Francesco Murdaca
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

"""General functions that can be reused for SrcOpsMetrics analysis."""

import logging
import os

import numpy as np

from typing import Tuple, Dict, Any, List, Optional
from pathlib import Path

from github import Github
import time
from datetime import datetime

_LOGGER = logging.getLogger(__name__)
API_RATE_MINIMAL_REMAINING = 20


class Knowledge:
    """Context manager for entity extraction process."""

    def __init__(self, entity_type, new_entities, accumulator, store_method):
        """Initialize with previous and new knowledge of an entity."""
        self.entity_type = entity_type
        self.new_entities = new_entities
        self.accumulator = accumulator
        self.store_method = store_method

    def __enter__(self):
        """Context manager enter method."""
        return self

    def __exit__(self, type, value, traceback):
        """Context manager exit method."""
        _LOGGER.info(
            "Something wrong went during the process of analysing, saving current state of work.")
        return self.accumulator

    def store(self):
        """Iterate through entities of given repository and accumulate them."""
        for idx, entity in enumerate(self.new_entities, 1):
            github = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
            remaining = github.rate_limiting[0]

            if remaining <= API_RATE_MINIMAL_REMAINING:
                wait_time = github.rate_limiting_resettime - \
                    int(datetime.now().timestamp())
                _LOGGER.info(
                    "API rate limit REACHED, will now wait for %d minutes" % (wait_time // 60))
                time.sleep(wait_time)

            if idx % 10 == 0:
                _LOGGER.info("[ API requests remaining: %d ]" % remaining)

            _LOGGER.info("Analysing %s no. %d/%d" %
                         (self.entity_type, idx, len(self.new_entities)))

            self.store_method(entity, self.accumulator)
        return self.accumulator


def check_directory(knowledge_dir: Path):
    """Check if directory exists. If not, create one."""
    if not knowledge_dir.exists():
        _LOGGER.info(
            "No repo identified, creating new directory at %s" % knowledge_dir)
        os.makedirs(knowledge_dir)


def assign_pull_request_size(lines_changes: int) -> str:
    """Assign size of PR is label is not provided."""
    if lines_changes > 1000:
        return "XXL"
    elif lines_changes >= 500 and lines_changes <= 999:
        return "XL"
    elif lines_changes >= 100 and lines_changes <= 499:
        return "L"
    elif lines_changes >= 30 and lines_changes <= 99:
        return "M"
    elif lines_changes >= 10 and lines_changes <= 29:
        return "S"
    elif lines_changes >= 0 and lines_changes <= 9:
        return "XS"


def convert_score2num(label: str) -> float:
    """Convert label string to numerical value."""
    if label == "XXL":
        return 1
    # lines_changes > 1000:
    elif label == "XL":
        return 0.7
    # lines_changes >= 500 and lines_changes <= 999:
    elif label == "L":
        return 0.4
    # lines_changes >= 100 and lines_changes <= 499:
    elif label == "M":
        return 0.09
    # lines_changes >= 30 and lines_changes <= 99:
    elif label == "S":
        return 0.02
    # lines_changes >= 10 and lines_changes <= 29:
    elif label == "XS":
        return 0.01
    # lines_changes >= 0 and lines_changes <= 9:
    else:
        _LOGGER.error("%s is not a recognized size" % label)


def convert_num2label(score: float) -> Tuple[str, float]:
    """Convert PR length to string label."""
    if score > 0.9:
        pull_request_size = "XXL"
        # lines_changes > 1000:
        assigned_score = 0.9

    elif score > 0.7 and score < 0.9:
        pull_request_size = "XL"
        # lines_changes >= 500 and lines_changes <= 999:
        assigned_score = np.mean([0.7, 0.9])

    elif score >= 0.4 and score < 0.7:
        pull_request_size = "L"
        # lines_changes >= 100 and lines_changes <= 499:
        assigned_score = np.mean([0.4, 0.7])

    elif score >= 0.09 and score < 0.4:
        pull_request_size = "M"
        # lines_changes >= 30 and lines_changes <= 99:
        assigned_score = np.mean([0.09, 0.4])

    elif score >= 0.02 and score < 0.09:
        pull_request_size = "S"
        # lines_changes >= 10 and lines_changes <= 29:
        assigned_score = np.mean([0.02, 0.09])

    elif score >= 0.01 and score < 0.02:
        pull_request_size = "XS"
        # lines_changes >= 0 and lines_changes <= 9:
        assigned_score = np.mean([0.01, 0.02])

    else:
        _LOGGER.error("%s cannot be mapped, it's out of range [%f, %f]" % (
            score,
            0.01,
            0.9
        )
        )

    return pull_request_size, assigned_score
