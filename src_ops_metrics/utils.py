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

"""General functions that can be reused."""

import logging
import os
from pathlib import Path

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_directory(knowledge_dir: Path):
    """Check if directory exists. If not, create one."""
    if not knowledge_dir.exists():
        _LOGGER.info(
            "No repo identified, creating new directory at %s" % knowledge_dir)
        os.makedirs(knowledge_dir)