""" Pylama's core functionality.

Prepare params, check a modeline and run the checkers.

"""
import logging
import re

from . import utils


#: A default checkers
DEFAULT_LINTERS = 'pep8', 'pyflakes', 'mccabe'

#: The skip pattern
SKIP_PATTERN = re.compile(r'# *noqa\b', re.I).search

# Parse a modelines
MODELINE_RE = re.compile(
    r'^\s*#\s+(?:pymode\:)?((?:lint[\w_]*=[^:\n\s]+:?)+)', re.I | re.M)

# Setup a logger
LOGGER = logging.getLogger('pylama')
STREAM = logging.StreamHandler()
LOGGER.addHandler(STREAM)


def run(path, ignore=None, select=None, linters=DEFAULT_LINTERS, config=None,
        **meta):
    """ Run a code checkers with given params.

    :return errors: list of dictionaries with error's information

    """
    errors = []
    params = dict(ignore=ignore, select=select)
    code = None
    try:
        with open(path, 'rU') as f:
            code = f.read() + '\n\n'

            params = prepare_params(
                parse_modeline(code), config, ignore=ignore, select=select
            )

            if not params['lint']:
                return errors

            for lint in linters:
                # security gate to consider just relevant code for current linter
                if not is_code_relevant_for_linter(path, lint):
                    continue

                try:
                    linter = getattr(utils, lint)
                except AttributeError:
                    LOGGER.warning("Linter `%s` not found.", lint)
                    continue

                result = linter(path, code=code, **meta)
                for e in result:
                    e['col'] = e.get('col') or 0
                    e['lnum'] = e.get('lnum') or 0
                    e['type'] = e.get('type') or 'E'
                    e['text'] = "{0} [{1}]".format((e.get(
                        'text') or '').strip()
                        .replace("'", "\"").split('\n')[0], lint)
                    e['filename'] = path or ''
                    errors.append(e)

    except IOError as e:
        errors.append(dict(
            lnum=0, type='E', col=0, text=str(e), filename=path or ''))

    except SyntaxError as e:
        errors.append(dict(
            lnum=e.lineno or 0, type='E', col=e.offset or 0,
            text=e.args[0] + ' [%s]' % lint, filename=path or ''
        ))

    except Exception:
        import traceback
        logging.debug(traceback.format_exc())

    errors = [er for er in errors if filter_errors(er, **params)]

    if code:
        errors = filter_skiplines(code, errors)

    return sorted(errors, key=lambda x: x['lnum'])


def is_code_relevant_for_linter(path, linter):
    """ Checks if code is relevant to by checked by current linter.

    :return bool: True if:
                  - '.js' file and gjslinter OR
                  - '.py' and python linters.

    """
    if path.endswith('.js') and linter != 'gjslint':
        return False
    elif path.endswith('.py') and linter == 'gjslint':
        return False
    else:
        return True


def parse_modeline(code):
    """ Parse params from file's modeline.

    :return dict: Linter params.

    """
    seek = MODELINE_RE.search(code)
    if seek:
        return dict(v.split('=') for v in seek.group(1).split(':'))

    return dict()


def prepare_params(*configs, **params):
    """ Prepare and merge a params from modelines and configs.

    :return dict:

    """
    params['ignore'] = list(params.get('ignore') or [])
    params['select'] = list(params.get('select') or [])

    for config in filter(None, configs):
        for key in ('ignore', 'select'):
            config.setdefault(key, config.get('lint_' + key, []))
            if not isinstance(config[key], list):
                config[key] = config[key].split(',')
            params[key] += config[key]
        params['lint'] = config.get('lint', 1)

    params['ignore'] = set(params['ignore'])
    params['select'] = set(params['select'])
    params.setdefault('lint', 1)
    return params


def filter_errors(e, select=None, ignore=None, **params):
    """ Filter a erros by select and ignore options.

    :return bool:

    """
    if select:
        for s in select:
            if e['text'].startswith(s):
                return True

    if ignore:
        for s in ignore:
            if e['text'].startswith(s):
                return False

    return True


def filter_skiplines(code, errors):
    """ Filter lines by `noqa`.

    :return list: A filtered errors

    """
    if not errors:
        return errors

    enums = set(er['lnum'] for er in errors)
    removed = set([
        num for num, l in enumerate(code.split('\n'), 1)
        if num in enums and SKIP_PATTERN(l)
    ])

    if removed:
        errors = [er for er in errors if not er['lnum'] in removed]

    return errors
