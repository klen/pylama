"""Support Radon."""

from typing import Any, Dict, List
from radon.visitors import ComplexityVisitor
from radon.complexity import add_inner_blocks

from pylama.lint import Linter as Abstract


class Linter(Abstract):
    """Radon runner."""

    name = 'radon'

    def run(self, path: str, code=None, params=None, **_) -> List[Dict[str, Any]]:  # noqa  # noqa
        """Check code with Radon."""
        if params is None:
            params = {}

        complexity = params.get('complexity', 10)
        no_assert = params.get('no_assert', False)
        show_closures = params.get('show_closures', False)

        visitor = ComplexityVisitor.from_code(code, no_assert=no_assert)
        blocks = visitor.blocks
        if show_closures:
            blocks = add_inner_blocks(blocks)

        return [
            {'lnum': block.lineno, 'col': block.col_offset, 'type': 'R', 'number': 'R901',
             'text': f"R901: {block.name} is too complex {block.complexity}"}
            for block in visitor.blocks if block.complexity > complexity
        ]
