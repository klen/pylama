"""Commented-out code checking."""

from typing import List, Dict, Any

from eradicate import Eradicator
from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Run commented-out code checking."""

    name = 'eradicate'

    def run(self, path: str, *, code: str = None, **_) -> List[Dict[str, Any]]:  # noqa
        """Eradicate code checking.

        TODO: Support params
        """
        if not code:
            return []

        eradicator = Eradicator()
        line_numbers = eradicator.commented_out_code_line_numbers(code)
        lines = code.split('\n')

        result = []
        for line_number in line_numbers:
            line = lines[line_number - 1]
            result.append(dict(
                lnum=line_number,
                offset=len(line) - len(line.rstrip()),
                text=str('E800 Found commented out code: ') + line,
                type='E800',
            ))
        return result
