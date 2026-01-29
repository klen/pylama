#!/usr/bin/env python

"""Setup pylama installation."""

import pathlib

from setuptools import setup

OPTIONAL_LINTERS = ['pylint', 'eradicate', 'radon', 'mypy', 'vulture']


setup(
    install_requires=[
        'mccabe>=0.7.0',
        'pycodestyle>=2.9.1',
        'pydocstyle>=6.1.1',
        'pyflakes>=2.5.0'
    ],
    extras_require=dict(
        tests=[
            'pytest>=7.1.2',
            'pytest-mypy',
            'eradicate>=2.0.0',
            'radon>=5.1.0',
            'mypy',
            'pylint>=2.11.1',
            'pylama-quotes',
            'toml',
            'vulture',
            'types-setuptools',
            'types-toml'
        ],
        all=OPTIONAL_LINTERS, **{linter: [linter] for linter in OPTIONAL_LINTERS},
        toml="toml>=0.10.2",
    ),
)
