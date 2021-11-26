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


def test_checkpath(parse_options):
    from pylama.main import check_paths

    path = op.abspath('dummy.py')
    options = parse_options([path])
    result = check_paths(None, options)
    assert result
    assert result[0].filename == 'dummy.py'


def test_run_with_code(run, parse_options):
    options = parse_options(linters='pyflakes')
    errors = run('filename.py', code='unknown_call()', options=options)
    assert errors


def test_async(parse_options):
    from pylama.check_async import check_async

    options = parse_options(config=False)
    errors = check_async(['dummy.py'], options=options, rootdir='.')
    assert errors
