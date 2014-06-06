import pytest

from pylama.config import parse_options, get_config
from pylama.core import (
    filter_errors, parse_modeline, prepare_params, run, remove_duplicates)
from pylama.errors import Error
from pylama.hook import git_hook, hg_hook
from pylama.lint.extensions import LINTERS
from pylama.main import shell, check_files
from pylama.tasks import check_path, async_check_files


def test_filters():
    assert list(
        filter_errors([Error(text='E')], select=['E'], ignore=['E101']))
    assert not list(
        filter_errors([Error(text='W')], select=['W100'], ignore=['W']))


def test_duplicates():
    errors = [
        Error(linter='pep8', text='E701'),
        Error(linter='pylint', text='C0321')]
    errors = list(remove_duplicates(errors))
    assert len(errors) == 1


def test_modeline():

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
        'ignore': set(['R45', 'E34', 'W', 'D']), 'select': set(['R01', 'E']),
        'skip': False}


def test_mccabe():
    mccabe = LINTERS.get('mccabe')
    errors = mccabe.run('dummy.py', '')
    assert errors == []


def test_pyflakes():
    options = parse_options(linters=['pyflakes'], config=False)
    assert options.linters
    errors = run('dummy.py', code="""
import sys

def test():
    unused = 1
""", options=options)
    assert len(errors) == 2


def test_pep8():
    options = parse_options(linters=['pep8'], config=False)
    errors = run('dummy.py', options=options)
    assert len(errors) == 3

    options.linter_params['pep8'] = dict(max_line_length=60)
    errors = run('dummy.py', options=options)
    assert len(errors) == 11


def test_pep257():
    options = parse_options(linters=['pep257'])
    errors = run('dummy.py', options=options)
    assert errors


def test_linters_params():
    options = parse_options(linters='mccabe', config=False)
    options.linter_params['mccabe'] = dict(complexity=2)
    errors = run('dummy.py', options=options)
    assert len(errors) == 13

    options.linter_params['mccabe'] = dict(complexity=20)
    errors = run('dummy.py', options=options)
    assert not errors


def test_ignore_select():
    options = parse_options()
    options.ignore = ['E301', 'D102']
    errors = run('dummy.py', options=options)
    assert len(errors) == 17

    options.ignore = ['E3', 'D']
    errors = run('dummy.py', options=options)
    assert len(errors) == 2

    options.ignore = ['E3', 'D']
    options.select = ['E301']
    errors = run('dummy.py', options=options)
    assert len(errors) == 3
    assert errors[0]['col']


def test_checkpath():
    options = parse_options(linters=['pep8'])
    errors = check_path('dummy.py', options)
    assert errors
    assert errors[0]['rel'] == 'dummy.py'


def test_async():
    options = parse_options(async=True, linters=['pep8'])
    errors = async_check_files(['dummy.py'], options)
    assert errors


def test_shell():
    errors = shell('-o dummy dummy.py'.split(), error=False)
    assert errors

    options = parse_options()
    errors = check_files(['dummy.py'], options=options, error=False)
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
