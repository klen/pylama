""" Don't duplicate same errors from different linters. """
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Generator, List, Set, Tuple

PATTERN_NUMBER = re.compile(r"^\s*([A-Z]\d+)\s*", re.I)

DUPLICATES: Dict[Tuple[str, str], Set] = {
    key: values  # type: ignore
    for values in (
        # multiple statements on one line
        {("pycodestyle", "E701"), ("pylint", "C0321")},
        # unused variable
        {("pylint", "W0612"), ("pyflakes", "W0612")},
        # undefined variable
        {("pylint", "E0602"), ("pyflakes", "E0602")},
        # unused import
        {("pylint", "W0611"), ("pyflakes", "W0611")},
        # whitespace before ')'
        {("pylint", "C0326"), ("pycodestyle", "E202")},
        # whitespace before '('
        {("pylint", "C0326"), ("pycodestyle", "E211")},
        # multiple spaces after operator
        {("pylint", "C0326"), ("pycodestyle", "E222")},
        # missing whitespace around operator
        {("pylint", "C0326"), ("pycodestyle", "E225")},
        # unexpected spaces
        {("pylint", "C0326"), ("pycodestyle", "E251")},
        # long lines
        {("pylint", "C0301"), ("pycodestyle", "E501")},
        # statement ends with a semicolon
        {("pylint", "W0301"), ("pycodestyle", "E703")},
        # multiple statements on one line
        {('pylint", "C0321'), ("pycodestyle", "E702")},
        # bad indentation
        {("pylint", "W0311"), ("pycodestyle", "E111")},
        # wildcart import
        {("pylint", "W00401"), ("pyflakes", "W0401")},
        # module docstring
        {("pydocstyle", "D100"), ("pylint", "C0111")},
    )
    for key in values  # type: ignore
}


class Error:
    """Store an error's information."""

    __slots__ = "source", "col", "lnum", "etype", "message", "filename", "number"

    def __init__(
        self,
        source="pylama",
        col=1,
        lnum=1,
        type=None,  # pylint: disable=R0913
        text="unknown error",
        filename="",
        number="",
        **_,
    ):
        """Init error information with default values."""
        text = str(text).strip().replace("\n", " ")
        if number:
            self.number = number
        else:
            number = PATTERN_NUMBER.match(text)
            self.number = number.group(1).upper() if number else ""

        self.etype = type[:1] if type else (number[0] if number else "E")
        self.col = max(col, 1)
        self.filename = filename
        self.source = source
        self.lnum = int(lnum)
        self.message = text

    def __repr__(self):
        return f"<Error:{self.lnum}:{self.col}: {self.number} {self.message}>"

    def format(self, pattern: str) -> str:
        """Format the error with the given pattern."""
        return pattern.format(
            filename=self.filename,
            lnum=self.lnum,
            col=self.col,
            message=self.message,
            etype=self.etype,
            source=self.source,
            number=self.number,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return the error as a dict."""
        return {
            "source": self.source,
            "col": self.col,
            "lnum": self.lnum,
            "etype": self.etype,
            "message": self.message,
            "filename": self.filename,
            "number": self.number,
        }


def remove_duplicates(errors: List[Error]) -> Generator[Error, None, None]:
    """Filter duplicates from given error's list."""
    passed: DefaultDict[int, Set] = defaultdict(set)
    for error in errors:
        key = error.source, error.number
        if key in DUPLICATES:
            if key in passed[error.lnum]:
                continue
            passed[error.lnum] = DUPLICATES[key]
        yield error


def default_sorter(err: Error) -> Any:
    """Sort by line number."""
    return err.lnum


# pylama:ignore=W0622,D,R0924
