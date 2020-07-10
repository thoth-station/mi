#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2019, 2020 Francesco Murdaca, Dominik Tuchyna
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
import shutil

import numpy as np

from srcopsmetrics.enums import StoragePath

from typing import Tuple
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


def check_directory(knowledge_dir: Path):
    """Check if directory exists. If not, create one."""
    if not knowledge_dir.exists():
        _LOGGER.info("No repo identified, creating new directory at %s" % knowledge_dir)
        os.makedirs(knowledge_dir)


def remove_previously_processed(project_name: str):
    """Remove processed information for whole project."""
    print(project_name)
    path = Path(StoragePath.PROCESSED.value).joinpath(project_name)
    _LOGGER.info("Cleaning processed knowledge at %s" % project_name)
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


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
        _LOGGER.error("%s is not a recognized size.", label)
        _LOGGER.error("Returning zero as a score.")
        return 0


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
        _LOGGER.error("%s cannot be mapped, it's out of range [%f, %f]." % (score, 0.01, 0.9))

    return pull_request_size, assigned_score
