"""pydocstyle support."""

from pydocstyle import ConventionChecker as PyDocChecker
from pydocstyle.violations import conventions

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Check pydocstyle errors."""

    name = "pydocstyle"

    def run_check(self, ctx: RunContext):  # noqa
        """Check code with pydocstyle."""
        params = ctx.get_params("pydocstyle")
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
