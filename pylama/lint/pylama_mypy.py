"""MyPy support.

TODO: Error codes
"""
from __future__ import annotations

from mypy import api

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """MyPy runner."""

    name = "mypy"

    def run_check(self, ctx: RunContext):
        """Check code with mypy."""
        # Support stdin
        args = [ctx.temp_filename, "--follow-imports=skip", "--show-column-numbers"]
        stdout, _, _ = api.run(args)  # noqa

        for line in stdout.splitlines():
            if not line:
                continue
            message = _MyPyMessage(line)
            if message.valid:
                ctx.push(
                    source="mypy",
                    lnum=message.line_num,
                    col=message.column,
                    text=message.text,
                    type=message.types.get(message.message_type.strip(), "W"),
                )


class _MyPyMessage:
    """Parser for a single MyPy output line."""

    types = {"error": "E", "warning": "W", "note": "N"}

    valid = False

    def __init__(self, line):
        self.filename = None
        self.line_num = None
        self.column = None

        try:
            result = line.split(":", maxsplit=4)
            self.filename, line_num_txt, column_txt, self.message_type, text = result
        except ValueError:
            return

        try:
            self.line_num = int(line_num_txt.strip())
            self.column = int(column_txt.strip())
        except ValueError:
            return

        self.text = text.strip()
        self.valid = True
