#!/usr/bin/env python3
# thoth-storages
# Copyright(C) 2020 Francesco Murdaca
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

"""Exceptions for SrcOpsMetrics."""


class MissingPreviousKnowledge(Exception):
    """An exception when no previous knowledge has been extracted for a project."""


class NotKnownEntities(Exception):
    """An exception when Entities requested are not known."""

    def __init__(self, message, specified_entities, available_entities):
        """Initialize exception with user specified entities."""
        allowed = [e.__name__ for e in available_entities]
        unallowed = [e for e in specified_entities if e not in allowed]
        super().__init__("Invalid specified entities: %s", unallowed)
