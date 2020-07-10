# Copyright (C) 2020 Dominik Tuchyna, Francesco Murdaca
#
# This file is part of the thoth-station/mi project.
#
# SrcOpsMetrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SrcOpsMetrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SrcOpsMetrics.  If not, see <http://www.gnu.org/licenses/>.

"""Meta-information Indicators project is a usable python module."""

from setuptools import setup, find_packages
from pathlib import Path
import os


def get_version():
    """Get the version of the MI."""
    with open(os.path.join("srcopsmetrics", "__init__.py")) as f:
        content = f.readlines()

    for line in content:
        if line.startswith("__version__ ="):
            return line.split(" = ")[1][1:-2]
    raise ValueError("No version identifier found")


VERSION = get_version()

HERE = Path(__file__).parent
README: str = Path(HERE, "README.rst").read_text(encoding="utf-8")

setup(
    name="srcopsmetrics",
    version=VERSION,
    twidescription="Source code metrics functionalities for analysing Python GitHub repositories",
    packages=find_packages(),
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Francesco Murdaca, Dominik Tuchyna",
    author_email="fmurdaca@redhat.com, xtuchyna@redhat.com",
    license="GPLv3+",
    url="https://github.com/AICoE/SrcOpsMetrics",
)
