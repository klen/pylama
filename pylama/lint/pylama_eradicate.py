"""Commented-out code checking.

Support stdin.
"""

from typing import Any, Dict, List

from eradicate import Eradicator

from pylama.lint import Linter as Abstract
from pylama.utils import get_lines


class Linter(Abstract):
    """Run commented-out code checking."""

    name = "eradicate"

    def run(self, path: str, *, code: str = None, **_) -> List[Dict[str, Any]]:  # noqa
        """Eradicate code checking.

        TODO: Support params
        """
        if not code:
            return []

        eradicator = Eradicator()
        line_numbers = eradicator.commented_out_code_line_numbers(code)
        lines = get_lines(code)

        result = []
        for line_number in line_numbers:
            line = lines[line_number - 1]
            result.append(
                dict(
                    lnum=line_number,
                    offset=len(line) - len(line.rstrip()),
                    text=str("E800 Found commented out code: ") + line,
                    type="E800",
                )
            )
        return result
