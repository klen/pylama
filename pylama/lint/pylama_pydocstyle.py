"""pydocstyle support."""

from argparse import ArgumentParser

from pydocstyle import ConventionChecker as PyDocChecker
from pydocstyle.violations import conventions

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Check pydocstyle errors."""

    name = "pydocstyle"

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """Add --max-complexity option."""
        parser.add_argument(
            "--pydocstyle-convention",
            choices=list(conventions.keys()),
            help="choose the basic list of checked errors by specifying an existing convention.",
        )

    def run_check(self, ctx: RunContext):  # noqa
        """Check code with pydocstyle."""
        params = ctx.get_params("pydocstyle")
        options = ctx.options
        if options and options.pydocstyle_convention:
            params.setdefault("convention", options.pydocstyle_convention)
        convention_codes = conventions.get(params.get("convention"))
        for err in PyDocChecker().check_source(
            ctx.source,
            ctx.filename,
            params.get("ignore_decorators"),
            params.get("ignore_inline_noqa", False),
        ):
            if convention_codes is None or err.code in convention_codes:
                ctx.push(
                    lnum=err.line,
                    text=err.short_desc,
                    type="D",
                    number=err.code,
                    source="pydocstyle",
                )
