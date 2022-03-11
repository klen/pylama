|logo| Pylama
#############

.. _badges:

.. image:: https://github.com/klen/pylama/workflows/tests/badge.svg
    :target: https://github.com/klen/pylama/actions/workflows/tests.yml
    :alt: Tests Status

.. image:: https://github.com/klen/pylama/workflows/docs/badge.svg
    :target: https://klen.github.io/pylama
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/pylama
    :target: https://pypi.org/project/pylama/
    :alt: PYPI Version

.. image:: https://img.shields.io/pypi/pyversions/pylama
    :target: https://pypi.org/project/pylama/
    :alt: Python Versions

.. _description:

Code audit tool for Python. Pylama wraps these tools:

* pycodestyle_ (formerly pep8) © 2012-2013, Florent Xicluna;
* pydocstyle_ (formerly pep257 by Vladimir Keleshev) © 2014, Amir Rachum;
* PyFlakes_ © 2005-2013, Kevin Watters;
* Mccabe_ © Ned Batchelder;
* Pylint_ © 2013, Logilab;
* Radon_ © Michele Lacchia
* eradicate_ © Steven Myint;
* Mypy_ © Jukka Lehtosalo and contributors;
* Vulture_ © Jendrik Seipp and contributors;


.. _documentation:

Docs are available at https://klen.github.io/pylama/. Pull requests with
documentation enhancements and/or fixes are awesome and most welcome.


.. _contents:

.. contents::

.. _requirements:

Requirements:
=============

- Python (3.7, 3.8, 3.9, 3.10)
- If your tests are failing on Win platform you are missing: ``curses`` -
  http://www.lfd.uci.edu/~gohlke/pythonlibs/ (The curses library supplies a
  terminal-independent screen-painting and keyboard-handling facility for
  text-based terminals)

For python versions < 3.7 install pylama 7.7.1


.. _installation:

Installation:
=============
**Pylama** can be installed using pip: ::

    $ pip install pylama

You may optionally install the requirements with the library: ::

    $ pip install pylama[mypy]
    $ pip install pylama[pylint]
    $ pip install pylama[eradicate]
    $ pip install pylama[radon]
    $ pip install pylama[vulture]

Or install them all: ::

    $ pip install pylama[all]


.. _quickstart:

Quickstart
==========

**Pylama** is easy to use and really fun for checking code quality.  Just run
`pylama` and get common output from all pylama plugins (pycodestyle_,
PyFlakes_, etc.)

Recursively check the current directory. ::

    $ pylama

Recursively check a path. ::

    $ pylama <path_to_directory_or_file>

Ignore errors ::

    $ pylama -i W,E501

.. note:: You can choose a group of errors like `D`, `E1`, etc, or special errors like `C0312`

Choose code checkers ::

    $ pylama -l "pycodestyle,mccabe"


.. _options:

Set Pylama (checkers) options
=============================

Command line options
--------------------

::

    $ pylama --help

    usage: pylama [-h] [--version] [--verbose] [--options FILE] [--linters LINTERS] [--from-stdin] [--concurrent] [--format {pydocstyle,pycodestyle,pylint,parsable,json}] [--abspath]
                  [--max-line-length MAX_LINE_LENGTH] [--select SELECT] [--ignore IGNORE] [--skip SKIP] [--sort SORT] [--report REPORT] [--hook] [--max-complexity MAX_COMPLEXITY]
                  [--pydocstyle-convention {pep257,numpy,google}] [--pylint-confidence {HIGH,INFERENCE,INFERENCE_FAILURE,UNDEFINED}]
                  [paths ...]

    Code audit tool for python.

    positional arguments:
      paths                 Paths to files or directories for code check.

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --verbose, -v         Verbose mode.
      --options FILE, -o FILE
                            Specify configuration file. Looks for pylama.ini, setup.cfg, tox.ini, or pytest.ini in the current directory (default: None)
      --linters LINTERS, -l LINTERS
                            Select linters. (comma-separated). Choices are eradicate,mccabe,mypy,pycodestyle,pydocstyle,pyflakes,pylint,isort.
      --from-stdin          Interpret the stdin as a python script, whose filename needs to be passed as the path argument.
      --concurrent, --async
                            Enable async mode. Useful for checking a lot of files.
      --format {pydocstyle,pycodestyle,pylint,parsable,json}, -f {pydocstyle,pycodestyle,pylint,parsable,json}
                            Choose output format.
      --abspath, -a         Use absolute paths in output.
      --max-line-length MAX_LINE_LENGTH, -m MAX_LINE_LENGTH
                            Maximum allowed line length
      --select SELECT, -s SELECT
                            Select errors and warnings. (comma-separated list)
      --ignore IGNORE, -i IGNORE
                            Ignore errors and warnings. (comma-separated)
      --skip SKIP           Skip files by masks (comma-separated, Ex. */messages.py)
      --sort SORT           Sort result by error types. Ex. E,W,D
      --report REPORT, -r REPORT
                            Send report to file [REPORT]
      --hook                Install Git (Mercurial) hook.
      --max-complexity MAX_COMPLEXITY
                            Max complexity threshold

.. note:: additional options may be available depending on installed linters

.. _modeline:

File modelines
--------------

You can set options for **Pylama** inside a source file. Use
a pylama *modeline* for this, anywhere in the file.

Format: ::

    # pylama:{name1}={value1}:{name2}={value2}:...


For example, ignore warnings except W301: ::

     # pylama:ignore=W:select=W301


Disable code checking for current file: ::

     # pylama:skip=1

Those options have a higher priority.

.. _skiplines:

Skip lines (noqa)
-----------------

Just add ``# noqa`` at the end of a line to ignore:

::

    def urgent_fuction():
        unused_var = 'No errors here' # noqa


.. _config:

Configuration file
------------------

**Pylama** looks for a configuration file in the current directory.

You can use a “global” configuration, stored in `.pylama.ini` in your home
directory. This will be used as a fallback configuration.

The program searches for the first matching ini-style configuration file in
the directories of command line argument. Pylama looks for the configuration
in this order: ::

    ./pylama.ini
    ./setup.cfg
    ./tox.ini
    ./pytest.ini
    ~/.pylama.ini

The ``--option`` / ``-o`` argument can be used to specify a configuration file.

Pylama searches for sections whose names start with `pylama`.

The `pylama` section configures global options like `linters` and `skip`.

::

    [pylama]
    format = pylint
    skip = */.tox/*,*/.env/*
    linters = pylint,mccabe
    ignore = F0401,C0111,E731

Set code-checkers' options
--------------------------

You can set options for a special code checkers with pylama configurations.

::

    [pylama:pyflakes]
    builtins = _

    [pylama:pycodestyle]
    max_line_length = 100

    [pylama:pylint]
    max_line_length = 100
    disable = R

See code-checkers' documentation for more info. Note that dashes are
replaced by underscores (e.g. Pylint's ``max-line-length`` becomes
``max_line_length``).


Set options for file (group of files)
-------------------------------------

You can set options for special file (group of files)
with sections:

The options have a higher priority than in the `pylama` section.

::

    [pylama:*/pylama/main.py]
    ignore = C901,R0914,W0212
    select = R

    [pylama:*/tests.py]
    ignore = C0110

    [pylama:*/setup.py]
    skip = 1


Pytest integration
==================

Pylama has Pytest_ support. The package automatically registers itself as a pytest
plugin during installation. Pylama also supports the `pytest_cache` plugin.

Check files with pylama ::

    pytest --pylama ...

The recommended way to set pylama options when using pytest — configuration
files (see below).


Writing a linter
================

You can write a custom extension for Pylama.
The custom linter should be a python module. Its name should be like 'pylama_<name>'.

In 'setup.py', 'pylama.linter' entry point should be defined. ::

    setup(
        # ...
        entry_points={
            'pylama.linter': ['lintername = pylama_lintername.main:Linter'],
        }
        # ...
    )

'Linter' should be an instance of 'pylama.lint.Linter' class.
It must implement two methods:

1. ``allow`` takes a `path` argument and returns true if the linter can check this file for errors.
2. ``run`` takes a `path` argument and `meta` keyword arguments and returns a list of errors.

Example:
--------

Just a virtual 'WOW' checker.

setup.py: ::

    setup(
        name='pylama_wow',
        install_requires=[ 'setuptools' ],
        entry_points={
            'pylama.linter': ['wow = pylama_wow.main:Linter'],
        }
        # ...
    )

pylama_wow.py: ::

    from pylama.lint import Linter as BaseLinter

    class Linter(BaseLinter):

        def allow(self, path):
            return 'wow' in path

        def run(self, path, **meta):
            with open(path) as f:
                if 'wow' in f.read():
                    return [{
                        lnum: 0,
                        col: 0,
                        text: '"wow" has been found.',
                        type: 'WOW'
                    }]


Run pylama from python code
---------------------------
::

    from pylama.main import check_paths, parse_options

    # Use and/or modify 0 or more of the options defined as keys in the variable my_redefined_options below.
    # To use defaults for any option, remove that key completely.
    my_redefined_options = {
        'linters': ['pep257', 'pydocstyle', 'pycodestyle', 'pyflakes' ...],
        'ignore': ['D203', 'D213', 'D406', 'D407', 'D413' ...],
        'select': ['R1705' ...],
        'sort': 'F,E,W,C,D,...',
        'skip': '*__init__.py,*/test/*.py,...',
        'async': True,
        'force': True
        ...
    }
    # relative path of the directory in which pylama should check
    my_path = '...'

    options = parse_options([my_path], **my_redefined_options)
    errors = check_paths(my_path, options, rootdir='.')


.. _bagtracker:

Bug tracker
-----------

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/klen/pylama/issues


.. _contributing:

Contributing
------------

Development of `pylama` happens at GitHub: https://github.com/klen/pylama

Contributors
^^^^^^^^^^^^

See CONTRIBUTORS_.


.. _license:

License
-------

This is free software. You are permitted to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of it, under the terms of the MIT
License. See LICENSE file for the complete license.

This software is provided WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
LICENSE file for the complete disclaimer.


.. _links:

.. _CONTRIBUTORS: https://github.com/klen/pylama/graphs/contributors
.. _Mccabe: http://nedbatchelder.com/blog/200803/python_code_complexity_microtool.html
.. _pydocstyle: https://github.com/PyCQA/pydocstyle/
.. _pycodestyle: https://github.com/PyCQA/pycodestyle
.. _PyFlakes: https://github.com/pyflakes/pyflakes
.. _Pylint: http://pylint.org
.. _Pytest: http://pytest.org
.. _klen: http://klen.github.io/
.. _eradicate: https://github.com/myint/eradicate
.. _Mypy: https://github.com/python/mypy
.. _Vulture: https://github.com/jendrikseipp/vulture

.. |logo| image:: https://raw.github.com/klen/pylama/develop/docs/_static/logo.png
                  :width: 100
.. _Radon: https://github.com/rubik/radon

