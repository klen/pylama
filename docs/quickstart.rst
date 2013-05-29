.. _quickstart:

Quickstart
==========

.. contents::

Pylama is easy to use and realy fun for checking code quality.
Just run `pylama` and get common output from all pylama plugins (PEP8_, PyFlakes_ and etc)

Recursive check the current directory. ::

    $ pylama

Recursive check a path. ::

    $ pylama <path_to_directory_or_file>

Ignore some errors ::

    $ pylama -i W,E501

Customize linters ::

    $ pylama -l "pep8,mccabe"


Options
=======
::

    $ pylama --help

    usage: pylama [-h] [--verbose] [--format {pep8,pylint}] [--select SELECT]
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
                            */messages.py)
    --complexity COMPLEXITY, -c COMPLEXITY
                            Set mccabe complexity.
    --report REPORT, -r REPORT
                            Filename for report.
    --hook                Install Git (Mercurial) hook.
    --options OPTIONS, -o OPTIONS
                            Select configuration file. By default is
                            '<CURDIR>/pylama.ini'
