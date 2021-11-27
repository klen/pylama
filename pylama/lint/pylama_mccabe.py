"""Code complexity checking."""
from mccabe import McCabeChecker

from pylama.lint import LinterV2 as Abstract
from pylama.context import RunContext


class Linter(Abstract):
    """Run complexity checking."""

    name = "mccabe"

    def run_check(self, ctx: RunContext):
        """Run Mccabe code checker."""
        params = ctx.get_params('mccabe')
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
