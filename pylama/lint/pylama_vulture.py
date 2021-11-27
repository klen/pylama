"""Support Vulture."""
from vulture.core import ERROR_CODES, Vulture, make_config

from pylama.context import RunContext
from pylama.lint import LinterV2 as BaseLinter


def parse_params(path, params=None):
    """Convert params from pylama."""
    return ["vulture"] + [f"--{key}={value}" for key, value in params.items()] + [path]


class Linter(BaseLinter):
    """vulture runner."""

    name = "vulture"

    def run_check(self, context: RunContext):  # noqa
        """Check code with vulture."""
        config = make_config(
            parse_params(context.filename, context.get_params("vulture"))
        )
        vulture = Vulture(
            verbose=config["verbose"],
            ignore_names=config["ignore_names"],
            ignore_decorators=config["ignore_decorators"],
        )
        vulture.scan(context.source, filename=context.filename)
        unused_code_items = vulture.get_unused_code(
            min_confidence=config["min_confidence"], sort_by_size=config["sort_by_size"]
        )
        for item in unused_code_items:
            error_code = ERROR_CODES[item.typ]
            context.push(
                source="vulture",
                type="R",
                lnum=item.first_lineno,
                number=error_code,
                text=f"{item.message} ({item.confidence}% confidence)",
            )
