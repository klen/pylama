"""pydocstyle support."""

from typing import Any, Dict, List

from pydocstyle import ConventionChecker as PyDocChecker
from pydocstyle.violations import conventions

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Check pydocstyle errors."""

    name = "pydocstyle"

    def run(self, path: str, code: str = None, params=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Check code with pydocstyle."""
        if params is None:
            params = {}

        convention_codes = conventions.get(params.get('convention'))

        return [
            {
                "lnum": e.line,
                # Remove colon after error code ("D403: ..." => "D403 ...").
                "text": (
                    e.message[0:4] + e.message[5:] if e.message[4] == ":" else e.message
                ),
                "type": "D",
                "number": e.code,
            }
            for e in PyDocChecker().check_source(
                code, path,
                params.get("ignore_decorators"),
                params.get("ignore_inline_noqa", False),
            ) if convention_codes is None or e.code in convention_codes
        ]
