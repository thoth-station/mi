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

HERE = Path(__file__).parent
README: str = Path(HERE, "README.md").read_text(encoding="utf-8")

setup(
    name='srcopsmetrics',
    version=VERSION,
    twidescription='Source code metrics functionalities for analysing Python GitHub repositories',
    packages=find_packages(),
    long_description=README,
    long_description_content_type='text/markdown',
    author='Francesco Murdaca, Dominik Tuchyna',
    author_email='fmurdaca@redhat.com, xtuchyna@redhat.com',
    license='GPLv3+',
    url='https://github.com/AICoE/SrcOpsMetrics',
)