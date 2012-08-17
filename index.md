---
layout: default
title: pylama
description: Code audit tool for python.
---

Pylama
======

[![Build Status](https://secure.travis-ci.org/klen/pylama.png?branch=master)](http://travis-ci.org/klen/pylama)

Code audit tool for python.


Requirements:
------------

* Python 2.6
* Python 2.7


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
    --ignore IGNORE, -i IGNORE
                            Ignore errors and warnings.
    --verbose, -v         Verbose mode.
    --select SELECT, -s SELECT
                            Select errors and warnings.
    --linters LINTERS, -l LINTERS
                            Select errors and warnings.
    --complexity COMPLEXITY, -c COMPLEXITY
                            Set mccabe complexity.
    --skip SKIP           Skip files (Ex. messages.py)


### File modeline

You can to set options for pylama inside the file.


     .. Somethere in code
     # lint_ignore=W:lint_select=W301


For disable pylama in current file:

     .. Somethere in code
     # lint=0


Bug tracker
-----------

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/klen/pylama/issues


Contributing
------------

Development of adrest happens at github: https://github.com/klen/adrest


License
-------

Licensed under a **GNU lesser general public license**.
