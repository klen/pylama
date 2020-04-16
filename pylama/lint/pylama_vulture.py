import sys

from vulture.core import Vulture, _parse_args

# Hack for Vulture =< 1.4
try:
    from vulture.core import ERROR_CODES
except ImportError:
    ERROR_CODES = {
        "attribute": "V101",
        "class": "V102",
        "function": "V103",
        "import": "V104",
        "property": "V105",
        "unreachable_code": "V201",
        "variable": "V106",
    }

from pylama.lint import Linter as BaseLinter


def _parse_params_as_args(path, params=None):
    if params is None:
        params = {}

    new_argv = ["vulture"]
    for key, value in params.items():
        new_argv.append("--{}={}".format(key, value))

    new_argv.append(path)

    old_argv = sys.argv
    sys.argv = new_argv
    parsed_args = _parse_args()
    sys.argv = old_argv

    return parsed_args


def _convert_vulture_item_to_pylama_item(item):
    error_code = ERROR_CODES[item.typ]

    return {
        "lnum": item.first_lineno,
        "type": "V",
        "number": error_code,
        "text": "{} {} ({}% confidence)".format(error_code,
                                                item.message,
                                                item.confidence)
    }


class Linter(BaseLinter):
    """vulture runner."""

    @staticmethod
    def run(path, code=None, params=None, **meta):
        """Check code with vulture.

        :return list: List of errors.
        """
        parsed_args = _parse_params_as_args(path, params)
        vulture = Vulture(
            verbose=parsed_args.verbose,
            ignore_names=parsed_args.ignore_names,
            ignore_decorators=parsed_args.ignore_decorators,
        )
        vulture.scavenge([path], exclude=parsed_args.exclude)

        unused_code_items = vulture.get_unused_code(
            min_confidence=parsed_args.min_confidence,
            sort_by_size=parsed_args.sort_by_size
        )
        result = []
        for item in unused_code_items:
            result.append(_convert_vulture_item_to_pylama_item(item))

        return result
