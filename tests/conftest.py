from pathlib import Path

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
