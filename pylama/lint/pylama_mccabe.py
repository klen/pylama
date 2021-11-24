"""Code complexity checking."""
import ast
from typing import Dict, List, Any

from mccabe import McCabeChecker

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Run complexity checking."""

    name = "mccabe"

    def run(self, path: str, *, code: str = None, params=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Run Mccabe code checker."""
        if not code:
            return []

        if params is None:
            params = {}

        tree = compile(code, path, "exec", ast.PyCF_ONLY_AST)
        McCabeChecker.max_complexity = int(params.get("complexity", 10))
        return [
            {
                "lnum": lineno,
                "offset": offset,
                "text": text,
                "type": McCabeChecker._code,
            }
            for lineno, offset, text, _ in McCabeChecker(tree, path).run()
        ]


#  pylama:ignore=W0212
