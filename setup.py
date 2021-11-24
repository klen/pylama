#!/usr/bin/env python

"""Setup pylama installation."""

import pathlib

import pkg_resources
from setuptools import setup


def parse_requirements(path: str) -> "list[str]":
    with pathlib.Path(path).open() as requirements:
        return [str(req) for req in pkg_resources.parse_requirements(requirements)]


setup(
    install_requires=parse_requirements("requirements/requirements.txt"),
    extras_require={"tests": parse_requirements("requirements/requirements-tests.txt")},
)
