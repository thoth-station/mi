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

"""General functions that can be reused for SrcOpsMetrics analysis."""

import logging
import os

import numpy as np

from typing import Tuple, Dict, Any, List
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


def check_directory(knowledge_dir: Path):
    """Check if directory exists. If not, create one."""
    if not knowledge_dir.exists():
        _LOGGER.info(
            "No repo identified, creating new directory at %s" % knowledge_dir)
        os.makedirs(knowledge_dir)


def convert_score2num(label: str) -> int:
    """Convert label string to numerical value."""
    if label == "XXL":
        return 1
    # lines_changes > 1000:
    #     return "size/XXL"
    elif label == "XL":
        return 0.7
    # elif lines_changes >= 500 and lines_changes <= 999:
    #     return "size/XL"
    elif label == "L":
        return 0.4
    # elif lines_changes >= 100 and lines_changes <= 499:
    #     return "size/L"
    elif label == "M":
        return 0.09
    # elif lines_changes >= 30 and lines_changes <= 99:
    #     return "size/M"
    elif label == "S":
        return 0.02
    # elif lines_changes >= 10 and lines_changes <= 29:
    #     return "size/S"
    elif label == "XS":
        return 0.01
    # elif lines_changes >= 0 and lines_changes <= 9:
    #     return "size/XS"
    else:
        _LOGGER.error("%s is not a recognized size" % label)


def convert_num2label(score: float) -> str:
    """Convert PR length to string label."""
    if score > 0.9:
        pull_request_size = "XXL"
        # lines_changes > 1000:
        #     return "size/XXL"
        assigned_score = 0.9

    elif score > 0.7 and score < 0.9:
        pull_request_size = "XL"
        # elif lines_changes >= 500 and lines_changes <= 999:
        #     return "size/XL"
        assigned_score = np.mean([0.7, 0.9])

    elif score >= 0.4 and score < 0.7:
        pull_request_size = "L"
        # elif lines_changes >= 100 and lines_changes <= 499:
        #     return "size/L"
        assigned_score = np.mean([0.4, 0.7])

    elif score >= 0.09 and score < 0.4:
        pull_request_size = "M"
        # elif lines_changes >= 30 and lines_changes <= 99:
        #     return "size/M"
        assigned_score = np.mean([0.09, 0.4])

    elif score >= 0.02 and score < 0.09:
        pull_request_size = "S"
        # elif lines_changes >= 10 and lines_changes <= 29:
        #     return "size/S"
        assigned_score = np.mean([0.02, 0.09])

    elif score >= 0.01 and score < 0.02:
        pull_request_size = "XS"
        # elif lines_changes >= 0 and lines_changes <= 9:
        #     return "size/XS"
        assigned_score = np.mean([0.01, 0.02])

    else:
        _LOGGER.error("%s cannot be mapped, it's out of range [%f, %f]" % (
            score,
            0.01,
            0.9
            )
            )

    return pull_request_size, assigned_score