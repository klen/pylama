"""Pylama TOML configuration."""

import toml

from pylama.libs.inirama import Namespace as _Namespace


class Namespace(_Namespace):
    """Inirama-style wrapper for TOML config."""

    def parse(self, source: str, update: bool = True, **params):
        """Parse TOML source as string."""
        content = toml.loads(source)
        tool = content.get("tool", {})
        pylama = tool.get("pylama", {})
        linters = pylama.pop("linter", {})
        files = pylama.pop("files", [])

        for name, value in pylama.items():
            self["pylama"][name] = value

        for linter, options in linters.items():
            for name, value in options.items():
                self[f"pylama:{linter}"][name] = value

        for file in files:
            path = file.pop("path", None)
            if path is None:
                continue
            for name, value in file.items():
                self[f"pylama:{path}"][name] = value
