#!/usr/bin/env python3
# SrcOpsMetrics
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

"""Enum types used in SrcOpsMetrics code."""

from enum import Enum


class EntityTypeEnum(Enum):
    """Class for the entity type to be collected."""

    PULL_REQUEST = "PullRequest"
    ISSUE = "Issue"
    CONTENT_FILE = "ContentFile"


class DeveloperActionEnum(Enum):
    """Class for the developer action on an entity type."""

    OPEN = "Open"
    CLOSE = "Close"


class StatisticalQuantityEnum(Enum):
    """Class for the statistical quantities to be used for data manipulation."""

    AVERAGE = "Average"
    MEDIAN = "Median"


class StoragePath(Enum):
    """Enum with predefined storage locations."""

    DEFAULT = "./srcopsmetrics/"
    LOCATION_VAR = "KNOWLEDGE_PATH"
    KNOWLEDGE = "bot_knowledge"
    PROCESSED = "processed"

    KNOWLEDGE_PATH = DEFAULT + KNOWLEDGE
    PROCESSED_PATH = DEFAULT + PROCESSED
