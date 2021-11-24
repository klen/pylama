"""Pylint integration to Pylama."""
import logging
from os import environ
from pathlib import Path
from typing import Dict

from astroid import MANAGER
from pylint.lint import Run
from pylint.reporters import BaseReporter

from pylama.lint import Linter as BaseLinter

HOME_RCFILE = Path(environ.get("HOME", "")) / ".pylintrc"


logger = logging.getLogger("pylama")


class Linter(BaseLinter):
    """Check code with Pylint."""

    name = "pylint"

    @staticmethod
    def run(path, *, code=None, params=None, ignore=None, select=None, **_):
        """Pylint code checking."""
        logger.debug("Start pylint")

        if params is None:
            params = {}

        clear_cache = params.pop("clear_cache", False)
        if clear_cache:
            MANAGER.astroid_cache.clear()

        class Reporter(BaseReporter):
            def __init__(self):
                self.errors = []
                super().__init__()

            def _display(self, _):
                pass

            def handle_message(self, msg):
                self.errors.append(
                    dict(
                        lnum=msg.line,
                        col=msg.column,
                        text=f"{msg.msg_id} {msg.msg}",
                        type=msg.msg_id[0],
                    )
                )

        params = _Params(params, ignore=ignore, select=select)
        logger.debug(params)

        reporter = Reporter()
        Run([path] + params.to_attrs(), reporter=reporter, exit=False)
        return reporter.errors


class _Params:
    """Store pylint params."""

    def __init__(self, params: Dict,  select=None, ignore=None):
        if HOME_RCFILE.exists():
            params["rcfile"] = HOME_RCFILE.as_posix()

        if select:
            enable = params.get("enable", None)
            params["enable"] = select | set(enable.split(",") if enable else [])

        if ignore:
            disable = params.get("disable", None)
            params["disable"] = ignore | set(disable.split(",") if disable else [])

        self.params = dict(
            (name.replace("_", "-"), self.prepare_value(value))
            for name, value in params.items()
            if value is not None
        )

    @staticmethod
    def prepare_value(value):
        """Prepare value to pylint."""
        if isinstance(value, (list, tuple, set)):
            return ",".join(value)

        if isinstance(value, bool):
            return "y" if value else "n"

        return str(value)

    def to_attrs(self):
        """Convert to argument list."""
        return ["--%s=%s" % item for item in self.params.items()]  # noqa

    def __str__(self):
        return " ".join(self.to_attrs())

    def __repr__(self):
        return f"<Pylint {self}>"


# pylama:ignore=W0403
