def test_config(parse_options):
    from pylama.config import get_config

    config = get_config()
    assert config

    options = parse_options()
    assert options
    assert options.skip
    assert options.max_line_length
    assert not options.verbose
    assert options.paths
    assert "pylama" in options.paths[0]

    options = parse_options(["-l", "pydocstyle,pycodestyle,unknown", "-i", "E"])
    assert set(options.linters) == set(["pydocstyle", "pycodestyle"])
    assert options.ignore == {"E"}

    options = parse_options("-o dummy dummy.py".split())
    assert set(options.linters) == set(["pycodestyle", "mccabe", "pyflakes"])
    assert options.skip == []


def test_parse_options(parse_options):
    options = parse_options()
    assert not options.select


def test_from_stdin(parse_options):
    options = parse_options("--from-stdin dummy.py".split())
    assert options
    assert options.from_stdin is True
    assert options.paths
