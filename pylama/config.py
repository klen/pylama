"""Parse arguments from command line and configuration files."""
import fnmatch
import logging
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Collection, Dict, List, Optional, Set, Union

from pylama import LOGGER, __version__
from pylama.libs import inirama
from pylama.lint import LINTERS

try:
    from pylama import config_toml
    CONFIG_FILES = ["pylama.ini", "pyproject.toml", "setup.cfg", "tox.ini", "pytest.ini"]
except ImportError:
    CONFIG_FILES = ["pylama.ini", "setup.cfg", "tox.ini", "pytest.ini"]


#: A default checkers
DEFAULT_LINTERS = "pycodestyle", "pyflakes", "mccabe"

CURDIR = Path.cwd()
HOMECFG = Path.home() / ".pylama.ini"
DEFAULT_SECTION = "pylama"

# Setup a logger
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


def prepare_sorter(val: Union[Collection[str], str]) -> Optional[Dict[str, int]]:
    """Parse sort value."""
    if val:
        types = split_csp_str(val)
        return dict((v, n) for n, v in enumerate(types, 1))

    return None


def parse_linters(linters: str) -> List[str]:
    """Initialize choosen linters."""
    return [name for name in split_csp_str(linters) if name in LINTERS]


def get_default_config_file(rootdir: Path = None) -> Optional[str]:
    """Search for configuration file."""
    if rootdir is None:
        return DEFAULT_CONFIG_FILE

    for filename in CONFIG_FILES:
        path = rootdir / filename
        if path.is_file() and os.access(path, os.R_OK):
            return path.as_posix()

    return None


DEFAULT_CONFIG_FILE = get_default_config_file(CURDIR)


def setup_parser() -> ArgumentParser:
    """Create and setup parser for command line."""
    parser = ArgumentParser(description="Code audit tool for python.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=_Default([CURDIR.as_posix()]),
        help="Paths to files or directories for code check.",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode.")
    parser.add_argument(
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
    parser.add_argument(
        "--linters",
        "-l",
        default=_Default(",".join(DEFAULT_LINTERS)),
        type=parse_linters,
        help=(
            f"Select linters. (comma-separated). Choices are {','.join(s for s in LINTERS)}."
        ),
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="Interpret the stdin as a python script, "
        "whose filename needs to be passed as the path argument.",
    )
    parser.add_argument(
        "--concurrent",
        "--async",
        action="store_true",
        help="Enable async mode. Useful for checking a lot of files. ",
    )

    parser.add_argument(
        "--format",
        "-f",
        default=_Default("pycodestyle"),
        choices=["pydocstyle", "pycodestyle", "pylint", "parsable", "json"],
        help="Choose output format.",
    )
    parser.add_argument(
        "--abspath",
        "-a",
        action="store_true",
        default=_Default(False),
        help="Use absolute paths in output.",
    )
    parser.add_argument(
        "--max-line-length",
        "-m",
        default=_Default(100),
        type=int,
        help="Maximum allowed line length",
    )
    parser.add_argument(
        "--select",
        "-s",
        default=_Default(""),
        type=split_csp_str,
        help="Select errors and warnings. (comma-separated list)",
    )
    parser.add_argument(
        "--ignore",
        "-i",
        default=_Default(""),
        type=split_csp_str,
        help="Ignore errors and warnings. (comma-separated)",
    )
    parser.add_argument(
        "--skip",
        default=_Default(""),
        type=lambda s: [re.compile(fnmatch.translate(p)) for p in s.split(",") if p],
        help="Skip files by masks (comma-separated, Ex. */messages.py)",
    )
    parser.add_argument(
        "--sort",
        default=_Default(),
        type=prepare_sorter,
        help="Sort result by error types. Ex. E,W,D",
    )
    parser.add_argument("--report", "-r", help="Send report to file [REPORT]")
    parser.add_argument(
        "--hook", action="store_true", help="Install Git (Mercurial) hook."
    )

    for linter_type in LINTERS.values():
        linter_type.add_args(parser)

    return parser


def parse_options(  # noqa
    args: List[str] = None, config: bool = True, rootdir: Path = CURDIR, **overrides
) -> Namespace:
    """Parse options from command line and configuration files."""
    # Parse args from command string
    parser = setup_parser()
    actions = dict(
        (a.dest, a) for a in parser._actions
    )  # pylint: disable=protected-access

    options = parser.parse_args(args or [])
    options.file_params = {}
    options.linters_params = {}

    # Compile options from ini
    if config:
        cfg = get_config(options.options, rootdir=rootdir)
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
        setattr(options, opt, process_value(actions, opt, val))

    # Postprocess options
    for name in options.__dict__:
        value = getattr(options, name)
        if isinstance(value, _Default):
            setattr(options, name, process_value(actions, name, value.value))

    if options.concurrent and "pylint" in options.linters:
        LOGGER.warning("Can't parse code asynchronously with pylint enabled.")
        options.concurrent = False

    return options


def process_value(actions: Dict, name: str, value: Any) -> Any:
    """Compile option value."""
    action = actions.get(name)
    if not action:

        return value

    if callable(action.type):
        return action.type(value)

    if action.const:
        return bool(int(value))

    return value


def get_config(user_path: str = None, rootdir: Path = None) -> inirama.Namespace:
    """Load configuration from files."""
    cfg_path = user_path or get_default_config_file(rootdir)
    if not cfg_path and HOMECFG.exists():
        cfg_path = HOMECFG.as_posix()

    if cfg_path:
        LOGGER.info("Read config: %s", cfg_path)
        if cfg_path.endswith(".toml"):
            return get_config_toml(cfg_path)
        else:
            return get_config_ini(cfg_path)

    return inirama.Namespace()


def get_config_ini(ini_path: str) -> inirama.Namespace:
    """Load configuration from INI."""
    config = inirama.Namespace()
    config.default_section = DEFAULT_SECTION
    config.read(ini_path)

    return config


def get_config_toml(toml_path: str) -> inirama.Namespace:
    """Load configuration from TOML."""
    config = config_toml.Namespace()
    config.default_section = DEFAULT_SECTION
    config.read(toml_path)

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
