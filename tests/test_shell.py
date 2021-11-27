import io


def test_shell():
    from pylama.main import shell

    errors = shell('-o dummy dummy.py'.split(), error=False)
    assert errors

    errors = shell(['unknown.py'], error=False)
    assert not errors


def test_sort(parse_options):
    from pylama.core import run

    options = parse_options()
    options.sort = {'C': 1, 'D': 2}
    errors = run('dummy.py', options=options)
    assert errors[0].etype == 'C'


def test_linters_params(parse_options, run):
    options = parse_options(linters='mccabe', config=False)
    options.linters_params['mccabe'] = {'max-complexity': '1'}
    errors = run('dummy.py', options=options)
    assert len(errors) == 1

    options.linters_params['mccabe'] = {'max-complexity': '20'}
    errors = run('dummy.py', options=options)
    assert not errors


def test_ignore_select(parse_options, run):
    options = parse_options()
    options.ignore = {'E301', 'D102'}
    options.linters = ['pycodestyle', 'pydocstyle', 'pyflakes', 'mccabe']
    errors = run('dummy.py', options=options)
    assert errors
    for err in errors:
        assert err.number not in options.ignore

    numbers = [error.number for error in errors]
    assert 'D100' in numbers
    assert 'E301' not in numbers
    assert 'D102' not in numbers

    options.ignore = {'E', 'D', 'W'}
    errors = run('dummy.py', options=options)
    assert not errors

    options.select = {'E301'}
    errors = run('dummy.py', options=options)
    assert len(errors) == 1
    assert errors[0].col


def test_skip(parse_options, run):
    options = parse_options()
    errors = run('dummy.py', options=options, code=(
        "undefined()\n"
        "# pylama: skip=1"
    ))
    assert not errors


def test_stdin(monkeypatch, parse_args):
    monkeypatch.setattr('sys.stdin', io.StringIO('unknown_call()\ndef no_doc():\n  pass\n\n'))
    options = parse_args("--from-stdin dummy.py")
    assert options.from_stdin
