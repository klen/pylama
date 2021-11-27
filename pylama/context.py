"""Manage resources."""

import ast
import os.path as op
import re
from argparse import Namespace
from os import remove
from tempfile import NamedTemporaryFile
from typing import Dict, Set
from functools import lru_cache

from pylama.errors import Error
from pylama.utils import read

# Parse modeline
MODELINE_RE = re.compile(
    r"^\s*#\s+(?:pylama:)\s*((?:[\w_]*=[^:\n\s]+:?)+)", re.I | re.M
).search

SKIP_PATTERN = re.compile(r"# *noqa\b", re.I).search


class RunContext:
    """Manage resources."""

    linters_params = {}

    def __init__(self, filename: str, source: str = None, options: Namespace = None):
        """Initialize the class."""
        self.skip = False
        self.errors = []
        self.ignore = set()
        self.select = set()
        self.linters = None

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
            self.linters = options.linters
            self.ignore = options.ignore
            self.select = options.select
            self.linters_params = options.linters_params

            for mask in options.file_params:
                if mask.match(filename):
                    fparams = options.file_params[mask]
                    self.update_params(**fparams)

        self.filename = filename

        # Read/parse modeline
        if not self.skip:
            modeline = MODELINE_RE(self.source)
            if modeline:
                self.update_params(
                    **dict(v.split("=", 1) for v in modeline.group(1).split(":"))
                )

    def __enter__(self):
        """Enter to context."""
        return self

    def __exit__(self, etype, evalue, tb):  # noqa
        """Exit from the context."""
        if self._tempfile is not None:
            remove(self._tempfile)

        if evalue is not None:
            if etype is IOError:
                self.push(text=f"E001 {evalue}", number="E001")
            elif etype is UnicodeDecodeError:
                self.push(text=f"E001 UnicodeError: {self.filename}", number="E001")
            elif etype is SyntaxError:
                self.push(
                    lnum=evalue.lineno,
                    col=evalue.offset,
                    text=f"E0100 SyntaxError: {evalue.args[0]}",
                )

        return self

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
            file = NamedTemporaryFile("w", encoding="utf8", suffix=".py", delete=False)  # noqa
            file.write(self.source)
            file.close()
            self._tempfile = file.name

        return self._tempfile

    def update_params(self, ignore=None, select=None, linters=None, skip=None, **_):
        """Update general params (from file configs or modeline)."""
        if select:
            self.select |= set(select.split(','))
        if ignore:
            self.ignore |= set(ignore.split(','))
        if linters:
            self.linters = linters.split(',')
        if skip is not None:
            self.skip = bool(int(skip))

    @lru_cache
    def get_params(self, name: str) -> Dict:
        """Get params for a linter with the given name."""
        lparams = self.linters_params.get(name, {})
        for key in ('ignore', 'select'):
            if key in lparams:
                lparams[key] = set(lparams[key].split(','))
        return lparams

    @lru_cache
    def get_filter(self, name: str, key: str) -> Set:
        """Get select/ignore from linter params."""
        lparams = self.get_params(name)
        return lparams.get(key, set())

    def push(self, **params):
        """Record an error."""
        err = Error(filename=self.filename, **params)
        number = err.number

        for rule in self.select | self.get_filter(err.source, 'select'):
            if number.startswith(rule):
                return self.errors.append(err)

        for rule in self.ignore | self.get_filter(err.source, 'ignore'):
            if number.startswith(rule):
                return None

        if SKIP_PATTERN(self.lines[err.lnum - 1]):
            return None

        return self.errors.append(err)