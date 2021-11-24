"""Pyflakes support."""

import ast
from typing import Any, Dict, List
from pyflakes import checker

from pylama.lint import Linter as Abstract


# Path pyflakes messages
m = checker.messages
m.UnusedImport.message = f"W0611 {m.UnusedImport.message}"
m.RedefinedWhileUnused.message = f"W0404 {m.RedefinedWhileUnused.message}"
m.RedefinedInListComp.message = f"W0621 {m.RedefinedInListComp}"
m.ImportShadowedByLoopVar.message = f"W0621 {m.ImportShadowedByLoopVar}"
m.ImportStarUsed.message = f"W0401 {m.ImportStarUsed.message}"
m.ImportStarUsage.message = f"W0401 {m.ImportStarUsage.message}"
m.UndefinedName.message = f"E0602 {m.UndefinedName.message}"
m.DoctestSyntaxError.message = f"W0511 {m.DoctestSyntaxError.message}"
m.UndefinedExport.message = f"E0603 {m.UndefinedExport.message}"
m.UndefinedLocal.message = f"E0602 {m.UndefinedLocal.message}"
m.DuplicateArgument.message = f"E1122 {m.DuplicateArgument.message}"
m.LateFutureImport.message = f"W0410 {m.LateFutureImport.message}"
m.UnusedVariable.message = f"W0612 {m.UnusedVariable.message}"
m.ReturnWithArgsInsideGenerator.message = f"E0106 {m.ReturnWithArgsInsideGenerator.message}"
m.ReturnOutsideFunction.message = f"E0104 {m.ReturnOutsideFunction.message}"


class Linter(Abstract):
    """Pyflakes runner."""

    name = 'pyflakes'

    def run(self, path, *, code=None, params=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Check code with pyflakes."""
        if params is None:
            params = {}

        builtins = params.get("builtins", "")
        if builtins:
            builtins = builtins.split(",")

        tree = compile(code, path, "exec", ast.PyCF_ONLY_AST)
        check = checker.Checker(tree, path, builtins=builtins)
        return [{
            'lnum': msg.lineno,
            'text': msg.message % msg.message_args,
            'type': msg.message[0]
        } for msg in check.messages]

#  pylama:ignore=E501,C0301
