"""Commented-out code checking."""

from eradicate import Eradicator

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Run commented-out code checking."""

    name = "eradicate"

    def run_check(self, ctx: RunContext):
        """Eradicate code checking.

        TODO: Support params
        """
        eradicator = Eradicator()
        line_numbers = eradicator.commented_out_code_line_numbers(ctx.source)
        for line_number in line_numbers:
            ctx.push(
                lnum=line_number,
                source="eradicate",
                text=str("Found commented out code"),
                number="E800",
                type="E",
            )
