"""Pylama's shell support."""

import sys
from os import path as op
from os import walk
from typing import List, Optional

from .check_async import check_async
from .config import CURDIR, Namespace, parse_options, setup_logger
from .core import LOGGER, run
from .errors import Error

DEFAULT_FORMAT = "{filename}:{lnum}:{col} [{etype}] {text}"
MESSAGE_FORMATS = {
    "pylint": "{filename}:{lnum}: [{etype}] {text}",
    "pycodestyle": "{filename}:{lnum}:{col} {text}",
    "parsable": DEFAULT_FORMAT,
}


def check_paths(
    paths: Optional[List[str]], options: Namespace, rootdir: str = None
) -> List[Error]:
    """Check the given paths.

    :param rootdir: Root directory (for making relative file paths)
    :param options: Parsed pylama options (from pylama.config.parse_options)
    """
    candidates = []
    for path in paths or options.paths:
        if not op.exists(path):
            continue

        if not op.isdir(path):
            candidates.append(op.abspath(path))

        for root, _, files in walk(path):
            candidates += [op.relpath(op.join(root, f), CURDIR) for f in files]

    if not candidates:
        return []

    if rootdir is None:
        path = candidates[0]
        rootdir = path if op.isdir(path) else op.dirname(path)

    linters = options.linters
    if not options.force:
        candidates = [path for path in candidates if any(l.allow(path) for _, l in linters)]

    if options.concurrent:
        return check_async(candidates, options, rootdir)

    errors = []
    for path in candidates:
        errors += run(path=path, rootdir=rootdir, options=options)

    return errors


def shell(args=None, error=True):
    """Endpoint for console.

    Parse a command arguments, configuration files and run a checkers.

    :return list: list of errors
    :raise SystemExit:

    """
    if args is None:
        args = sys.argv[1:]

    options = parse_options(args)
    setup_logger(options)
    LOGGER.info(options)

    # Install VSC hook
    if options.hook:
        from .hook import install_hook  # noqa

        for path in options.paths:
            return install_hook(path)

    return process_paths(options, error=error)


def process_paths(
    options: Namespace, candidates: List[str] = None, error: bool = True
) -> List[Error]:
    """Process files and log errors."""
    errors = check_paths(candidates, options, rootdir=CURDIR)
    pattern = MESSAGE_FORMATS.get(options.format, DEFAULT_FORMAT)

    for err in errors:
        if options.abspath:
            err.filename = op.abspath(err.filename)
        LOGGER.warning(
            pattern.format(
                filename=err.filename,
                lnum=err.lnum,
                col=err.col,
                text=err.text,
                etype=err.type,
            )
        )

    if error:
        sys.exit(int(bool(errors)))

    return errors


if __name__ == "__main__":
    shell()

# pylama:ignore=F0001
