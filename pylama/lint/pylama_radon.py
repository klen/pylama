"""Support Radon.

Supports stdin.
"""

from radon.complexity import add_inner_blocks
from radon.visitors import ComplexityVisitor

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Radon runner."""

    name = "radon"

    def run_check(self, context: RunContext):  # noqa  # noqa
        """Check code with Radon."""
        params = context.get_params("radon")
        complexity = params.get("complexity", 10)
        no_assert = params.get("no_assert", False)
        show_closures = params.get("show_closures", False)
        visitor = ComplexityVisitor.from_code(context.source, no_assert=no_assert)
        blocks = visitor.blocks
        if show_closures:
            blocks = add_inner_blocks(blocks)
        for block in visitor.blocks:
            if block.complexity > complexity:
                context.push(
                    lnum=block.lineno,
                    col=block.col_offset + 1,
                    source="radon",
                    type="R",
                    number="R901",
                    text=f"{block.name} is too complex {block.complexity}",
                )
