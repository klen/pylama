from pathlib import Path
import sys
import builtins

import pytest


@pytest.fixture(scope="session")
def source():
    dummy = Path(__file__).parent / "../dummy.py"
    return dummy.read_text()


def test_skip_optional_if_not_installed():
    from pylama.lint import LINTERS

    assert 'fake' not in LINTERS


def test_mccabe(source):
    from pylama.lint import LINTERS, Linter

    mccabe = LINTERS["mccabe"]
    assert mccabe
    assert issubclass(mccabe, Linter)

    errors = mccabe().run("dummy.py", code=source, params={'complexity': 3})
    assert errors


def test_pydocstyle(source):
    from pylama.lint import LINTERS, Linter

    pydocstyle = LINTERS["pydocstyle"]
    assert pydocstyle
    assert issubclass(pydocstyle, Linter)

    errors = pydocstyle().run("dummy.py", code=source)
    assert errors

    errors2 = pydocstyle().run("dummy.py", code=source, params={'convention': 'numpy'})
    assert errors2
    assert len(errors) > len(errors2)


def test_pycodestyle(source):
    from pylama.lint import LINTERS, Linter

    pycodestyle = LINTERS["pycodestyle"]
    assert pycodestyle
    assert issubclass(pycodestyle, Linter)

    errors = pycodestyle().run("dummy.py", code=source)
    assert errors

    errors2 = pycodestyle().run("dummy.py", code=source, params={"max_line_length": 60})
    assert errors2
    assert len(errors2) > len(errors)


def test_pyflakes(source):
    from pylama.lint import LINTERS, Linter

    pyflakes = LINTERS["pyflakes"]
    assert pyflakes
    assert issubclass(pyflakes, Linter)

    errors = pyflakes().run("dummy.py", code=source)
    assert errors


def test_eradicate(source):
    from pylama.lint import LINTERS, Linter

    eradicate = LINTERS["eradicate"]
    assert eradicate
    assert issubclass(eradicate, Linter)

    errors = eradicate().run("dummy.py", code=source)
    assert errors

    errors = eradicate().run(
        "",
        code=(
            "#import os\n"
            "# from foo import junk\n"
            "#a = 3\n"
            "a = 4\n"
            "#foo(1, 2, 3)"
        )
    )
    assert len(errors) == 4


def test_mypy(source):
    from pylama.lint import LINTERS, Linter

    mypy = LINTERS["mypy"]
    assert mypy
    assert issubclass(mypy, Linter)

    errors = mypy().run("dummy.py", code=source)
    assert errors


def test_radon(source):
    from pylama.lint import LINTERS, Linter

    radon = LINTERS["radon"]
    assert radon
    assert issubclass(radon, Linter)

    errors = radon().run("dummy.py", code=source, params={'complexity': 3})
    assert errors


def test_pylint(source):
    from pylama.lint import LINTERS, Linter

    pylint = LINTERS["pylint"]
    assert pylint
    assert issubclass(pylint, Linter)

    errors = pylint().run("dummy.py", code=source)
    assert errors

    # Test immutable params
    params = {}
    errors = pylint().run("dummy.py", code=source, params=params)
    assert errors
    assert params == {}


def test_quotes(source):
    from pylama.lint import LINTERS, Linter

    quotes = LINTERS["quotes"]
    assert quotes
    assert issubclass(quotes, Linter)

    errors = quotes().run("dummy.py", code=source)
    assert errors


def test_vulture(source):
    from pylama.lint import LINTERS, Linter

    vulture = LINTERS["vulture"]
    assert vulture
    assert issubclass(vulture, Linter)

    errors = vulture().run("dummy.py", code=source)
    assert errors
