"""pycodestyle support."""
from io import StringIO
from typing import Any, Dict, List

from pycodestyle import (BaseReport, StyleGuide, _parse_multi_options,
                         get_parser)

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """pycodestyle runner."""

    name = "pycodestyle"

    def run(self, path, code=None, params=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Check code with pycodestyle.

        :return list: List of errors.
        """
        if params is None:
            params = {}
        parser = get_parser()
        for option in parser.option_list:
            if option.dest and option.dest in params:
                value = params[option.dest]
                if isinstance(value, str):
                    params[option.dest] = option.convert_value(option, value)

        for key in ["filename", "exclude", "select", "ignore"]:
            if key in params and isinstance(params[key], str):
                params[key] = _parse_multi_options(params[key])

        checker = StyleGuide(reporter=_PycodestyleReport, **params)
        buf = StringIO(code)
        return checker.input_file(path, lines=buf.readlines())


class _PycodestyleReport(BaseReport):
    def __init__(self, *args, **kwargs):
        super(_PycodestyleReport, self).__init__(*args, **kwargs)
        self.errors = []

    def init_file(self, filename, lines, expected, line_offset):
        """Prepare storage for errors."""
        super(_PycodestyleReport, self).init_file(
            filename, lines, expected, line_offset
        )
        self.errors = []

    def error(self, line_number, offset, text, check):
        """Save errors."""
        code = super(_PycodestyleReport, self).error(line_number, offset, text, check)

        if code:
            self.errors.append(
                dict(
                    text=text,
                    type=code.replace("E", "C"),
                    col=offset + 1,
                    lnum=line_number,
                )
            )

    def get_file_results(self):
        """Get errors.

        :return list: List of errors.

        """
        return self.errors
