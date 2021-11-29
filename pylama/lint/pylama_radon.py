"""Support Radon.

Supports stdin.
"""

from argparse import ArgumentError, ArgumentParser

from radon.complexity import add_inner_blocks
from radon.visitors import ComplexityVisitor

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """Radon runner."""

    name = "radon"

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """Add --max-complexity option."""
        parser.add_argument(
            "--radon-no-assert",
            default=False,
            action="store_true",
            help="Ignore `assert` statements.",
        )
        parser.add_argument(
            "--radon-show-closures",
            default=False,
            action="store_true",
            help="Increase complexity on closures.",
        )
        try:
            parser.add_argument(
                "--max-complexity",
                default=10,
                type=int,
                help="Max complexity threshold",
            )
        except ArgumentError:
            pass

    def run_check(self, ctx: RunContext):  # noqa  # noqa
        """Check code with Radon."""
        params = ctx.get_params("radon")
        options = ctx.options
        if options:
            params.setdefault("complexity", options.max_complexity)
            params.setdefault("no_assert", options.radon_no_assert)
            params.setdefault("show_closures", options.radon_show_closures)

        complexity = params.get("complexity", 10)
        no_assert = params.get("no_assert", False)
        show_closures = params.get("show_closures", False)
        visitor = ComplexityVisitor.from_code(ctx.source, no_assert=no_assert)
        blocks = visitor.blocks
        if show_closures:
            blocks = add_inner_blocks(blocks)
        for block in visitor.blocks:
            if block.complexity > complexity:
                ctx.push(
                    lnum=block.lineno,
                    col=block.col_offset + 1,
                    source="radon",
                    type="R",
                    number="R901",
                    text=f"{block.name} is too complex {block.complexity}",
                )
