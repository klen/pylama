"""pycodestyle support."""
from pycodestyle import BaseReport, Checker, StyleGuide, get_parser

from pylama.context import RunContext
from pylama.lint import LinterV2 as Abstract


class Linter(Abstract):
    """pycodestyle runner."""

    name = "pycodestyle"

    def run_check(self, ctx: RunContext):  # noqa
        """Check code with pycodestyle."""
        params = ctx.get_params("pycodestyle")
        options = ctx.options
        if options:
            params.setdefault("max_line_length", options.max_line_length)

        if params:
            parser = get_parser()
            for option in parser.option_list:
                if option.dest and option.dest in params:
                    value = params[option.dest]
                    if isinstance(value, str):
                        params[option.dest] = option.convert_value(option, value)

        style = StyleGuide(reporter=_PycodestyleReport, **params)
        options = style.options
        options.report.ctx = ctx  # type: ignore
        checker = Checker(ctx.filename, lines=ctx.lines, options=options)
        checker.check_all()


class _PycodestyleReport(BaseReport):

    ctx: RunContext

    def error(self, line_number, offset, text, _):
        """Save errors."""
        code, _, text = text.partition(" ")
        self.ctx.push(
            text=text,
            type=code[0],
            number=code,
            col=offset + 1,
            lnum=line_number,
            source="pycodestyle",
        )
