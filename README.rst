|logo| Pylama
#############

.. _description:

Code audit tool for python. Pylama wraps these tools:

* PEP8_ © 2012-2013, Florent Xicluna;
* PEP257_  © 2012, GreenSteam, <http://greensteam.dk/>
* PyFlakes_ © 2005-2013, Kevin Watters;
* Pylint_ © 2013, Logilab;
* Mccabe_ © Ned Batchelder;

 |  `Pylint doesnt supported in python3.`

.. _badges:

.. image:: https://secure.travis-ci.org/klen/pylama.png?branch=develop
    :target: http://travis-ci.org/klen/pylama
    :alt: Build Status

.. image:: https://coveralls.io/repos/klen/pylama/badge.png
    :target: https://coveralls.io/r/klen/pylama
    :alt: Coverals

.. image:: https://pypip.in/v/pylama/badge.png
    :target: https://crate.io/packages/pylama
    :alt: Version

.. image:: https://pypip.in/d/pylama/badge.png
    :target: https://crate.io/packages/pylama
    :alt: Downloads

.. image:: https://dl.dropboxusercontent.com/u/487440/reformal/donate.png
    :target: https://www.gittip.com/klen/
    :alt: Donate


.. _documentation:

Docs are available at https://pylama.readthedocs.org/. Pull requests with documentation enhancements and/or fixes are awesome and most welcome.


.. _contents:

.. contents::


.. _requirements:

Requirements:
=============

- Python (2.6, 2.7, 3.2, 3.3)


.. _installation:

Instalation:
============
**Pylama** should be installed using pip: ::
::

    $ pip install pylama


.. _quickstart:

Quickstart
==========

**Pylama** is easy to use and realy fun for checking code quality.
Just run `pylama` and get common output from all pylama plugins (PEP8_, PyFlakes_ and etc)

Recursive check the current directory. ::

    $ pylama

Recursive check a path. ::

    $ pylama <path_to_directory_or_file>

Ignore some errors ::

    $ pylama -i W,E501

Customize linters ::

    $ pylama -l "pep8,mccabe"


.. _options:

Command line options
====================
::

    $ pylama --help

    usage: main.py [-h] [--verbose] [--format {pep8,pylint}] [--select SELECT]
                [--linters LINTERS] [--ignore IGNORE] [--skip SKIP]
                [--complexity COMPLEXITY] [--report REPORT] [--hook]
                [--options OPTIONS]
                [path]

    Code audit tool for python.

    positional arguments:
    path                  Path on file or directory.

    optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         Verbose mode.
    --version             show program's version number and exit
    --format {pep8,pylint}, -f {pep8,pylint}
                            Error format.
    --select SELECT, -s SELECT
                            Select errors and warnings. (comma-separated)
    --linters LINTERS, -l LINTERS
                            Select linters. (comma-separated). Choices are
                            pep8,pep257,mccabe,pyflakes,pylint.
    --ignore IGNORE, -i IGNORE
                            Ignore errors and warnings. (comma-separated)
    --skip SKIP           Skip files by masks (comma-separated, Ex.
                            */messages.py*)
    --complexity COMPLEXITY, -c COMPLEXITY
                            Set mccabe complexity.
    --report REPORT, -r REPORT
                            Filename for report.
    --hook                Install Git (Mercurial) hook.
    --options OPTIONS, -o OPTIONS
                            Select configuration file. By default is
                            '<CURDIR>/pylama.ini'


.. _modeline:

File modeline
=============

You can set :ref:`options` for **Pylama** inside a source files.

::

     .. Somethere in code
     # lint_ignore=W:lint_select=W301


Disable code checking for current file: ::

     .. Somethere in code
     # lint=0


.. _skiplines:

Skip lines
==========

Just add `# noqa` in end of line for ignore. ::

     .. Somethere in code
     x=d+34  # noqa


.. _config:

Configuration file
==================

When starting **Pylama** try loading configuration file. By default: `<CURDIR>/pylama.ini`,
but you set it with "-o" option.

Section `main` contains a global options (see :ref:`options`), like `linters` and `skip`.

Other sections could set :ref:`modeline` for a custom files by filepath mask.

Example: `pylama.ini` ::

    [main]
    format = pylint
    skip = */.tox/*,*/.env/*
    linters = pylint,mccabe

    [*/pylama/main.py]
    lint_ignore = C901,R0914,W0212
    lint_select = R

    [*/tests.py]
    lint_ignore = C0110

    [*/setup.py]
    lint = 0

.. _bagtracker:

Bug tracker
-----------

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/klen/pylama/issues


.. _contributing:

Contributing
------------

Development of adrest happens at github: https://github.com/klen/pylama


.. _contributors:

Contributors
^^^^^^^^^^^^

* klen_ (Kirill Klenov)


.. _license:

License
-------

Licensed under a `BSD license`_.


.. _links:

.. _klen: http://klen.github.io/
.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _PEP8: https://github.com/jcrocholl/pep8
.. _PEP257: https://github.com/GreenSteam/pep257
.. _PyFlakes: https://github.com/kevinw/pyflakes 
.. _Pylint: http://pylint.org
.. _Mccabe: http://nedbatchelder.com/blog/200803/python_code_complexity_microtool.html
.. |logo| image:: https://raw.github.com/klen/pylama/develop/docs/_static/logo.png
                  :width: 100
