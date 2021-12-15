import pytest


def test_modeline(context):
    ctx = context(code=("def test():\n" "  pass\n\n" "# pylama:ignore=D:select=D100"))
    assert ctx.select == {"D100"}
    assert ctx.ignore == {"D"}


def test_filter(parse_args, context):
    ctx = context()
    assert not ctx.select
    assert not ctx.ignore
    ctx.push(number="D100")
    ctx.push(number="D200")
    ctx.push(number="E300")
    assert ctx.errors
    assert len(ctx.errors) == 3

    options = parse_args("--ignore=D,E300 --select=D100 dummy.py")
    ctx = context(options=options)
    assert ctx.select
    assert ctx.ignore

    ctx.push(number="D100")
    ctx.push(number="D200")
    ctx.push(number="E300")
    assert ctx.errors
    assert len(ctx.errors) == 1
    assert ctx.errors[0].number == "D100"

    ctx = context(options=options, pydocstyle={"select": "D200"})
    ctx.push(number="D100", source="pydocstyle")
    ctx.push(number="D200", source="pydocstyle")
    ctx.push(number="E300", source="pydocstyle")
    assert ctx.errors
    assert len(ctx.errors) == 2


def test_context_doesnt_suppress_exception(context):
    ctx = context()

    with pytest.raises(Exception):
        with ctx:
            raise Exception()


def test_get_params_doesnt_fail_on_subsequent_invocation(context):
    linter_params = {"pycodestyle": {"ignore": "D203,W503"}}

    ctx = context(**linter_params)
    ctx.get_params("pycodestyle")

    ctx = context(**linter_params)
    ctx.get_params("pycodestyle")


def test_context_linters_params(context):
    params = {'pylint': {'good_names': 'f'}}
    ctx = context(**params)
    lparams = ctx.get_params("pylint")
    assert lparams
    lparams["enable"] = True
    assert "enable" in lparams

    ctx = context(**params)
    lparams = ctx.get_params("pylint")
    assert lparams
    assert "enable" not in lparams
