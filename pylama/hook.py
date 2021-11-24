"""SCM hooks. Integration with git and mercurial."""

from __future__ import absolute_import

import sys
from configparser import ConfigParser  # noqa
from os import chmod
from os import path as op
from subprocess import PIPE, Popen
from typing import List, Tuple

from .config import parse_options, setup_logger
from .main import LOGGER, process_paths


def run(command: str) -> Tuple[int, List[bytes], List[bytes]]:
    """Run a shell command."""
    with Popen(command.split(), stdout=PIPE, stderr=PIPE) as p:
        (stdout, stderr) = p.communicate()
        return (
            p.returncode,
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
        process_paths(options, candidates=candidates, error=error)


def hg_hook(ui, repo, node=None, **kwargs):
    """Run pylama after mercurial commit."""
    seen = set()
    paths = []
    if len(repo):
        for rev in range(repo[node], len(repo)):
            for file_ in repo[rev].files():
                file_ = op.join(repo.root, file_)
                if file_ in seen or not op.exists(file_):
                    continue
                seen.add(file_)
                paths.append(file_)

    options = parse_options()
    setup_logger(options)
    if paths:
        process_paths(options, candidates=paths)


def install_git(path):
    """Install hook in Git repository."""
    hook = op.join(path, "pre-commit")
    with open(hook, "w", encoding='utf-8') as fd:
        fd.write(
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
        open(hook, "w+", encoding='utf-8').close()

    c = ConfigParser()
    with open(hook, "r", encoding='utf-8') as source:
        c.read_file(source)

    if not c.has_section("hooks"):
        c.add_section("hooks")

    if not c.has_option("hooks", "commit"):
        c.set("hooks", "commit", "python:pylama.hooks.hg_hook")

    if not c.has_option("hooks", "qrefresh"):
        c.set("hooks", "qrefresh", "python:pylama.hooks.hg_hook")

    with open(hook, "w+", encoding='utf-8') as target:
        c.write(target)


def install_hook(path):
    """Auto definition of SCM and hook installation."""
    git = op.join(path, ".git", "hooks")
    hg = op.join(path, ".hg")
    if op.exists(git):
        install_git(git)
        LOGGER.warning("Git hook has been installed.")

    elif op.exists(hg):
        install_hg(hg)
        LOGGER.warning("Mercurial hook has been installed.")

    else:
        LOGGER.error("VCS has not found. Check your path.")
        sys.exit(1)


# pylama:ignore=F0401,E1103,D210,F0001
