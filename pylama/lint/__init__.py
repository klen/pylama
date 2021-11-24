"""Custom module loader."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import Any, Dict, List, Optional, Type

from pkg_resources import iter_entry_points

LINTERS: Dict[str, Type[Linter]] = {}


class Linter(metaclass=ABCMeta):
    """Abstract class for linter plugin."""

    name: Optional[str] = None

    def __init_subclass__(cls) -> None:
        """Register subclasses."""
        if cls.name is not None:
            LINTERS[cls.name] = cls

    @staticmethod
    def allow(path: str) -> bool:
        """Check path is relevant for linter."""
        return path.endswith(".py")

    @abstractmethod
    def run(self, path: str, **meta) -> List[Dict[str, Any]]:
        """Not implemented."""
        raise NotImplementedError(__doc__)


# Import default linters
for _, name, _ in walk_packages([str(Path(__file__).parent)]):  # type: ignore
    try:
        import_module(f"{__name__}.{name}")
    except ImportError:
        pass

# Import installed linters
for entry in iter_entry_points("pylama.linter"):
    if entry.name not in LINTERS:
        try:
            LINTERS[entry.name] = entry.load()
        except ImportError:
            pass
