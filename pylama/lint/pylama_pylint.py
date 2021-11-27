"""Pylint integration to Pylama."""
import logging
from os import environ
from pathlib import Path
from typing import Dict

from pylint.lint import Run
from pylint.reporters import BaseReporter

from pylama.context import RunContext
from pylama.lint import LinterV2 as BaseLinter

HOME_RCFILE = Path(environ.get("HOME", "")) / ".pylintrc"


logger = logging.getLogger("pylama")


class Linter(BaseLinter):
    """Check code with Pylint."""

    name = "pylint"

    def run_check(self, ctx: RunContext):
        """Pylint code checking."""
        logger.debug("Start pylint")
        params = ctx.get_params("pylint")

        class Reporter(BaseReporter):
            """Handle messages."""

            def _display(self, _):
                pass

            def handle_message(self, msg):
                msg_id = msg.msg_id
                ctx.push(
                    col=msg.column + 1,
                    lnum=msg.line,
                    number=msg_id,
                    text=msg.msg,
                    type=msg_id[0],
                    source="pylint",
                )

        params = _Params(params)
        logger.debug(params)

        reporter = Reporter()
        Run([ctx.temp_filename] + params.to_attrs(), reporter=reporter, exit=False)


class _Params:
    """Store pylint params."""

    def __init__(self, params: Dict):
        attrs = {
            name.replace("_", "-"): self.prepare_value(value)
            for name, value in params.items()
            if value is not None
        }
        if HOME_RCFILE.exists():
            attrs["rcfile"] = HOME_RCFILE.as_posix()

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
