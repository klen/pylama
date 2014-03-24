""" Parse arguments from command line and configuration files. """
import fnmatch
from os import getcwd, path
from re import compile as re

import logging
from argparse import ArgumentParser

from . import version
from .core import LOGGER, STREAM
from .libs.inirama import Namespace
from .lint.extensions import LINTERS


#: A default checkers
DEFAULT_LINTERS = 'pep8', 'pyflakes', 'mccabe'

CURDIR = getcwd()
DEFAULT_INI_PATH = path.join(CURDIR, 'pylama.ini')


class _Default(object):

    def __init__(self, value=None):
        self.value = value

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __str__(self):
        return str(self.value)

    __repr__ = lambda s: "<_Default [%s]>" % s.value


def parse_options(args=None, **overrides): # noqa
    """ Parse options from command line and configuration files.

    :return argparse.Namespace:

    """
    if args is None:
        args = []

    # Parse args from command string
    parser = get_parser()
    options = parser.parse_args(args)

    # Parse options from ini file
    cfg = get_config(str(options.options))

    actions = dict((a.dest, a) for a in parser._actions)

    # Compile options from ini
    for k, v in cfg.default.items():
        LOGGER.info('Find option %s (%s)', k, v)
        passed_value = getattr(options, k, _Default())
        if isinstance(passed_value, _Default):
            setattr(options, k, _Default(v))

    # Override options
    for k, v in overrides.items():
        passed_value = getattr(options, k, _Default())
        if isinstance(passed_value, _Default):
            setattr(options, k, _Default(v))

    # Postprocess options
    opts = dict(options.__dict__.items())
    for name, value in opts.items():
        if not isinstance(value, _Default):
            continue

        value = value.value
        action = actions.get(name)
        if not action:
            continue

        if callable(action.type):
            value = action.type(value)

        if action.const:
            value = bool(int(value))

        setattr(options, name, value)

    # Parse file related options
    options.file_params = dict()
    options.linter_params = dict()
    for k, s in cfg.sections.items():
        if k == cfg.default_section:
            continue
        if k in LINTERS:
            options.linter_params[k] = dict(s)
            continue
        mask = re(fnmatch.translate(k))
        options.file_params[mask] = dict(s)
        options.file_params[mask]['lint'] = int(
            options.file_params[mask].get('lint', 1)
        )

    return options


def setup_logger(options):
    """ Setup logger with options. """
    LOGGER.setLevel(logging.INFO if options.verbose else logging.WARN)
    if options.report:
        LOGGER.removeHandler(STREAM)
        LOGGER.addHandler(logging.FileHandler(options.report, mode='w'))
    LOGGER.info('Try to read configuration from: ' + options.options)


def get_parser():
    """ Make command parser for pylama.

    :return ArgumentParser:

    """
    def split_csp_str(s):
        if isinstance(s, (list, tuple)):
            return s
        return list(set(i for i in s.strip().split(',') if i))

    parser = ArgumentParser(description="Code audit tool for python.")
    parser.add_argument(
        "path", nargs='?', default=_Default(CURDIR),
        help="Path on file or directory.")

    parser.add_argument(
        "--verbose", "-v", action='store_true', help="Verbose mode.")

    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)

    parser.add_argument(
        "--format", "-f", default=_Default('pep8'), choices=['pep8', 'pylint'],
        help="Error format.")

    parser.add_argument(
        "--select", "-s", default=_Default(''), type=split_csp_str,
        help="Select errors and warnings. (comma-separated)")

    def parse_linters(linters):
        result = list()
        for name in split_csp_str(linters):
            linter = LINTERS.get(name)
            if linter:
                result.append((name, linter))
            else:
                logging.warn("Linter `%s` not found.", name)
        return result

    parser.add_argument(
        "--linters", "-l", default=_Default(','.join(DEFAULT_LINTERS)),
        type=parse_linters, help=(
            "Select linters. (comma-separated). Choices are %s."
            % ','.join(s for s in LINTERS.keys())
        ))

    parser.add_argument(
        "--ignore", "-i", default=_Default(''), type=split_csp_str,
        help="Ignore errors and warnings. (comma-separated)")

    parser.add_argument(
        "--skip", default=_Default(''),
        type=lambda s: [re(fnmatch.translate(p)) for p in s.split(',') if p],
        help="Skip files by masks (comma-separated, Ex. */messages.py)")

    parser.add_argument("--report", "-r", help="Filename for report.")
    parser.add_argument(
        "--hook", action="store_true", help="Install Git (Mercurial) hook.")

    parser.add_argument(
        "--async", action="store_true",
        help="Enable async mode. Usefull for checking a lot of files. "
        "Dont supported with pylint.")

    parser.add_argument(
        "--options", "-o", default=_Default(DEFAULT_INI_PATH),
        help="Select configuration file. By default is '<CURDIR>/pylama.ini'")

    return parser


def get_config(ini_path=DEFAULT_INI_PATH):
    """ Load configuration from INI.

    :return Namespace:

    """
    config = Namespace()
    config.default_section = 'main'
    config.read(ini_path)

    return config


# lint_ignore=R0914,W0212,E1103,C901
