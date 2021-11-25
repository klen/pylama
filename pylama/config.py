"""Parse arguments from command line and configuration files."""
import fnmatch
import logging
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Any, Collection, List, Optional, Set, Tuple, Type, Union

from . import __version__
from .libs import inirama
from .lint import LINTERS, Linter

#: A default checkers
DEFAULT_LINTERS = "pycodestyle", "pyflakes", "mccabe"

CURDIR = os.getcwd()
CONFIG_FILES = "pylama.ini", "setup.cfg", "tox.ini", "pytest.ini"

#: The skip pattern
SKIP_PATTERN = re.compile(r"# *noqa\b", re.I).search

# Parse a modelines
MODELINE_RE = re.compile(
    r"^\s*#\s+(?:pylama:)\s*((?:[\w_]*=[^:\n\s]+:?)+)", re.I | re.M
)

# Setup a logger
LOGGER = logging.getLogger("pylama")
LOGGER.propagate = False
STREAM = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM)


class _Default:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<_Default [{self.value}]>"


def split_csp_str(val: Union[Collection[str], str]) -> Set[str]:
    """Split comma separated string into unique values, keeping their order."""
    if isinstance(val, str):
        val = val.strip().split(",")
    return set(x for x in val if x)


def parse_linters(linters: str) -> List[Tuple[str, Type[Linter]]]:
    """Initialize choosen linters."""
    result = []
    for name in split_csp_str(linters):
        linter = LINTERS.get(name)
        if linter:
            result.append((name, linter))
        else:
            logging.warning("Linter `%s` not found.", name)
    return result


def get_default_config_file(rootdir: str = None) -> Optional[str]:
    """Search for configuration file."""
    if rootdir is None:
        return DEFAULT_CONFIG_FILE

    for path in CONFIG_FILES:
        path = os.path.join(rootdir, path)
        if os.path.isfile(path) and os.access(path, os.R_OK):
            return path

    return None


DEFAULT_CONFIG_FILE = get_default_config_file(CURDIR)


PARSER = ArgumentParser(description="Code audit tool for python.")
PARSER.add_argument(
    "paths",
    nargs="*",
    default=_Default([CURDIR]),
    help="Paths to files or directories for code check.",
)

PARSER.add_argument("--verbose", "-v", action="store_true", help="Verbose mode.")

PARSER.add_argument("--version", action="version", version="%(prog)s " + __version__)

PARSER.add_argument(
    "--format",
    "-f",
    default=_Default("pycodestyle"),
    choices=["pep8", "pycodestyle", "pylint", "parsable"],
    help="Choose errors format (pycodestyle, pylint, parsable).",
)

PARSER.add_argument(
    "--select",
    "-s",
    default=_Default(""),
    type=split_csp_str,
    help="Select errors and warnings. (comma-separated list)",
)

PARSER.add_argument(
    "--sort",
    default=_Default(""),
    type=split_csp_str,
    help="Sort result by error types. Ex. E,W,D",
)

PARSER.add_argument(
    "--linters",
    "-l",
    default=_Default(",".join(DEFAULT_LINTERS)),
    type=parse_linters,
    help=(
        f"Select linters. (comma-separated). Choices are {','.join(s for s in LINTERS)}."
    ),
)

PARSER.add_argument(
    "--ignore",
    "-i",
    default=_Default(""),
    type=split_csp_str,
    help="Ignore errors and warnings. (comma-separated)",
)

PARSER.add_argument(
    "--skip",
    default=_Default(""),
    type=lambda s: [re.compile(fnmatch.translate(p)) for p in s.split(",") if p],
    help="Skip files by masks (comma-separated, Ex. */messages.py)",
)

PARSER.add_argument("--report", "-r", help="Send report to file [REPORT]")
PARSER.add_argument("--hook", action="store_true", help="Install Git (Mercurial) hook.")

PARSER.add_argument(
    "--concurrent",
    "--async",
    action="store_true",
    help="Enable async mode. Useful for checking a lot of files. ",
)

PARSER.add_argument(
    "--options",
    "-o",
    default=DEFAULT_CONFIG_FILE,
    metavar="FILE",
    help=(
        "Specify configuration file. "
        f"Looks for {', '.join(CONFIG_FILES[:-1])}, or {CONFIG_FILES[-1]}"
        f" in the current directory (default: {DEFAULT_CONFIG_FILE})"
    ),
)

PARSER.add_argument(
    "--force",
    "-F",
    action="store_true",
    default=_Default(False),
    help="Force code checking (if linter doesn't allow)",
)

PARSER.add_argument(
    "--abspath",
    "-a",
    action="store_true",
    default=_Default(False),
    help="Use absolute paths in output.",
)


ACTIONS = dict((a.dest, a) for a in PARSER._actions)  # pylint: disable=protected-access


def parse_options(  # noqa
    args: List[str] = None, config: bool = True, rootdir: str = CURDIR, **overrides
) -> Namespace:
    """Parse options from command line and configuration files."""
    args = args or []

    # Parse args from command string
    options = PARSER.parse_args(args)
    options.file_params = {}
    options.linters_params = {}

    # Compile options from ini
    if config:
        cfg = get_config(str(options.options), rootdir=rootdir)
        for opt, val in cfg.default.items():
            LOGGER.info("Find option %s (%s)", opt, val)
            passed_value = getattr(options, opt, _Default())
            if isinstance(passed_value, _Default):
                if opt == "paths":
                    val = val.split()
                if opt == "skip":
                    val = fix_pathname_sep(val)
                setattr(options, opt, _Default(val))

        # Parse file related options
        for name, opts in cfg.sections.items():

            if name == cfg.default_section:
                continue

            if name.startswith("pylama"):
                name = name[7:]

            if name in LINTERS:
                options.linters_params[name] = dict(opts)
                continue

            mask = re.compile(fnmatch.translate(fix_pathname_sep(name)))
            options.file_params[mask] = dict(opts)

    # Override options
    for opt, val in overrides.items():
        setattr(options, opt, process_value(opt, val))

    # Postprocess options
    for name in options.__dict__:
        value = getattr(options, name)
        if isinstance(value, _Default):
            setattr(options, name, process_value(name, value.value))

    if options.concurrent and "pylint" in options.linters:
        LOGGER.warning("Can't parse code asynchronously with pylint enabled.")
        options.concurrent = False

    return options


def process_value(name: str, value: Any) -> Any:
    """Compile option value."""
    action = ACTIONS.get(name)
    if not action:
        return value

    if callable(action.type):
        return action.type(value)

    if action.const:
        return bool(int(value))

    return value


def get_config(ini_path: str = None, rootdir: str = None) -> inirama.Namespace:
    """Load configuration from INI."""
    config = inirama.Namespace()
    config.default_section = "pylama"

    if not ini_path:
        path = get_default_config_file(rootdir)
        if path:
            config.read(path)
    else:
        config.read(ini_path)

    return config


def setup_logger(options: Namespace):
    """Do the logger setup with options."""
    LOGGER.setLevel(logging.INFO if options.verbose else logging.WARN)
    if options.report:
        LOGGER.removeHandler(STREAM)
        LOGGER.addHandler(logging.FileHandler(options.report, mode="w"))

    if options.options:
        LOGGER.info("Try to read configuration from: %r", options.options)


def fix_pathname_sep(val: str) -> str:
    """Fix pathnames for Win."""
    return val.replace(os.altsep or "\\", os.sep)


# pylama:ignore=W0212,D210,F0001
