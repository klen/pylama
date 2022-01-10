"""Pylama's shell support."""

import sys
import warnings
from json import dumps
from os import path as op
from os import walk
from pathlib import Path
from typing import List, Optional

from pylama.check_async import check_async
from pylama.config import CURDIR, Namespace, parse_options, setup_logger
from pylama.core import LOGGER, run
from pylama.errors import Error
from pylama.utils import read_stdin

DEFAULT_FORMAT = "{filename}:{lnum}:{col} [{etype}] {number} {message} [{source}]"
MESSAGE_FORMATS = {
    "pylint": "{filename}:{lnum}: [{etype}] {number} {message} [{source}]",
    "pycodestyle": "{filename}:{lnum}:{col} {number} {message} [{source}]",
    "parsable": DEFAULT_FORMAT,
}


def check_paths(
    paths: Optional[List[str]],
    options: Namespace,
    code: str = None,
    rootdir: Path = None,
) -> List[Error]:
    """Check the given paths.

    :param rootdir: Root directory (for making relative file paths)
    :param options: Parsed pylama options (from pylama.config.parse_options)
    """
    paths = paths or options.paths
    if not paths:
        return []

    if code is None:
        candidates = []
        for path in paths or options.paths:
            if not op.exists(path):
                continue

            if not op.isdir(path):
                candidates.append(op.abspath(path))

            for root, _, files in walk(path):
                candidates += [op.relpath(op.join(root, f), CURDIR) for f in files]
    else:
        candidates = [paths[0]]

    if not candidates:
        return []

    if rootdir is None:
        path = candidates[0]
        rootdir = Path(path if op.isdir(path) else op.dirname(path))

    candidates = [path for path in candidates if path.endswith(".py")]

    if options.concurrent:
        return check_async(candidates, code=code, options=options, rootdir=rootdir)

    errors = []
    for path in candidates:
        errors += run(path=path, code=code, rootdir=rootdir, options=options)

    return errors


def check_path(
    options: Namespace,
    rootdir: str = None,
    candidates: List[str] = None,
    code: str = None,  # noqa
) -> List[Error]:
    """Support legacy code."""
    warnings.warn(
        "pylama.main.check_path is depricated and will be removed in pylama 9",
        DeprecationWarning,
    )
    return check_paths(
        candidates,
        code=code,
        options=options,
        rootdir=rootdir and Path(rootdir) or None,
    )


def shell(args: List[str] = None, error: bool = True):
    """Endpoint for console.

    Parse a command arguments, configuration files and run a checkers.
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

    if options.from_stdin and not options.paths:
        LOGGER.error("--from-stdin requires a filename")
        return sys.exit(1)

    errors = check_paths(
        options.paths,
        code=read_stdin() if options.from_stdin else None,
        options=options,
        rootdir=CURDIR,
    )
    display_errors(errors, options)

    if error:
        sys.exit(int(bool(errors)))

    return errors


def display_errors(errors: List[Error], options: Namespace):
    """Format and display the given errors."""
    if options.format == "json":
        LOGGER.warning(dumps([err.to_dict() for err in errors]))

    else:
        pattern = MESSAGE_FORMATS.get(options.format, DEFAULT_FORMAT)
        for err in errors:
            LOGGER.warning(err.format(pattern))


if __name__ == "__main__":
    shell()

# pylama:ignore=F0001
