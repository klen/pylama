import os.path as op
import sys
import _ast

from .. import Linter as BaseLinter


class Linter(BaseLinter):

    def __init__(self):
        """ Update python paths. """
        try:
            from frosted import checker
        except ImportError:
            path = op.dirname(op.abspath( __file__ ))
            sys.path.insert(0, path)
            from pies.version_info import PY2
            if PY2:
                sys.path.insert(0, op.join(path, 'pies2overrides'))

    @staticmethod
    def run(path, code=None, **meta):
        """ Frosted code checking.

        :return list: List of errors.

        """
        tree = compile(code, path, "exec", _ast.PyCF_ONLY_AST)

        from frosted import checker

        cc = checker.Checker(tree, path, None, **meta)
        errors = []
        for mm in cc.messages:
            _, text = mm.message.split(' ', 1)
            text = mm.type.error_code + ' ' + text
            errors.append(dict(
                lnum=mm.lineno, col=mm.col, text=text, type=text[0]))
        return errors
