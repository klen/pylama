"""Custom module loader."""
from __future__ import annotations

from argparse import ArgumentParser
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from pkg_resources import iter_entry_points

LINTERS: Dict[str, Type[LinterV2]] = {}

if TYPE_CHECKING:
    from pylama.context import RunContext


class LinterMeta(type):
    """Register linters."""

    def __new__(mcs, name, bases, params):
        """Register linters."""
        cls: Type[LinterV2] = super().__new__(mcs, name, bases, params)
        if cls.name is not None:
            LINTERS[cls.name] = cls
        return cls


class Linter(metaclass=LinterMeta):
    """Abstract class for linter plugin."""

    name: Optional[str] = None

    @classmethod
    def add_args(cls, _: ArgumentParser):
        """Add options from linters.

        The method has to be a classmethod.
        """

    def run(self, _path: str, **_meta) -> List[Dict[str, Any]]:  # noqa
        """Legacy method (support old extenstions)."""
        return []


class LinterV2(Linter):
    """A new linter class."""

    def run_check(self, ctx: RunContext):
        """Check code."""


# Import default linters
for _, pname, _ in walk_packages([str(Path(__file__).parent)]):  # type: ignore
    try:
        import_module(f"{__name__}.{pname}")
    except ImportError:
        pass

# Import installed linters
for entry in iter_entry_points("pylama.linter"):
    if entry.name not in LINTERS:
        try:
            LINTERS[entry.name] = entry.load()
        except ImportError:
            pass
