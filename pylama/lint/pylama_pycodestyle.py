"""pycodestyle support."""
from pycodestyle import (BaseReport, StyleGuide, Checker, _parse_multi_options,
                         get_parser)

from pylama.lint import LinterV2 as Abstract
from pylama.context import RunContext


class Linter(Abstract):
    """pycodestyle runner."""

    name = "pycodestyle"

    def run_check(self, ctx: RunContext):  # noqa
        """Check code with pycodestyle."""
        params = ctx.get_params('pycodestyle')
        if params:
            parser = get_parser()
            for option in parser.option_list:
                if option.dest and option.dest in params:
                    value = params[option.dest]
                    if isinstance(value, str):
                        params[option.dest] = option.convert_value(option, value)

            for key in ["filename", "exclude", "select", "ignore"]:
                if key in params and isinstance(params[key], str):
                    params[key] = _parse_multi_options(params[key])

        style = StyleGuide(reporter=_PycodestyleReport, **params)
        style.options.report.ctx = ctx
        checker = Checker(ctx.filename, lines=ctx.lines, options=style.options)
        checker.check_all()


class _PycodestyleReport(BaseReport):

    ctx: RunContext

    def error(self, line_number, offset, text, _):
        """Save errors."""
        code, _,  text = text.partition(' ')
        self.ctx.push(
            text=text,
            type=code[0],
            number=code,
            col=offset + 1,
            lnum=line_number,
            source='pycodestyle',
        )
