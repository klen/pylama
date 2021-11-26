""" Don't duplicate same errors from different linters. """
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Generator, List, Set, Collection


PATTERN_NUMBER = re.compile(r'^\s*([A-Z]\d+)\s*', re.I)

DUPLICATES = {key: values for values in (

    # multiple statements on one line
    {('pycodestyle', 'E701'), ('pylint', 'C0321')},

    # unused variable
    {('pylint', 'W0612'), ('pyflakes', 'W0612')},

    # undefined variable
    {('pylint', 'E0602'), ('pyflakes', 'E0602')},

    # unused import
    {('pylint', 'W0611'), ('pyflakes', 'W0611')},

    # whitespace before ')'
    {('pylint', 'C0326'), ('pycodestyle', 'E202')},

    # whitespace before '('
    {('pylint', 'C0326'), ('pycodestyle', 'E211')},

    # multiple spaces after operator
    {('pylint', 'C0326'), ('pycodestyle', 'E222')},

    # missing whitespace around operator
    {('pylint', 'C0326'), ('pycodestyle', 'E225')},

    # unexpected spaces
    {('pylint', 'C0326'), ('pycodestyle', 'E251')},

    # long lines
    {('pylint', 'C0301'), ('pycodestyle', 'E501')},

    # statement ends with a semicolon
    {('pylint', 'W0301'), ('pycodestyle', 'E703')},

    # multiple statements on one line
    {('pylint', 'C0321'), ('pycodestyle', 'E702')},

    # bad indentation
    {('pylint', 'W0311'), ('pycodestyle', 'E111')},

    # wildcart import
    {('pylint', 'W00401'), ('pyflakes', 'W0401')},

    # module docstring
    {('pydocstyle', 'D100'), ('pylint', 'C0111')},

) for key in values}


class Error:

    """ Store an error's information. """

    __slots__ = 'linter', 'col', 'lnum', 'type', 'text', 'filename', 'number'

    def __init__(self, linter="pylama", col=1, lnum=1, type="E",
                 text="unknown error", filename="", number="", **_):
        """ Init error information with default values. """
        text = str(text).strip().replace('\n', ' ')
        if number:
            self.number = number
        else:
            number = PATTERN_NUMBER.match(text)
            self.number = number.group(1).upper() if number else ""

        self.linter = linter
        self.col = col
        self.lnum = int(lnum)
        self.type = type[:1]
        self.text = text
        self.filename = filename

    def __repr__(self):
        return f"<Error: {self.text}>"

    def format(self, pattern: str) -> str:
        """Format the error with the given pattern."""
        return pattern.format(
            filename=self.filename,
            lnum=self.lnum,
            col=self.col,
            text=self.text,
            etype=self.type,
            linter=self.linter,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return the error as a dict."""
        return {
            'linter': self.linter,
            'col': self.col,
            'lnum': self.lnum,
            'etype': self.type,
            'text': self.text,
            'filename': self.filename,
        }


def remove_duplicates(errors: List[Error]) -> Generator[Error, None, None]:
    """ Filter duplicates from given error's list. """
    passed: DefaultDict[str, Set] = defaultdict(set)
    for error in errors:
        key = error.linter, error.number
        if key in DUPLICATES:
            if key in passed[error.lnum]:
                continue
            passed[error.lnum] = DUPLICATES[key]
        yield error


def filter_errors(
    errors: List[Error], select: Collection[str] = None, ignore: Collection[str] = None
) -> Generator[Error, None, None]:
    """Filter errors by select and ignore options."""
    select = select or []
    ignore = ignore or []

    for err in errors:
        number = err.number
        for rule in select:
            if number.startswith(rule):
                yield err
                break
        else:
            for rule in ignore:
                if number.startswith(rule):
                    break
            else:
                yield err


def default_sorter(err: Error) -> Any:
    """Sort by line number."""
    return err.lnum


# pylama:ignore=W0622,D,R0924
