from pylama.config import parse_options, get_config
from pylama.core import run, prepare_params


def test_config():
    config = get_config()
    assert config

    options = parse_options()
    assert options
    assert options.skip
    assert not options.verbose
    assert options.paths == ['pylama']

    options = parse_options(['-l', 'pydocstyle,pycodestyle', '-i', 'E'])
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pydocstyle', 'pycodestyle'])
    assert options.ignore == ['E']

    options = parse_options('-o dummy dummy.py'.split())
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pycodestyle', 'mccabe', 'pyflakes', 'eradicate'])
    assert options.skip == []


def test_ignore_select():
    options = parse_options()
    options.ignore = ['E301', 'D102']
    options.linters = ['pycodestyle', 'pydocstyle', 'pyflakes', 'mccabe']
    errors = run('dummy.py', options=options)
    assert len(errors) == 31

    numbers = [error.number for error in errors]
    assert 'D100' in numbers
    assert 'E301' not in numbers
    assert 'D102' not in numbers

    options.ignore = ['E3', 'D', 'E2']
    errors = run('dummy.py', options=options)
    assert not errors

    options.select = ['E301']
    errors = run('dummy.py', options=options)
    assert len(errors) == 1
    assert errors[0]['col']


def test_prepare_params():
    p1 = dict(ignore='W', select='R01', skip='0')
    p2 = dict(ignore='E34,R45', select='E')
    options = parse_options(ignore=['D'], config=False)
    params = prepare_params(p1, p2, options)
    assert params == {
        'ignore': set(['R45', 'E34', 'W', 'D']),
        'select': set(['R01', 'E']),
        'skip': False, 'linters': []}


def test_merge_params():
    from pylama.core import merge_params

    params = {'ignore': {1, 2, 3}}
    lparams = {'ignore': {4, 5}}

    ignore, _ = merge_params(params, lparams)
    assert ignore == {1, 2, 3, 4, 5}
    assert params['ignore'] == {1, 2, 3}
