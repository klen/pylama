def test_git_hook():
    from pylama.hook import git_hook

    assert not git_hook(False)


def test_hg_hook():
    from pylama.hook import hg_hook

    assert not hg_hook(None, {})
