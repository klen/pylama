"""Pylama utils."""

from io import StringIO
from sys import stdin
from typing import List


def get_lines(value: str) -> List[str]:
    """Return lines from the given string."""
    return StringIO(value).readlines()


def read(filename: str) -> str:
    """Read the given filename."""
    with open(filename, encoding="utf-8") as file:
        return file.read()


def read_stdin() -> str:
    """Get value from stdin."""
    value = stdin.buffer.read()
    return value.decode("utf-8")
