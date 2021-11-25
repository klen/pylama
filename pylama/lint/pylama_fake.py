"""A fake linter which one never be loaded."""

from typing import Dict, List, Any

import unknown_module  # noqa

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Just a fake."""

    name = "fake"

    def run(self, path: str, **_) -> List[Dict[str, Any]]:
        """Run the unknown module."""
        return unknown_module.run(path)
