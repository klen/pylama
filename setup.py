#!/usr/bin/env python

"""Setup pylama installation."""

import pathlib

import pkg_resources
from setuptools import setup


def parse_requirements(path: str) -> "list[str]":
    with pathlib.Path(path).open(encoding='utf-8') as requirements:
        return [str(req) for req in pkg_resources.parse_requirements(requirements)]


OPTIONAL_LINTERS = ['pylint', 'eradicate', 'radon', 'mypy', 'vulture']


setup(
    install_requires=parse_requirements("requirements/requirements.txt"),
    extras_require=dict(
        tests=parse_requirements("requirements/requirements-tests.txt"),
        all=OPTIONAL_LINTERS, **{linter: [linter] for linter in OPTIONAL_LINTERS}
    ),
)
