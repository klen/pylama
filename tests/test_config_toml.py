"""Test TOML config handling."""

from unittest import mock

from pylama import config_toml
from pylama.config import DEFAULT_SECTION
from pylama.libs import inirama

CONFIG_TOML = """
[tool.pylama]
async = 1
ignore = "D203,D213,F0401,C0111,E731,I0011"
linters = "pycodestyle,pyflakes,mccabe,pydocstyle,pylint,mypy"
skip = "pylama/inirama.py,pylama/libs/*"
verbose = 0
max_line_length = 100

[tool.pylama.linter.pyflakes]
builtins = "_"

[tool.pylama.linter.pylint]
ignore = "R,E1002,W0511,C0103,C0204"

[[tool.pylama.files]]
path = "pylama/core.py"
ignore = "C901,R0914"

[[tool.pylama.files]]
path = "pylama/main.py"
ignore = "R0914,W0212,C901,E1103"

[[tool.pylama.files]]
path = "tests/*"
ignore = "D,C,W,E1103"
"""

CONFIG_INI="""
[pylama]
async = 1
ignore = D203,D213,F0401,C0111,E731,I0011
linters = pycodestyle,pyflakes,mccabe,pydocstyle,pylint,mypy
skip = pylama/inirama.py,pylama/libs/*
verbose = 0
max_line_length = 100

[pylama:pyflakes]
builtins = _

[pylama:pylint]
ignore=R,E1002,W0511,C0103,C0204

[pylama:pylama/core.py]
ignore = C901,R0914

[pylama:pylama/main.py]
ignore = R0914,W0212,C901,E1103

[pylama:tests/*]
ignore = D,C,W,E1103
"""

def test_toml_parsing_matches_ini():
    """Ensure the parsed TOML namepsace matches INI parsing."""
    with mock.patch("pylama.libs.inirama.io.open", mock.mock_open(read_data=CONFIG_INI)):
        ini = inirama.Namespace()
        ini.default_section = DEFAULT_SECTION
        ini.read("ini")

    with mock.patch("pylama.libs.inirama.io.open", mock.mock_open(read_data=CONFIG_TOML)):
        toml = config_toml.Namespace()
        toml.default_section = DEFAULT_SECTION
        toml.read("toml")

    assert ini.sections == toml.sections
