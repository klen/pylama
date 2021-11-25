import os.path as op


def test_filter_errors():
    from pylama.core import filter_errors
    from pylama.errors import Error

    assert list(filter_errors([Error(text='E1')], select=['E'], ignore=['E101']))
    assert not list(filter_errors([Error(text='W1')], select=['W100'], ignore=['W']))


def test_remove_duplicates():
    from pylama.errors import Error, remove_duplicates

    errors = [Error(linter='pycodestyle', text='E701'), Error(linter='pylint', text='C0321')]
    errors = list(remove_duplicates(errors))
    assert len(errors) == 1


def test_parser_modeline():
    from pylama.core import parse_modeline

    code = """
        bla bla bla
        # pylama: ignore=W12,E14:select=R:skip=0
    """
    params = parse_modeline(code)
    assert params == dict(ignore='W12,E14', select='R', skip='0')


def test_checkpath():
    from pylama.config import parse_options
    from pylama.main import check_paths

    path = op.abspath('dummy.py')
    options = parse_options([path])
    result = check_paths(None, options)
    assert result
    assert result[0].filename == 'dummy.py'


def test_linters_params():
    from pylama.core import run
    from pylama.config import parse_options

    options = parse_options(linters='mccabe', config=False)
    options.linters_params['mccabe'] = dict(complexity=1)
    errors = run('dummy.py', options=options)
    assert len(errors) == 1

    options.linters_params['mccabe'] = dict(complexity=20)
    errors = run('dummy.py', options=options)
    assert not errors


def test_sort():
    from pylama.core import run
    from pylama.config import parse_options

    options = parse_options()
    options.sort = ['C', 'D']
    errors = run('dummy.py', options=options)
    assert errors[0].type == 'C'


def test_shell():
    from pylama.main import shell

    errors = shell('-o dummy dummy.py'.split(), error=False)
    assert errors

    errors = shell(['unknown.py'], error=False)
    assert not errors


def test_git_hook():
    from pylama.hook import git_hook

    assert not git_hook(False)


def test_hg_hook():
    from pylama.hook import hg_hook

    assert not hg_hook(None, dict())


def test_async():
    from pylama.check_async import check_async
    from pylama.config import parse_options

    options = parse_options(config=False)
    errors = check_async(['dummy.py'], options=options, rootdir='.')
    assert errors
