import os.path as op

from pylama.check_async import check_async
from pylama.config import parse_options, get_config
from pylama.core import filter_errors, parse_modeline, prepare_params, run
from pylama.errors import Error, remove_duplicates
from pylama.hook import git_hook, hg_hook
from pylama.lint.extensions import LINTERS
from pylama.main import shell, check_path


def test_filter_errors():
    assert list(filter_errors([Error(text='E1')], select=['E'], ignore=['E101']))
    assert not list(filter_errors([Error(text='W1')], select=['W100'], ignore=['W']))


def test_remove_duplicates():
    errors = [Error(linter='pycodestyle', text='E701'), Error(linter='pylint', text='C0321')]
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
        'ignore': set(['R45', 'E34', 'W', 'D']),
        'select': set(['R01', 'E']),
        'skip': False, 'linters': []}


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


def test_eradicate():
    eradicate = LINTERS.get('eradicate')
    errors = eradicate.run('', code="\n".join([
        "#import os",
        "# from foo import junk",
        "#a = 3",
        "a = 4",
        "#foo(1, 2, 3)",
    ]))
    assert len(errors) == 4


def test_pyflakes():
    options = parse_options(linters=['pyflakes'], config=False)
    assert options.linters
    errors = run('dummy.py', code="\n".join([
        "import sys",
        "def test():",
        "    unused = 1"
    ]), options=options)
    assert len(errors) == 2


def test_pycodestyle():
    options = parse_options(linters=['pycodestyle'], config=False)
    assert len(options.linters) == 1
    errors = run('dummy.py', options=options)
    numbers = [error.number for error in errors]
    assert len(errors) == 4
    assert 'E265' in numbers
    assert 'E301' in numbers
    assert 'E501' in numbers

    options.linters_params['pycodestyle'] = dict(max_line_length=60)
    errors = run('dummy.py', options=options)
    assert len(errors) == 13


def test_pydocstyle():
    options = parse_options(linters=['pydocstyle'])
    assert len(options.linters) == 1
    errors = run('dummy.py', options=options)
    assert errors


#  def test_radon():
    #  options = parse_options(linters=['radon'])
    #  options.linters_params['radon'] = dict(complexity=1)
    #  assert len(options.linters) == 1
    #  errors = run('dummy.py', options=options)
    #  assert errors


def test_linters_params():
    options = parse_options(linters='mccabe', config=False)
    options.linters_params['mccabe'] = dict(complexity=1)
    errors = run('dummy.py', options=options)
    assert len(errors) == 1

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
    options.linters = ['pycodestyle', 'pydocstyle', 'pyflakes', 'mccabe']
    errors = run('dummy.py', options=options)
    assert len(errors) == 31

    numbers = [error.number for error in errors]
    assert 'D100' in numbers
    assert 'E301' not in numbers
    assert 'D102' not in numbers

    options.ignore = ['E3', 'D', 'E2']
    errors = run('dummy.py', options=options)
    assert len(errors) == 0

    options.select = ['E301']
    errors = run('dummy.py', options=options)
    assert len(errors) == 1
    assert errors[0]['col']


def test_shell():
    errors = shell('-o dummy dummy.py'.split(), error=False)
    assert errors

    errors = shell(['unknown.py'], error=False)
    assert not errors


def test_git_hook():
    assert not git_hook(False)


def test_hg_hook():
    assert not hg_hook(None, dict())


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


def test_async():
    options = parse_options(config=False)
    errors = check_async(['dummy.py'], options=options, rootdir='.')
    assert errors
