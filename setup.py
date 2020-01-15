from setuptools import setup, find_packages
from pathlib import Path
import os


def get_version():
    with open(os.path.join('srcopsmetrics', '__init__.py')) as f:
        content = f.readlines()

    for line in content:
        if line.startswith('__version__ ='):
            return line.split(' = ')[1][1:-2]
    raise ValueError("No version identifier found")


VERSION = get_version()

setup(
    name='srcopsmetrics',
    version=VERSION,
    description='Source code metrics functionality for analysing python GitHub repositories',
    packages=find_packages(),
    long_description=Path('README.md').read_text(),
    author='Francesco Murdaca, Dominik Tuchyna',
    author_email='fmurdaca@redhat.com, xtuchyna@redhat.com',
    license='GPLv3+',
    url='https://github.com/AICoE/SrcOpsMetrics',
)