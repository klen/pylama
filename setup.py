#!/usr/bin/env python

"""Setup pylama installation."""

import re
import sys
from os import path as op
from io import open

from setuptools import setup, find_packages


_read = lambda f: open(
    op.join(op.dirname(__file__), f), encoding='utf-8').read() if op.exists(f) else ''

_meta = _read('pylama/__init__.py')
_license = re.search(r'^__license__\s*=\s*"(.*)"', _meta, re.M).group(1)
_project = re.search(r'^__project__\s*=\s*"(.*)"', _meta, re.M).group(1)
_version = re.search(r'^__version__\s*=\s*"(.*)"', _meta, re.M).group(1)

install_requires = [
    l.replace('==', '>=') for l in _read('requirements.txt').split('\n')
    if l and not l.startswith(('#', '-'))]

meta = dict(
    name=_project,
    version=_version,
    license=_license,
    description=_read('DESCRIPTION'),
    long_description=_read('README.rst'),
    platforms=('Any'),
    zip_safe=False,
    keywords='pylint pep8 pycodestyle pyflakes mccabe linter qa pep257 pydocstyle'.split(),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' https://github.com/klen/pylama',

    packages=find_packages(exclude=['plugins']),

    entry_points={
        'console_scripts': [
            'pylama = pylama.main:shell',
        ],
        'pytest11': ['pylama = pylama.pytest'],
    },

    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Code Generators',
    ],

    install_requires=install_requires,
)


if __name__ == "__main__":
    setup(**meta)
