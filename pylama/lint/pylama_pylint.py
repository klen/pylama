"""Pylint integration to Pylama."""
import logging
from os import environ
from pathlib import Path
from typing import Any, Dict, List

from pylint.lint import Run
from pylint.reporters import BaseReporter

from pylama.lint import Linter as BaseLinter

HOME_RCFILE = Path(environ.get("HOME", "")) / ".pylintrc"


logger = logging.getLogger("pylama")


class Linter(BaseLinter):
    """Check code with Pylint."""

    name = "pylint"

    def run(self, path, *, params=None, ignore=None, select=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Pylint code checking."""
        logger.debug("Start pylint")

        if params is None:
            params = {}

        class Reporter(BaseReporter):
            """Handle messages."""

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
        attrs = {
            name.replace("_", "-"): self.prepare_value(value)
            for name, value in params.items() if value is not None
        }
        if HOME_RCFILE.exists():
            attrs["rcfile"] = HOME_RCFILE.as_posix()

        if select:
            enable = attrs.get("enable", None)
            attrs["enable"] = select | set(enable.split(",") if enable else [])

        if ignore:
            disable = attrs.get("disable", None)
            attrs["disable"] = ignore | set(disable.split(",") if disable else [])

        self.attrs = attrs

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
        return [f"--{key}={value}" for key, value in self.attrs.items()]  # noqa

    def __str__(self):
        return " ".join(self.to_attrs())

    def __repr__(self):
        return f"<Pylint {self}>"


# pylama:ignore=W0403
