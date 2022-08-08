"""Pylama's core functionality.

Prepare params, check a modeline and run the checkers.
"""
import os.path as op
from pathlib import Path
from typing import List

from pylama.config import CURDIR, LOGGER, Namespace
from pylama.context import RunContext
from pylama.errors import Error, default_sorter, remove_duplicates
from pylama.lint import LINTERS, LinterV2


def run(
    path: str, code: str = None, rootdir: Path = CURDIR, options: Namespace = None
) -> List[Error]:
    """Run code checkers with the given params.

    :param path: (str) A file's path.
    """
    path = op.relpath(path, rootdir)

    with RunContext(path, code, options) as ctx:
        if ctx.skip:
            LOGGER.info("Skip checking for path: %s", path)

        else:
            for lname in ctx.linters or LINTERS:
                linter_cls = LINTERS.get(lname)
                if not linter_cls:
                    continue
                linter = linter_cls()
                LOGGER.info("Run [%s] %s", lname, path)
                if isinstance(linter, LinterV2):
                    linter.run_check(ctx)
                else:
                    for err_info in linter.run(
                        ctx.temp_filename, code=ctx.source, params=ctx.get_params(lname)
                    ):
                        ctx.push(source=lname, **err_info)

    if not ctx.errors:
        return ctx.errors

    errors = list(remove_duplicates(ctx.errors))

    sorter = default_sorter
    if options and options.sort:
        sort = options.sort
        sorter = lambda err: (sort.get(err.etype, 999), err.lnum)  # pylint: disable=C3001

    return sorted(errors, key=sorter)


# pylama:ignore=R0912,D210,F0001,C3001
