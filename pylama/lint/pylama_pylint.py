"""Pylint integration to Pylama."""
import logging
from os import path as op, environ

from astroid import MANAGER
from pylama.lint import Linter as BaseLinter
from pylint.__pkginfo__ import numversion
from pylint.lint import Run
from pylint.reporters import BaseReporter


CURDIR = op.abspath(op.dirname(__file__))
HOME_RCFILE = op.abspath(op.join(environ.get('HOME', ''), '.pylintrc'))
LAMA_RCFILE = op.abspath(op.join(CURDIR, 'pylint.rc'))


logger = logging.getLogger('pylama')


class Linter(BaseLinter):
    """Check code with Pylint."""

    @staticmethod
    def run(path, code, params=None, ignore=None, select=None, **meta):
        """Pylint code checking.

        :return list: List of errors.
        """
        logger.debug('Start pylint')

        clear_cache = params.pop('clear_cache', False)
        if clear_cache:
            MANAGER.astroid_cache.clear()

        class Reporter(BaseReporter):

            def __init__(self):
                self.errors = []
                super(Reporter, self).__init__()

            def _display(self, layout):
                pass

            def handle_message(self, msg):
                self.errors.append(dict(
                    lnum=msg.line,
                    col=msg.column,
                    text="%s %s" % (msg.msg_id, msg.msg),
                    type=msg.msg_id[0]
                ))

        params = _Params(ignore=ignore, select=select, params=params)
        logger.debug(params)

        reporter = Reporter()

        kwargs = {
            (numversion[0] == 1 and 'exit' or 'do_exit'): False
        }

        Run([path] + params.to_attrs(), reporter=reporter, **kwargs)

        return reporter.errors


class _Params(object):
    """Store pylint params."""

    def __init__(self, select=None, ignore=None, params=None):

        params = dict(params)

        if op.exists(HOME_RCFILE):
            params['rcfile'] = HOME_RCFILE

        if select:
            enable = params.get('enable', None)
            params['enable'] = select | set(enable.split(",") if enable else [])

        if ignore:
            disable = params.get('disable', None)
            params['disable'] = ignore | set(disable.split(",") if disable else [])

        self.params = dict(
            (name.replace('_', '-'), self.prepare_value(value))
            for name, value in params.items() if value is not None)

    @staticmethod
    def prepare_value(value):
        """Prepare value to pylint."""
        if isinstance(value, (list, tuple, set)):
            return ",".join(value)

        if isinstance(value, bool):
            return "y" if value else "n"

        return str(value)

    def to_attrs(self):
        """Convert to argument list."""
        return ["--%s=%s" % item for item in self.params.items()]

    def __str__(self):
        return " ".join(self.to_attrs())

    def __repr__(self):
        return "<Pylint %s>" % self

# pylama:ignore=W0403
