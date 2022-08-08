""" py.test plugin for checking files with pylama. """
from __future__ import absolute_import

import pathlib
from os import path as op

import pytest

from pylama.config import CURDIR
from pylama.main import DEFAULT_FORMAT, check_paths, parse_options

HISTKEY = "pylama/mtimes"


def pytest_load_initial_conftests(early_config, *_):
    # Marks have to be registered before usage
    # to not fail with --strict command line argument
    early_config.addinivalue_line(
        "markers", "pycodestyle: Mark test as using pylama code audit tool."
    )


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        "--pylama",
        action="store_true",
        help="perform some pylama code checks on .py files",
    )


def pytest_sessionstart(session):
    config = session.config
    if config.option.pylama and getattr(config, "cache", None):
        config._pylamamtimes = config.cache.get(HISTKEY, {})


def pytest_sessionfinish(session):
    config = session.config
    if hasattr(config, "_pylamamtimes"):
        config.cache.set(HISTKEY, config._pylamamtimes)


def pytest_collect_file(path, parent):
    config = parent.config
    if config.option.pylama and path.ext == ".py":
        return PylamaFile.from_parent(parent, path=pathlib.Path(path))
    return None


class PylamaError(Exception):
    """indicates an error during pylama checks."""


class PylamaFile(pytest.File):
    def collect(self):
        return [PylamaItem.from_parent(self, name="pylama")]


class PylamaItem(pytest.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_marker("pycodestyle")
        self.cache = None
        self._pylamamtimes = None

    def setup(self):
        if not getattr(self.config, "cache", None):
            return False

        self.cache = True
        self._pylamamtimes = self.fspath.mtime()
        pylamamtimes = self.config._pylamamtimes
        old = pylamamtimes.get(str(self.fspath), 0)
        if old == self._pylamamtimes:
            pytest.skip("file(s) previously passed Pylama checks")

        return True

    def runtest(self):
        errors = check_file(self.fspath)
        if errors:
            out = "\n".join(err.format(DEFAULT_FORMAT) for err in errors)
            raise PylamaError(out)

        # update mtime only if test passed
        # otherwise failures would not be re-run next time
        if self.cache:
            self.config._pylamamtimes[str(self.fspath)] = self._pylamamtimes

    def repr_failure(self, excinfo, style=None):
        if excinfo.errisinstance(PylamaError):
            return excinfo.value.args[0]
        return super().repr_failure(excinfo, style)


def check_file(path):
    options = parse_options()
    path = op.relpath(str(path), CURDIR)
    return check_paths([path], options, rootdir=CURDIR)


# pylama:ignore=D,E1002,W0212,F0001,C0115,C0116
