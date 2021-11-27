from pathlib import Path
from typing import Dict

import pytest


@pytest.fixture(scope='session')
def parse_options():
    from pylama.config import parse_options as parse_options_

    return parse_options_


@pytest.fixture(scope='session')
def parse_args(parse_options):

    def parse_args_(args: str):
        return parse_options(args.split())

    return parse_args_


@pytest.fixture(scope='session')
def run():
    from pylama.core import run as run_

    return run_


@pytest.fixture(scope="session")
def source():
    dummy = Path(__file__).parent / "../dummy.py"
    return dummy.read_text()


@pytest.fixture
def context(source):
    from pylama.context import RunContext

    def fabric(*, code: str = None, options = None, **linters_params):
        ctx = RunContext('dummy.py', source if code is None else code, options=options)
        ctx.linters_params = linters_params
        return ctx

    return fabric
