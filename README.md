Pylama
======

[![Build Status](https://secure.travis-ci.org/klen/pylama.png?branch=master)](http://travis-ci.org/klen/pylama)

Code audit tool for python. Pylama wraps these tools:

* [PEP8](https://github.com/jcrocholl/pep8) © 2012-2013, Florent Xicluna;
* [PyFlakes](https://github.com/kevinw/pyflakes) © 2005-2013, Kevin Watters;
* [Mccabe](http://nedbatchelder.com/blog/200803/python_code_complexity_microtool.html) © Ned Batchelder;
* [Pylint](http://pylint.org`) © 2013, Logilab;

  `Pylint dont supported in python3.`


Requirements:
------------

* Python 2.6
* Python 2.7
* Python 3.2
* Python 3.3


Instalation:
------------

    $ pip install pylama


Usage:
------

Recursive check current directory.

    $ pylama

Ignore some errors

    $ pylama -i W,E501

Set linters

    $ pylama -l "pep8,mccabe"


Options
-------

    $ pylama --help

    usage: pylama [-h] [--ignore IGNORE] [--verbose] [--select SELECT]
                [--linters LINTERS] [--complexity COMPLEXITY] [--skip SKIP]
                [path]

    Code audit tool for python.

    positional arguments:
    path                  Path on file or directory.

    optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         Verbose mode.
    --select SELECT, -s SELECT
                            Select errors and warnings. (comma-separated)
    --linters LINTERS, -l LINTERS
                            Select linters. (comma-separated)
    --ignore IGNORE, -i IGNORE
                            Ignore errors and warnings. (comma-separated)
    --skip SKIP           Skip files by masks (comma-separated, Ex.
                            */messages.py)
    --complexity COMPLEXITY, -c COMPLEXITY
                            Set mccabe complexity.
    --report REPORT, -r REPORT
                            Filename for report.


### File modeline

You can to set options for pylama inside the file.


     .. Somethere in code
     # lint_ignore=W:lint_select=W301


For disable pylama in current file:

     .. Somethere in code
     # lint=0


### Skip lines

Just add `# nolint` in end of line for ignore.

     .. Somethere in code
     x=d+34  # nolint


Bug tracker
-----------

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/klen/pylama/issues


Contributing
------------

Development of adrest happens at github: https://github.com/klen/adrest


License
-------

Licensed under a **GNU lesser general public license**.
