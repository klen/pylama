"""Pylama's core functionality.

Prepare params, check a modeline and run the checkers.
"""
import os.path as op
from typing import Any, Collection, Dict, Generator, List, Optional, Set, Tuple

from .config import (CURDIR, LOGGER, MODELINE_RE, SKIP_PATTERN, Namespace,
                     process_value)
from .errors import Error, remove_duplicates
from .lint import LINTERS


def run(path: str, rootdir: str = CURDIR, options: Namespace = None) -> List[Error]:
    """Run code checkers with given params.

    :param path: (str) A file's path.
    """
    code = None
    errors: List[Error] = []
    fileconfig = {}
    linters_params = {}
    params = {}
    path = op.relpath(path, rootdir)

    if options:
        linters_params = options.linters_params
        for mask in options.file_params:
            if mask.match(path):
                fileconfig.update(options.file_params[mask])

        if options.skip and any(p.match(path) for p in options.skip):
            LOGGER.info("Skip checking for path: %s", path)
            return []

    try:
        with open(path, encoding="utf-8") as source:
            code = source.read()
            params = build_params(options, fileconfig, parse_modeline(code))
            if params.get("skip"):
                LOGGER.info("Skip: %s", path)
                return errors

            LOGGER.debug("Checking params: %s", params)
            linters_to_run = get_linters(path, params, linters_params)
            for linter_cls, lname, select, ignore, lparams in linters_to_run:
                LOGGER.info("Run [%s] %s - %s", lname, path, lparams)
                linter_errors = linter_cls().run(
                    path, code=code, ignore=ignore, select=select, params=lparams
                )
                if linter_errors:
                    errors += filter_errors(
                        [
                            Error(filename=path, linter=lname, **er)
                            for er in linter_errors
                        ],
                        select=select,
                        ignore=ignore,
                    )

    except IOError as exc:
        LOGGER.error("IOError %s", exc)
        errors.append(Error(text=str(exc), filename=path, linter="pylama"))

    except SyntaxError as exc:
        LOGGER.error("SyntaxError %s", exc)
        errors.append(
            Error(
                linter="pylama",
                lnum=exc.lineno,
                col=exc.offset,
                text=f"E0100 SyntaxError: {exc.args[0]}",
                filename=path,
            )
        )

    except Exception as exc:  # noqa
        LOGGER.exception(exc)

    errors = list(remove_duplicates(errors))

    if code and errors:
        errors = filter_skiplines(code, errors)

    sorter = default_sorter
    if options and options.sort:
        sort = dict((v, n) for n, v in enumerate(options.sort, 1))
        sorter = lambda err: (sort.get(err.type, 999), err.lnum)

    return sorted(errors, key=sorter)


def get_linters(
    path: str, params: Dict[str, Any], linters_params: Dict[str, Any]
) -> Generator[Tuple, None, None]:
    """Prepare linters and params."""
    linters = params.get("linters") or LINTERS
    for item in linters:
        if not isinstance(item, tuple):
            item = item, LINTERS.get(item)

        lname, lclass = item
        if not (lclass and lclass.allow(path)):  # noqa
            continue

        lparams = linters_params.get(lname, {})
        ignore, select = merge_params(params, lparams)
        yield (lclass, lname, select, ignore, lparams)


def parse_modeline(code: str) -> Dict[str, str]:
    """Parse params from file's modeline."""
    seek = MODELINE_RE.search(code)
    if seek:
        return dict(v.split("=", 1) for v in seek.group(1).split(":"))  # type: ignore

    return {}


def build_params(
    options: Optional[Namespace], *configs: Dict[str, str]
) -> Dict[str, Any]:
    """Prepare and merge a params from modelines and configs."""
    if options:
        params: Dict[str, Any] = dict(
            skip=False,
            linters=options.linters,
            ignore=options.ignore,
            select=options.select,
        )
    else:
        params = dict(skip=False, ignore=set(), select=set(), linters=[])

    for config in configs:
        if not config:
            continue

        for key in ("ignore", "select"):
            if key in config:
                params[key] |= process_value(key, config[key])

        if "linters" in config:
            params["linters"] = process_value("linters", config["linters"])

        params["skip"] = bool(int(config.get("skip", False)))

    return params


def filter_errors(
    errors: List[Error], select: Collection[str] = None, ignore: Collection[str] = None
) -> Generator[Error, None, None]:
    """Filter errors by select and ignore options."""
    select = select or []
    ignore = ignore or []

    for err in errors:
        for rule in select:
            if err.number.startswith(rule):
                yield err
                break
        else:
            for rule in ignore:
                if err.number.startswith(rule):
                    break
            else:
                yield err


def filter_skiplines(code: str, errors: List[Error]) -> List[Error]:
    """Filter lines by `noqa`."""
    lnums = set(er.lnum for er in errors)
    skipped = set(
        lnum
        for lnum, line in enumerate(code.split("\n"), 1)
        if lnum in lnums and SKIP_PATTERN(line)
    )

    if skipped:
        errors = [er for er in errors if er.lnum not in skipped]

    return errors


def merge_params(
    params: Dict[str, Any], lparams: Dict[str, Any]
) -> Tuple[Set[str], Set[str]]:
    """Merge global ignore/select with linter local params."""
    ignore = params.get("ignore", set())
    if "ignore" in lparams:
        ignore = ignore | set(lparams["ignore"].split(","))

    select = params.get("select", set())
    if "select" in lparams:
        select = select | set(lparams["select"].split(","))

    return ignore, select


def default_sorter(err: Error) -> Any:
    """Sort by line number."""
    return err.lnum


# pylama:ignore=R0912,D210,F0001
