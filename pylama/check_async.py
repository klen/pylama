"""Support for checking code asynchronously."""

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List

from pylama.config import Namespace
from pylama.errors import Error

try:
    import multiprocessing

    CPU_COUNT = multiprocessing.cpu_count()

except (ImportError, NotImplementedError):
    CPU_COUNT = 1

from pylama.core import run

LOGGER = logging.getLogger("pylama")


def worker(params):
    """Do work."""
    path, code, options, rootdir = params
    return run(path, code=code, rootdir=rootdir, options=options)


def check_async(
    paths: List[str], code: str = None, options: Namespace = None, rootdir: Path = None
) -> List[Error]:
    """Check given paths asynchronously."""
    with ProcessPoolExecutor(CPU_COUNT) as pool:
        return [
            err
            for res in pool.map(
                worker, [(path, code, options, rootdir) for path in paths]
            )
            for err in res
        ]


# pylama:ignore=W0212,D210,F0001
