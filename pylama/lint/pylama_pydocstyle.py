"""pydocstyle support."""

from pydocstyle import PEP257Checker

from pylama.lint import Linter as Abstract


class Linter(Abstract):

    """Check pydocstyle errors."""

    @staticmethod
    def run(path, code=None, **meta):
        """pydocstyle code checking.

        :return list: List of errors.
        """
        return [
            {'lnum': e.line, 'text': e.message, 'type': 'D', 'number': e.code}
            for e in PEP257Checker().check_source(code, path)
        ]
