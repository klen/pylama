"""Commented-out code checking."""
from eradicate import commented_out_code_line_numbers
from pylama.lint import Linter as Abstract

try:
    converter = unicode
except NameError:
    converter = str


class Linter(Abstract):

    """Run commented-out code checking."""

    @staticmethod
    def run(path, code=None, params=None, **meta):
        """Eradicate code checking.

        :return list: List of errors.
        """
        code = converter(code)
        line_numbers = commented_out_code_line_numbers(code)
        lines = code.split('\n')

        result = []
        for line_number in line_numbers:
            line = lines[line_number - 1]
            result.append(dict(
                lnum=line_number,
                offset=len(line) - len(line.rstrip()),
                # https://github.com/sobolevn/flake8-eradicate#output-example
                text=converter('E800: Found commented out code: ') + line,
                # https://github.com/sobolevn/flake8-eradicate#error-codes
                type='E800',
            ))
        return result
