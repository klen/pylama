import pytest

import os.path as op
from pylama.config import parse_options, get_config
from pylama.core import (
    filter_errors, parse_modeline, prepare_params, run)
from pylama.errors import Error, remove_duplicates
from pylama.hook import git_hook, hg_hook
from pylama.lint.extensions import LINTERS
from pylama.main import shell, check_path
from pylama.async import check_async


def test_filter_errors():
    assert list(filter_errors([Error(text='E')], select=['E'], ignore=['E101']))
    assert not list(filter_errors([Error(text='W')], select=['W100'], ignore=['W']))


def test_remove_duplicates():
    errors = [Error(linter='pep8', text='E701'), Error(linter='pylint', text='C0321')]
    errors = list(remove_duplicates(errors))
    assert len(errors) == 1


def test_parser_modeline():
    code = """
        bla bla bla
        # pylama: ignore=W12,E14:select=R:skip=0
    """
    params = parse_modeline(code)
    assert params == dict(ignore='W12,E14', select='R', skip='0')


def test_prepare_params():
    p1 = dict(ignore='W', select='R01', skip='0')
    p2 = dict(ignore='E34,R45', select='E')
    options = parse_options(ignore=['D'], config=False)
    params = prepare_params(p1, p2, options)
    assert params == {
        'ignore': set(['R45', 'E34', 'W', 'D']), 'select': set(['R01', 'E']), 'skip': False, 'linters': []}


def test_checkpath():
    path = op.abspath('dummy.py')
    options = parse_options([path])
    result = check_path(options)
    assert result
    assert result[0].filename == 'dummy.py'


def test_mccabe():
    mccabe = LINTERS.get('mccabe')
    errors = mccabe.run('dummy.py', '', params={})
    assert errors == []


def test_pyflakes():
    options = parse_options(linters=['pyflakes'], config=False)
    assert options.linters
    errors = run('dummy.py', code="\n".join([
        "import sys",
        "def test():",
        "    unused = 1"
    ]), options=options)
    assert len(errors) == 2


def test_pep8():
    options = parse_options(linters=['pep8'], config=False)
    errors = run('dummy.py', options=options)
    assert len(errors) == 3

    options.linters_params['pep8'] = dict(max_line_length=60)
    errors = run('dummy.py', options=options)
    assert len(errors) == 11


def test_pep257():
    options = parse_options(linters=['pep257'])
    errors = run('dummy.py', options=options)
    assert errors


def test_linters_params():
    options = parse_options(linters='mccabe', config=False)
    options.linters_params['mccabe'] = dict(complexity=2)
    errors = run('dummy.py', options=options)
    assert len(errors) == 13

    options.linters_params['mccabe'] = dict(complexity=20)
    errors = run('dummy.py', options=options)
    assert not errors


def test_sort():
    options = parse_options()
    options.sort = ['C', 'D']
    errors = run('dummy.py', options=options)
    assert errors[0].type == 'C'


def test_ignore_select():
    options = parse_options()
    options.ignore = ['E301', 'D102']
    options.linters = ['pep8', 'pep257', 'pyflakes', 'mccabe']
    errors = run('dummy.py', options=options)
    assert len(errors) == 16

    options.ignore = ['E3', 'D']
    errors = run('dummy.py', options=options)
    assert len(errors) == 1

    options.select = ['E301']
    errors = run('dummy.py', options=options)
    assert len(errors) == 2
    assert errors[0]['col']


def test_shell():
    errors = shell('-o dummy dummy.py'.split(), error=False)
    assert errors

    errors = shell(['unknown.py'], error=False)
    assert not errors


def test_git_hook():
    with pytest.raises(SystemExit):
        git_hook()


def test_hg_hook():
    with pytest.raises(SystemExit):
        hg_hook(None, dict())


def test_config():
    config = get_config()
    assert config

    options = parse_options()
    assert options
    assert options.skip
    assert not options.verbose
    assert options.path == 'pylama'

    options = parse_options(['-l', 'pep257,pep8', '-i', 'E'])
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pep257', 'pep8'])
    assert options.ignore == ['E']

    options = parse_options('-o dummy dummy.py'.split())
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pep8', 'mccabe', 'pyflakes'])
    assert options.skip == []


def test_async():
    options = parse_options(config=False)
    errors = check_async(['dummy.py'], options=options, rootdir='.')
    assert errors
