"""Manage resources."""

import ast
import os.path as op
import re
from argparse import Namespace
from copy import copy
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Dict, List, Set

from pylama.errors import Error
from pylama.utils import read

# Parse modeline
MODELINE_RE = re.compile(
    r"^\s*#\s+(?:pylama:)\s*((?:[\w_]*=[^:\n\s]+:?)+)", re.I | re.M
).search

SKIP_PATTERN = re.compile(r"# *noqa\b", re.I).search


class RunContext:  # pylint: disable=R0902
    """Manage resources."""

    __slots__ = (
        "errors",
        "options",
        "skip",
        "ignore",
        "select",
        "linters",
        "linters_params",
        "filename",
        "_ast",
        "_from_stdin",
        "_source",
        "_tempfile",
        "_lines",
    )

    def __init__(self, filename: str, source: str = None, options: Namespace = None):
        """Initialize the class."""
        self.errors: List[Error] = []
        self.options = options
        self.skip = False
        self.ignore = set()
        self.select = set()
        self.linters = []
        self.linters_params = {}

        self._ast = None
        self._from_stdin = source is not None
        self._source = source
        self._tempfile = None
        self._lines = None

        if options:
            if options.abspath:
                filename = op.abspath(filename)
            self.skip = options.skip and any(
                ptrn.match(filename) for ptrn in options.skip
            )
            self.linters.extend(options.linters)
            self.ignore |= options.ignore
            self.select |= options.select
            self.linters_params.update(options.linters_params)

            for mask in options.file_params:
                if mask.match(filename):
                    fparams = options.file_params[mask]
                    self.update_params(**fparams)

        self.filename = filename

        # Read/parse modeline
        if not self.skip:
            modeline = MODELINE_RE(self.source)
            if modeline:
                values = modeline.group(1).split(":")
                self.update_params(**dict(v.split("=", 1) for v in values))  # type: ignore

    def __enter__(self):
        """Enter to context."""
        return self

    def __exit__(self, etype, evalue, _):
        """Exit from the context."""
        if self._tempfile is not None:
            tmpfile = Path(self._tempfile)
            tmpfile.unlink()
            tmpfile.parent.rmdir()

        if evalue is not None:
            if etype is IOError:
                self.push(text=f"{evalue}", number="E001")
            elif etype is UnicodeDecodeError:
                self.push(text=f"UnicodeError: {self.filename}", number="E001")
            elif etype is SyntaxError:
                self.push(
                    lnum=evalue.lineno,
                    col=evalue.offset,
                    text=f"SyntaxError: {evalue.args[0]}",
                )
            else:
                self.push(lnum=1, col=1, text=str(evalue))
                return False

        return True

    @property
    def source(self):
        """Get the current source code."""
        if self._source is None:
            self._source = read(self.filename)
        return self._source

    @property
    def lines(self):
        """Split source to lines."""
        if self._lines is None:
            self._lines = self.source.splitlines(True)
        return self._lines

    @property
    def ast(self):
        """Get the AST for the source."""
        if self._ast is None:
            self._ast = compile(self.source, self.filename, "exec", ast.PyCF_ONLY_AST)
        return self._ast

    @property
    def temp_filename(self):
        """Get a filename for run external command."""
        if not self._from_stdin:
            return self.filename

        if self._tempfile is None:
            file = NamedTemporaryFile(  # noqa
                "w",
                encoding="utf8",
                suffix=".py",
                dir=mkdtemp(prefix="pylama_"),
                delete=False,
            )
            file.write(self.source)
            file.close()
            self._tempfile = file.name

        return self._tempfile

    def update_params(self, ignore=None, select=None, linters=None, skip=None, **_):
        """Update general params (from file configs or modeline)."""
        if select:
            self.select |= set(select.split(","))
        if ignore:
            self.ignore |= set(ignore.split(","))
        if linters:
            self.linters = linters.split(",")
        if skip is not None:
            self.skip = bool(int(skip))

    @lru_cache(42)
    def get_params(self, name: str) -> Dict:
        """Get params for a linter with the given name."""
        lparams = copy(self.linters_params.get(name, {}))
        for key in ("ignore", "select"):
            if key in lparams and not isinstance(lparams[key], set):
                lparams[key] = set(lparams[key].split(","))
        return lparams

    @lru_cache(42)
    def get_filter(self, name: str, key: str) -> Set:
        """Get select/ignore from linter params."""
        lparams = self.get_params(name)
        return lparams.get(key, set())

    def push(self, filtrate: bool = True, **params):
        """Record an error."""
        err = Error(filename=self.filename, **params)
        number = err.number

        if len(self.lines) >= err.lnum and SKIP_PATTERN(self.lines[err.lnum - 1]):
            return None

        if filtrate:

            for rule in self.select | self.get_filter(err.source, "select"):
                if number.startswith(rule):
                    return self.errors.append(err)

            for rule in self.ignore | self.get_filter(err.source, "ignore"):
                if number.startswith(rule):
                    return None

        return self.errors.append(err)
