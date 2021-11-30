def test_skip_optional_if_not_installed():
    from pylama.lint import LINTERS

    assert "fake" not in LINTERS


def test_mccabe(context):
    from pylama.lint import LINTERS

    mccabe = LINTERS["mccabe"]
    assert mccabe

    ctx = context(mccabe={"max-complexity": 3})
    mccabe().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert not errors[0].message.startswith(errors[0].number)
    assert errors[0].col == 5

    ctx = context(args="--max-complexity 3")
    mccabe().run_check(ctx)
    errors = ctx.errors
    assert errors


def test_pydocstyle(context):
    from pylama.lint import LINTERS

    pydocstyle = LINTERS["pydocstyle"]
    assert pydocstyle

    ctx = context()
    pydocstyle().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert not errors[0].message.startswith(errors[0].number)

    ctx = context(pydocstyle={"convention": "numpy"})
    pydocstyle().run_check(ctx)
    errors2 = ctx.errors
    assert errors2
    assert len(errors) > len(errors2)

    ctx = context(args="--pydocstyle-convention numpy")
    pydocstyle().run_check(ctx)
    errors3 = ctx.errors
    assert errors3
    assert len(errors3) == len(errors2)


def test_pycodestyle(context):
    from pylama.lint import LINTERS

    pycodestyle = LINTERS["pycodestyle"]
    assert pycodestyle

    ctx = context()
    pycodestyle().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert not errors[0].message.startswith(errors[0].number)
    assert len(errors) == 5

    ctx = context(pycodestyle={"max_line_length": 60})
    pycodestyle().run_check(ctx)
    errors2 = ctx.errors
    assert errors2
    assert len(errors2) > len(errors)

    ctx = context(args="--max-line-length=60")
    pycodestyle().run_check(ctx)
    errors3 = ctx.errors
    assert errors3
    assert len(errors3) == len(errors2)


def test_pyflakes(context):
    from pylama.lint import LINTERS

    pyflakes = LINTERS["pyflakes"]
    assert pyflakes

    ctx = context()
    pyflakes().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert not errors[0].message.startswith(errors[0].number)


def test_eradicate(context):
    from pylama.lint import LINTERS

    eradicate = LINTERS["eradicate"]
    assert eradicate

    ctx = context()
    eradicate().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert not errors[0].message.startswith(errors[0].number)

    ctx = context(code=("#import os\n" "# from foo import junk\n" "#a = 3\n" "a = 4\n"))
    eradicate().run_check(ctx)
    errors = ctx.errors
    assert len(errors) == 3

    ctx = context(code="")
    eradicate().run_check(ctx)
    errors = ctx.errors
    assert not errors


def test_mypy(context):
    from pylama.lint import LINTERS

    mypy = LINTERS["mypy"]
    assert mypy

    ctx = context()
    mypy().run_check(ctx)
    errors = ctx.errors
    assert errors
    # assert errors[0]['number']
    # assert not errors[0]['text'].startswith(errors[0]['number'])


def test_radon(context):
    from pylama.lint import LINTERS

    radon = LINTERS["radon"]
    assert radon

    ctx = context(radon={"complexity": 3})
    radon().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert errors[0].col == 1
    assert not errors[0].message.startswith(errors[0].number)

    # Issue #164
    assert ":" not in errors[0].message

    ctx = context(args="--max-complexity=3 --radon-no-assert")
    radon().run_check(ctx)
    errors = ctx.errors
    assert errors


def test_pylint(context):
    from pylama.lint import LINTERS

    pylint = LINTERS["pylint"]
    assert pylint

    ctx = context()
    pylint().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert errors[0].col == 1
    assert not errors[0].message.startswith(errors[0].number)

    # Test immutable params
    ctx = context()
    pylint().run_check(ctx)
    assert ctx.errors
    assert not ctx.linters_params

    ctx = context(args="--pylint-confidence=HIGH --ignore=C")
    pylint().run_check(ctx)
    assert not ctx.errors

    ctx = context(pylint={"ignore": "E,R,W,C"})
    pylint().run_check(ctx)
    errors = ctx.errors
    assert not errors

    ctx = context(args="--ignore=E,R,W,C")
    pylint().run_check(ctx)
    errors = ctx.errors
    assert not errors

    ctx = context(pylint={"disable": "E,R,W,C"})
    pylint().run_check(ctx)
    errors = ctx.errors
    assert not errors


def test_quotes(source):
    from pylama.lint import LINTERS, Linter

    quotes = LINTERS["quotes"]
    assert quotes
    assert issubclass(quotes, Linter)

    errors = quotes().run("dummy.py", code=source)
    assert errors


def test_vulture(context):
    from pylama.lint import LINTERS

    vulture = LINTERS["vulture"]
    assert vulture

    ctx = context()
    vulture().run_check(ctx)
    errors = ctx.errors
    assert errors
    assert errors[0].number
    assert errors[0].col == 1
    assert not errors[0].message.startswith(errors[0].number)

    ctx = context(args="--vulture-min-confidence=80")
    vulture().run_check(ctx)
    assert not ctx.errors
