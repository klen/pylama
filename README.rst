Pylama
######

.. image:: https://secure.travis-ci.org/klen/pylama.png?branch=develop
    :target: http://travis-ci.org/klen/pylama
    :alt: Build Status

Code audit tool for python. Pylama wraps these tools:

* PEP8_ © 2012-2013, Florent Xicluna;
* PyFlakes_ © 2005-2013, Kevin Watters;
* Pylint_ © 2013, Logilab;
* Mccabe_ © Ned Batchelder;


 |  `Pylint dont supported in python3.`


Requirements:
============

* Python 2.6
* Python 2.7
* Python 3.2
* Python 3.3


Instalation:
============
::

    $ pip install pylama


Usage:
======

Recursive check current directory. ::

    $ pylama


Ignore some errors ::

    $ pylama -i W,E501


Set linters ::

    $ pylama -l "pep8,mccabe"


Options
=======
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
    --format {pep8,pylint}, -f {pep8,pylint}
                            Error format.
    --select SELECT, -s SELECT
                            Select errors and warnings. (comma-separated)
    --linters LINTERS, -l LINTERS
                            Select linters. (comma-separated)
    --ignore IGNORE, -i IGNORE
                            Ignore errors and warnings. (comma-separated)
    --skip SKIP           Skip files by masks (comma-separated, Ex.
                            */messages.py,*/.env)
    --complexity COMPLEXITY, -c COMPLEXITY
                            Set mccabe complexity.
    --report REPORT, -r REPORT
                            Filename for report.
    --hook                Install Git (Mercurial) hook.
    --options OPTIONS, -o OPTIONS
                            Select configuration file. By default is
                            '<CURDIR>/pylama.ini'


File modeline
-------------

You can to set options for pylama inside the file. ::


     .. Somethere in code
     # lint_ignore=W:lint_select=W301


For disable pylama in current file: ::

     .. Somethere in code
     # lint=0


Skip lines
----------

Just add `# nolint` in end of line for ignore. ::

     .. Somethere in code
     x=d+34  # nolint


Configuration file
------------------

When starting pylama try loading configuration file. By default: `<CURDIR>/pylama.ini`,
but you set it with "-o" option.

Section `main` set a global options, like `linters` and `skip`. Other sections set
modeline options for a custom files.

Example: `pylama.ini` ::

    [main]
    format = pylint
    skip = */.tox/*,*/.env/*
    linters = pylint,mccabe

    [pylama/main.py]
    lint_ignore = C901,R0914,W0212
    lint_select = R

    [setup.py]
    lint = 0


Bug tracker
-----------

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/klen/pylama/issues


Contributing
------------

Development of adrest happens at github: https://github.com/klen/adrest


License
-------

Licensed under a **GNU lesser general public license**.

.. _PEP8: https://github.com/jcrocholl/pep8
.. _PyFlakes: https://github.com/kevinw/pyflakes 
.. _Pylint: http://pylint.org
.. _Mccabe: http://nedbatchelder.com/blog/200803/python_code_complexity_microtool.html
