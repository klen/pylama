"""SCM hooks. Integration with git and mercurial."""

from __future__ import absolute_import

import sys
from configparser import ConfigParser  # noqa
from os import chmod, getcwd
from os import path as op
from subprocess import PIPE, Popen
from typing import List, Tuple

from pylama.config import parse_options, setup_logger
from pylama.main import LOGGER, check_paths, display_errors


def run(command: str) -> Tuple[int, List[bytes], List[bytes]]:
    """Run a shell command."""
    with Popen(command.split(), stdout=PIPE, stderr=PIPE) as pipe:
        (stdout, stderr) = pipe.communicate()
        return (
            pipe.returncode,
            [line.strip() for line in stdout.splitlines()],
            [line.strip() for line in stderr.splitlines()],
        )


def git_hook(error=True):
    """Run pylama after git commit."""
    _, files_modified, _ = run("git diff-index --cached --name-only HEAD")

    options = parse_options()
    setup_logger(options)
    candidates = [f.decode("utf-8") for f in files_modified]
    if candidates:
        errors = check_paths(candidates, options, rootdir=getcwd())
        display_errors(errors, options)
        sys.exit(int(error and bool(errors)))


def hg_hook(_, repo, node=None, **kwargs):  # noqa
    """Run pylama after mercurial commit."""
    seen = set()
    candidates = []
    if len(repo):
        for rev in range(repo[node], len(repo)):
            for file_ in repo[rev].files():
                file_ = op.join(repo.root, file_)
                if file_ in seen or not op.exists(file_):
                    continue
                seen.add(file_)
                candidates.append(file_)

    options = parse_options()
    setup_logger(options)
    if candidates:
        errors = check_paths(candidates, options)
        display_errors(errors, options)
        sys.exit(int(bool(errors)))


def install_git(path):
    """Install hook in Git repository."""
    hook = op.join(path, "pre-commit")
    with open(hook, "w", encoding="utf-8") as target:
        target.write(
            """#!/usr/bin/env python
import sys
from pylama.hook import git_hook

if __name__ == '__main__':
    sys.exit(git_hook())
"""
        )
    chmod(hook, 484)


def install_hg(path):
    """Install hook in Mercurial repository."""
    hook = op.join(path, "hgrc")
    if not op.isfile(hook):
        open(hook, "w+", encoding="utf-8").close()

    cfgp = ConfigParser()
    with open(hook, "r", encoding="utf-8") as source:
        cfgp.read_file(source)

    if not cfgp.has_section("hooks"):
        cfgp.add_section("hooks")

    if not cfgp.has_option("hooks", "commit"):
        cfgp.set("hooks", "commit", "python:pylama.hooks.hg_hook")

    if not cfgp.has_option("hooks", "qrefresh"):
        cfgp.set("hooks", "qrefresh", "python:pylama.hooks.hg_hook")

    with open(hook, "w+", encoding="utf-8") as target:
        cfgp.write(target)


def install_hook(path):
    """Auto definition of SCM and hook installation."""
    is_git = op.join(path, ".git", "hooks")
    is_hg = op.join(path, ".hg")
    if op.exists(is_git):
        install_git(is_git)
        LOGGER.warning("Git hook has been installed.")

    elif op.exists(is_hg):
        install_hg(is_hg)
        LOGGER.warning("Mercurial hook has been installed.")

    else:
        LOGGER.error("VCS has not found. Check your path.")
        sys.exit(1)


# pylama:ignore=F0401,E1103,D210,F0001
