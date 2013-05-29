.. _modeline:

File modeline
=============

You can set :ref:`options` for pylama inside a source files.

::


     .. Somethere in code
     # lint_ignore=W:lint_select=W301


For skip current file: ::

     .. Somethere in code
     # lint=0


Skip lines
==========

Just add `# nolint` in end of line for ignore. ::

     .. Somethere in code
     x=d+34  # nolint
