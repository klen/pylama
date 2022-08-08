"""Pyflakes support."""

from pyflakes import checker

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract

m = checker.messages
CODES = {
    m.UnusedImport.message: "W0611",
    m.RedefinedWhileUnused.message: "W0404",
    m.ImportShadowedByLoopVar.message: "W0621",
    m.ImportStarUsed.message: "W0401",
    m.ImportStarUsage.message: "W0401",
    m.UndefinedName.message: "E0602",
    m.DoctestSyntaxError.message: "W0511",
    m.UndefinedExport.message: "E0603",
    m.UndefinedLocal.message: "E0602",
    m.DuplicateArgument.message: "E1122",
    m.LateFutureImport.message: "W0410",
    m.UnusedVariable.message: "W0612",
    m.ReturnOutsideFunction.message: "E0104",
}

# RedefinedInListComp and ReturnWithArgsInsideGenerator were removed at pyflakes 2.5.0:
#   https://github.com/PyCQA/pyflakes/commit/2246217295dc8cb30ef4a7b9d8dc449ce32e603a
if hasattr(m, "RedefinedInListComp"):
    CODES[m.RedefinedInListComp.message] = "W0621"
if hasattr(m, "ReturnWithArgsInsideGenerator"):
    CODES[m.ReturnWithArgsInsideGenerator.message] = "E0106"


class Linter(Abstract):
    """Pyflakes runner."""

    name = "pyflakes"

    def run_check(self, context: RunContext):  # noqa
        """Check code with pyflakes."""
        params = context.get_params("pyflakes")
        builtins = params.get("builtins", "")
        if builtins:
            builtins = builtins.split(",")

        check = checker.Checker(context.ast, context.filename, builtins=builtins)
        for msg in check.messages:
            context.push(
                lnum=msg.lineno,
                col=msg.col + 1,
                text=msg.message % msg.message_args,
                number=CODES.get(msg.message, ""),
                source="pyflakes",
            )


#  pylama:ignore=E501,C0301
