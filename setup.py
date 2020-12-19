# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
from pathlib import Path
import re


# Load doc
with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

# Setup info
about = {}
with open(Path('./transpydata/__version__.py'), 'r', encoding='utf8') as f:
    exec(f.read(), about)

# Validate version (semantic versioning)
if (not about['__version__']
    or not re.match('\\d+\\.\\d+\\.\\d+', about['__version__'])):
    raise RuntimeError('Version not provided or incorrect format')

# Dependecies
requires = [
    'mysql-connector-python',
    'requests',
    'clinlog'
]
setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    install_requires=requires,
    license=about['__license__'],
    packages=find_packages(exclude=('tests', 'tests.*', 'assets', 'venv', 'examples'))
)
