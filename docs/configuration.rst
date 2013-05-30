.. _config:

Configuration files
===================

When starting pylama try loading configuration file. By default: `<CURDIR>/pylama.ini`,
but you set it with "-o" option (:ref:`options`).

Section `main` set a global options, like `linters` and `skip`. Other sections are setting
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
