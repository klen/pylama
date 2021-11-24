"""A fake linter which one never be loaded."""

from typing import Dict, List

import unknown_module

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Just a fake."""

    name = "fake"

    @staticmethod
    def run(path: str, **_) -> List[Dict]:
        """Run the unknown module."""
        return unknown_module.run(path)
