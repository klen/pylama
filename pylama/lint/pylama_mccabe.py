"""Code complexity checking."""
from argparse import ArgumentError

from mccabe import McCabeChecker

from pylama.context import RunContext
from pylama.lint import ArgumentParser
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Run complexity checking."""

    name = "mccabe"

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """Add --max-complexity option."""
        try:
            parser.add_argument(
                "--max-complexity", default=10, type=int, help="Max complexity threshold"
            )
        except ArgumentError:
            pass

    def run_check(self, ctx: RunContext):
        """Run Mccabe code checker."""
        params = ctx.get_params("mccabe")
        options = ctx.options
        if options:
            params.setdefault("max-complexity", options.max_complexity)

        McCabeChecker.max_complexity = int(params.get("max-complexity", 10))
        McCabeChecker._error_tmpl = "%r is too complex (%d)"
        number = McCabeChecker._code
        for lineno, offset, text, _ in McCabeChecker(ctx.ast, ctx.filename).run():
            ctx.push(
                col=offset + 1,
                lnum=lineno,
                number=number,
                text=text,
                type="C",
                source="mccabe",
            )


#  pylama:ignore=W0212
