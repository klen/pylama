"""Support Vulture."""
from typing import Any, Dict, List

from vulture.core import Vulture, make_config, ERROR_CODES

from pylama.lint import Linter as BaseLinter


def parse_params(path, params=None):
    """Convert params from pylama."""
    return ['vulture'] + [f"--{key}={value}" for key, value in params.items()] + [path]


class Linter(BaseLinter):
    """vulture runner."""

    name = 'vulture'

    def run(self, path: str, *, params=None, **_) -> List[Dict[str, Any]]:  # noqa
        """Check code with vulture."""
        config = make_config(parse_params(path, params or {}))

        vulture = Vulture(
            verbose=config['verbose'],
            ignore_names=config['ignore_names'],
            ignore_decorators=config['ignore_decorators'],
        )
        vulture.scavenge([path], exclude=config['exclude'])
        unused_code_items = vulture.get_unused_code(
            min_confidence=config['min_confidence'],
            sort_by_size=config['sort_by_size']
        )
        result = []
        for item in unused_code_items:
            error_code = ERROR_CODES[item.typ]
            result.append({
                "lnum": item.first_lineno,
                "type": "V",
                "number": error_code,
                "text": f"{error_code} {item.message} ({item.confidence}% confidence)"
            })

        return result
