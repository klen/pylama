""" Pylama's shell support. """

from __future__ import absolute_import, with_statement

import sys
from os import walk, path as op

from .config import parse_options, CURDIR, setup_logger
from .core import LOGGER, run
from .async import check_async


def check_path(options, rootdir=None, candidates=None):
    """ Check path.

    :param path: Path to file or directory for code checking.
    :param rootdir: Root directory (for making relative file paths)
    :param options: Parsed pylama options (from pylama.config.parse_options)

    :returns: (list) Errors list

    """
    if not candidates:
        candidates = []
        path = op.abspath(options.path)
        if op.isdir(options.path):
            for root, _, files in walk(options.path):
                candidates += [op.relpath(op.join(root, f), CURDIR) for f in files]
        else:
            candidates.append(options.path)

    if rootdir is None:
        rootdir = path if op.isdir(path) else op.dirname(path)

    paths = []
    for path in candidates:

        if not options.force and not any(l.allow(path) for _, l in options.linters): # noqa
            continue

        if not op.exists(path):
            continue

        if options.skip and any(p.match(path) for p in options.skip):
            LOGGER.info('Skip path: %s', path)
            continue

        paths.append(path)

    if options.async:
        return check_async(paths, options, rootdir)

    errors = []
    for path in paths:
        errors += run(path=path, rootdir=rootdir, options=options)
    return errors


def shell(args=None, error=True):
    """ Endpoint for console.

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
        from .hook import install_hook
        return install_hook(options.path)

    return process_paths(options, error=error)


def process_paths(options, candidates=None, error=True):
    """ Process files and log errors. """
    errors = check_path(options, rootdir=CURDIR, candidates=candidates)
    pattern = "%(filename)s:%(lnum)s:%(col)s: %(text)s"
    if options.format == 'pylint':
        pattern = "%(filename)s:%(lnum)s: [%(type)s] %(text)s"

    for er in errors:
        LOGGER.warning(pattern, er._info)

    if error:
        sys.exit(int(bool(errors)))

    return errors


if __name__ == '__main__':
    shell()
