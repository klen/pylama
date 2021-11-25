"""MyPy support."""

from typing import Any, Dict, List
from mypy import api

from pylama.lint import Linter as Abstract


class _MyPyMessage:
    """Parser for a single MyPy output line."""

    types = {
        'error': 'E',
        'warning': 'W',
        'note': 'N'
    }

    valid = False

    def __init__(self, line):
        self.filename = None
        self.line_num = None
        self.column = None

        try:
            result = line.split(':', maxsplit=4)
            self.filename, line_num_txt, column_txt, self.message_type, text = result
        except ValueError:
            return

        try:
            self.line_num = int(line_num_txt.strip())
            self.column = int(column_txt.strip())
        except ValueError:
            return

        self.text = text.strip()
        self.valid = True

    def add_note(self, note):
        """Add in additional information about this message."""
        self.text = f"{self.text} - {note}"

    def to_result(self):
        """Convert to the Linter.run return value."""
        return {
            'lnum': self.line_num,
            'col': self.column,
            'text': self.text,
            'type': self.types.get(self.message_type.strip(), 'W')
        }


class Linter(Abstract):
    """MyPy runner."""

    name = 'mypy'

    def run(self, path, **_) -> List[Dict[str, Any]]:
        """Check code with mypy."""
        args = [path, '--follow-imports=skip', '--show-column-numbers']
        stdout, _, _ = api.run(args)    # noqa
        messages = []
        for line in stdout.split('\n'):
            if not line:
                continue
            message = _MyPyMessage(line)
            if message.valid:
                if message.message_type == 'note':
                    if messages[-1].line_num == message.line_num:
                        messages[-1].add_note(message.text)
                else:
                    messages.append(message)

        return [m.to_result() for m in messages]
