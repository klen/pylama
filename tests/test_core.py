import os.path as op


def test_remove_duplicates():
    from pylama.errors import Error, remove_duplicates

    errors = [
        Error(source="pycodestyle", text="E701"),
        Error(source="pylint", text="C0321"),
    ]
    errors = list(remove_duplicates(errors))
    assert len(errors) == 1


def test_checkpath(parse_options):
    from pylama.main import check_paths

    path = op.abspath("dummy.py")
    options = parse_options([path])
    result = check_paths(None, options)
    assert result
    assert result[0].filename == "dummy.py"


def test_run_with_code(run, parse_options):
    options = parse_options(linters="pyflakes")
    errors = run("filename.py", code="unknown_call()", options=options)
    assert errors


def test_async(parse_options):
    from pylama.check_async import check_async

    options = parse_options(config=False)
    errors = check_async(["dummy.py"], options=options, rootdir=".")
    assert errors


def test_errors():
    from pylama.errors import Error

    err = Error(col=0)
    assert err.col == 1
