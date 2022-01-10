def test_git_hook():
    from pylama.hook import git_hook

    try:
        assert not git_hook(False)
    except SystemExit as exc:
        assert exc.code == 0


def test_hg_hook():
    from pylama.hook import hg_hook

    assert not hg_hook(None, {})
