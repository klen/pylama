"""MyPy support."""

from mypy import api

from pylama.lint import Linter as Abstract


class _MyPyMessage(object):
    """Parser for a single MyPy output line."""
    types = {
        'error': 'E',
        'warning': 'W',
        'note': 'N'
    }

    def __init__(self, line):
        self.filename = None
        self.line_num = None
        self.column = None
        self.text = None
        self.note = None
        self.message_type = None
        self.valid = False

        self._parse(line)

    def _parse(self, line):
        """Parse the output line"""
        try:
            result = line.split(':', maxsplit=4)
            filename, line_num_txt, column_txt, message_type, text = result
        except ValueError:
            return

        try:
            self.line_num = int(line_num_txt.strip())
            self.column = int(column_txt.strip())
        except ValueError:
            return

        self.filename = filename
        self.message_type = message_type.strip()
        self.text = text.strip()
        self.valid = True

    def add_note(self, note):
        """Add in additional information about this message"""
        self.note = note

    def to_result(self):
        """Convert to the Linter.run return value"""
        text = [self.text]
        if self.note:
            text.append(self.note)

        return {
            'lnum': self.line_num,
            'col': self.column,
            'text': ' - '.join(text),
            'type': self.types.get(self.message_type, '')
        }


class Linter(Abstract):
    """MyPy runner."""

    @staticmethod
    def run(path, code=None, params=None, **meta):
        """Check code with mypy.

        :return list: List of errors.
        """
        args = [path, '--follow-imports=skip', '--show-column-numbers']
        stdout, stderr, status = api.run(args)
        messages = []
        for line in stdout.split('\n'):
            line.strip()
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
