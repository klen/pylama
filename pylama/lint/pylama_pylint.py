"""Pylint integration to Pylama."""
import logging
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from typing import Dict

from pylint.interfaces import CONFIDENCE_LEVELS
from pylint.lint import Run
from pylint.reporters import BaseReporter

from pylama.context import RunContext
from pylama.lint import LinterV2 as BaseLinter

HOME_RCFILE = Path(environ.get("HOME", "")) / ".pylintrc"


logger = logging.getLogger("pylama")


class Linter(BaseLinter):
    """Check code with Pylint."""

    name = "pylint"

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """Add --max-complexity option."""
        parser.add_argument(
            "--pylint-confidence",
            choices=[cc.name for cc in CONFIDENCE_LEVELS],
            help="Only show warnings with the listed confidence levels.",
        )

    def run_check(self, ctx: RunContext):
        """Pylint code checking."""
        logger.debug("Start pylint")
        params = ctx.get_params("pylint")
        options = ctx.options
        if options:
            params.setdefault("max_line_length", options.max_line_length)
            params.setdefault("confidence", options.pylint_confidence)

        params.setdefault("enable", ctx.select | ctx.get_filter("pylint", "select"))
        params.setdefault("disable", ctx.ignore | ctx.get_filter("pylint", "ignore"))
        # if params.get("disable"):
        #     params["disable"].add("W0012")

        class Reporter(BaseReporter):
            """Handle messages."""

            def _display(self, _):
                pass

            def handle_message(self, msg):
                msg_id = msg.msg_id
                ctx.push(
                    filtrate=False,
                    col=msg.column + 1,
                    lnum=msg.line,
                    number=msg_id,
                    text=msg.msg,
                    type=msg_id[0],
                    source="pylint",
                )

        logger.debug(params)

        reporter = Reporter()
        args = _Params(params).to_attrs()
        Run([ctx.temp_filename] + args, reporter=reporter, exit=False)


class _Params:
    """Store pylint params."""

    def __init__(self, params: Dict):
        attrs = {
            name.replace("_", "-"): self.prepare_value(value)
            for name, value in params.items()
            if value
        }
        if HOME_RCFILE.exists():
            attrs["rcfile"] = HOME_RCFILE.as_posix()

        if attrs.get("disable"):
            attrs["disable"] += ",W0012"
        else:
            attrs["disable"] = "W0012"

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
