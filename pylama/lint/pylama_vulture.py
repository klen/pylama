"""Support Vulture."""
from argparse import ArgumentParser

from vulture.core import ERROR_CODES, Vulture, make_config

from pylama.context import RunContext
from pylama.lint import LinterV2 as BaseLinter


class Linter(BaseLinter):
    """vulture runner."""

    name = "vulture"

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """Add --max-complexity option."""
        parser.add_argument(
            "--vulture-min-confidence",
            type=int,
            help="Minimum confidence (between 0 and 100) for code to be reported as unused.",
        )
        parser.add_argument(
            "--vulture-ignore-names",
            help="Comma-separated list of names to ignore",
        )
        parser.add_argument(
            "--vulture-ignore-decorators",
            help="Comma-separated list of decorators to ignore",
        )

    def run_check(self, ctx: RunContext):  # noqa
        """Check code with vulture."""
        params = ctx.get_params("vulture")
        options = ctx.options
        if options:
            params.setdefault("min-confidence", options.vulture_min_confidence)
            params.setdefault("ignore-names", options.vulture_ignore_names)
            params.setdefault("ignore-decorators", options.vulture_ignore_decorators)

        config = make_config(parse_params(ctx.filename, params))
        vulture = Vulture(
            verbose=config["verbose"],
            ignore_names=config["ignore_names"],
            ignore_decorators=config["ignore_decorators"],
        )
        vulture.scan(ctx.source, filename=ctx.filename)
        unused_code_items = vulture.get_unused_code(
            min_confidence=config["min_confidence"], sort_by_size=config["sort_by_size"]
        )
        for item in unused_code_items:
            error_code = ERROR_CODES[item.typ]
            ctx.push(
                source="vulture",
                type="R",
                lnum=item.first_lineno,
                number=error_code,
                text=f"{item.message} ({item.confidence}% confidence)",
            )


def parse_params(path, params=None):
    """Convert params from pylama."""
    return [f"--{key}={value}" for key, value in params.items() if value] + [path]
