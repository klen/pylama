def test_config(parse_options):
    from pylama.config import get_config

    config = get_config()
    assert config

    options = parse_options()
    assert options
    assert options.skip
    assert not options.verbose
    assert options.paths
    assert options.paths[0].endswith('pylama')

    options = parse_options(['-l', 'pydocstyle,pycodestyle', '-i', 'E'])
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pydocstyle', 'pycodestyle'])
    assert options.ignore == {'E'}

    options = parse_options('-o dummy dummy.py'.split())
    linters, _ = zip(*options.linters)
    assert set(linters) == set(['pycodestyle', 'mccabe', 'pyflakes'])
    assert options.skip == []


def test_parse_options(parse_options):
    options = parse_options()
    assert not options.select


def test_build_params(parse_options):
    from pylama.core import build_params

    p1 = dict(ignore='W', select='R01', skip='0')
    p2 = dict(ignore='E34,R45', select='E')
    options = parse_options(ignore=['D'], config=False)
    params = build_params(options, p1, p2)
    assert params
    assert params['linters']
    assert params['ignore'] == set(['R45', 'E34', 'W', 'D'])
    assert params['select'] == set(['R01', 'E'])
    assert params['skip'] is False


def test_merge_params():
    from pylama.core import merge_params

    params = {'ignore': {1, 2, 3}}
    lparams = {'ignore': '4,5'}

    ignore, _ = merge_params(params, lparams)
    assert ignore == {1, 2, 3, '4', '5'}
    assert params['ignore'] == {1, 2, 3}


def test_from_stdin(parse_options):
    options = parse_options('--from-stdin dummy.py'.split())
    assert options
    assert options.from_stdin is True
    assert options.paths
