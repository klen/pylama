""" Don't duplicate same errors from different linters. """
from __future__ import annotations

import re
from collections import defaultdict
from typing import DefaultDict, Generator, List, Set


PATTERN_NUMBER = re.compile(r'^[A-Z]\d+$')

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


class Error:

    """ Store an error's information. """

    __slots__ = 'linter', 'col', 'lnum', 'type', 'text', 'filename', 'number'

    def __init__(self, linter="", col=1, lnum=1, type="E",
                 text="unknown error", filename="", number="", **_):
        """ Init error information with default values. """
        text = str(text).strip().replace('\n', ' ')
        if linter:
            text = f"{text} [{linter}]"
        number = number or text.split(' ', 1)[0]
        if not PATTERN_NUMBER.match(number):
            number = ""

        self.linter = linter
        self.col = col
        self.lnum = int(lnum)
        self.type = type[:1]
        self.text = text
        self.filename = filename
        self.number = number

    def __repr__(self):
        return f"<Error: {self.number} {self.linter}>"

# pylama:ignore=W0622,D,R0924
