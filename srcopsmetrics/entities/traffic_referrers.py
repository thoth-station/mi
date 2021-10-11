# Copyright (C) 2021 Dominik Tuchyna
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

"""Traffic Referrers stats class."""

from datetime import datetime

from srcopsmetrics.entities.traffic_paths import TrafficPaths


class TrafficReferrers(TrafficPaths):
    """Traffic Referrers entity."""

    def get_raw_github_data(self):
        """Override :func:`~Entity.get_raw_github_data`."""
        self.date_id = str(datetime.today())
        self.entry_key = "referrer"
        return self.repository.get_top_referrers()
