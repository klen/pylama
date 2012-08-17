import logging
import re
import sys
from argparse import ArgumentParser
from os import getcwd, walk, path as op

from . import utils


default_linters = 'pep8', 'pyflakes', 'mccabe'
default_complexity = 10
logger = logging.Logger('pylama')
logger.addHandler(logging.StreamHandler())


def run(path, ignore=None, select=None, linters=default_linters, **meta):
    errors = []
    ignore = ignore or []
    select = select or []

    for lint in linters:
        try:
            linter = getattr(utils, lint)
        except AttributeError:
            continue

        try:
            code = open(path, "rU").read() + '\n\n'
            params = parse_modeline(code)

            if params.get('lint_ignore'):
                ignore += params.get('lint_ignore').split(',')

            if params.get('lint_select'):
                select += params.get('lint_select').split(',')

            if params.get('lint'):
                for e in linter(path, code=code, **meta):
                    e.update(
                        col=e.get('col') or 0,
                        text="%s [%s]" % (e.get('text', '').strip().replace("'", "\"").split('\n')[0], lint),
                        filename=path,
                        **meta
                    )
                    errors.append(e)

        except IOError, e:
            errors.append(dict(
                lnum=0,
                col=0,
                text=str(e),
                **meta
            ))
        except SyntaxError, e:
            errors.append(dict(
                lnum=e.lineno,
                col=e.offset or 0,
                text=e.args[0],
                **meta
            ))
            break

        except Exception, e:
            assert True

    errors = filter(lambda e: _ignore_error(e, select, ignore), errors)
    return sorted(errors, key=lambda x: x['lnum'])


def _ignore_error(e, select, ignore):
    for s in select:
        if e['text'].startswith(s):
            return True
    for i in ignore:
        if e['text'].startswith(i):
            return False
    return True


def shell():
    parser = ArgumentParser(description="Code audit tool for python.")
    parser.add_argument("path", nargs='?', default=getcwd(), help="Path on file or directory.")
    parser.add_argument("--ignore", "-i", default='', help="Ignore errors and warnings.")
    parser.add_argument("--verbose", "-v", action='store_true', help="Verbose mode.")
    parser.add_argument("--select", "-s", default='', help="Select errors and warnings.")
    parser.add_argument("--linters", "-l", default=','.join(default_linters), help="Select errors and warnings.")
    parser.add_argument("--complexity", "-c", default=default_complexity, type=int, help="Set mccabe complexity.")
    parser.add_argument("--skip", help="Skip files (Ex. messages.py)")
    args = parser.parse_args()

    linters = set(filter(lambda i: i, args.linters.split(',')))
    ignore = set(filter(lambda i: i, args.ignore.split(',')))
    select = set(filter(lambda i: i, args.select.split(',')))

    logger.setLevel(logging.INFO if args.verbose else logging.WARN)

    paths = [args.path]
    if op.isdir(args.path):
        paths = []
        for root, _, files in walk(args.path):
            paths += [op.join(root, f) for f in files if f.endswith('.py') and not f.endswith(args.skip or '\/')]

    error = None
    for path in paths:
        logger.info("Parse file: %s" % path)
        errors = run(path, ignore=ignore, select=select, linters=linters, complexity=args.complexity)
        for e in errors:
            e['rel'] = op.relpath(e['filename'], op.dirname(args.path))
            error = 1
            logger.warning("%(rel)s:%(lnum)s %(text)s", e)

    sys.exit(error)


MODERE = re.compile(r'^\s*#\s+(?:pymode\:)?((?:lint[\w_]*=[^:\n\s]+:?)+)', re.I | re.M)


def parse_modeline(code):
    seek = MODERE.search(code)
    params = dict(lint=1)
    if seek:
        params = dict(v.split('=') for v in seek.group(1).split(':'))
        params['lint'] = int(params['lint'])
    return params


if __name__ == '__main__':
    shell()

# lint=12:lint_ignore=test
