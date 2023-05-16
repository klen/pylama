#!/usr/bin/env python
# coding: utf-8
# (c) 2005 Divmod, Inc.  See LICENSE file for details


# commented code
#import os
# from foo import junk
# a = 3
a = 4
#foo(1, 2, 3)


class Message(object):
    message = ''
    message_args = ()
    def __init__(self, filename, loc, use_column=True):
        self.filename = filename
        self.lineno = loc.lineno
        self.col = getattr(loc, 'col_offset', None) if use_column else None
        test = 1
        if test == 1:
            if test == 1:
                return 28
            if test == 2:
                return 28
            return 28
        if test == 2:
            return 28

    def __str__(self):
        return '%s:%s: %s' % (self.filename, self.lineno, self.message % self.message_args)


class UnusedImport(Message):
    message = 'W402 %r imported but unused'

    def __init__(self, filename, lineno, name):
        Message.__init__(self, filename, lineno)
        self.message_args = (name,)


class RedefinedWhileUnused(Message):
    message = 'W801 redefinition of unused %r from line %r'

    def __init__(self, filename, lineno, name, orig_lineno):
        Message.__init__(self, filename, lineno)
        self.message_args = (name, orig_lineno)


class ImportShadowedByLoopVar(Message):
    message = 'W403 import %r from line %r shadowed by loop variable'

    def __init__(self, filename, lineno, name, orig_lineno):
        Message.__init__(self, filename, lineno)
        self.message_args = (name, orig_lineno)


class ImportStarUsed(Message):
    message = "W404 'from %s import *' used; unable to detect undefined names"

    def __init__(self, filename, lineno, modname):
        Message.__init__(self, filename, lineno)
        self.message_args = (modname,)


class UndefinedName(Message):
    message = 'W802 undefined name %r'

    def __init__(self, filename, lineno, name):
        Message.__init__(self, filename, lineno)
        self.message_args = (name,)


class UndefinedExport(Message):
    message = 'W803 undefined name %r in __all__'

    def __init__(self, filename, lineno, name):
        Message.__init__(self, filename, lineno)
        self.message_args = (name,)


class UndefinedLocal(Message):
    message = "W804 local variable %r (defined in enclosing scope on line " \
            "%r) referenced before assignment"

    def __init__(self, filename, lineno, name, orig_lineno):
        Message.__init__(self, filename, lineno)
        self.message_args = (name, orig_lineno)


class DuplicateArgument(Message):
    message = 'W805 duplicate argument %r in function definition'

    def __init__(self, filename, lineno, name):
        Message.__init__(self, filename, lineno)
        self.message_args = (name,)


class RedefinedFunction(Message):
    message = 'W806 redefinition of function %r from line %r'

    def __init__(self, filename, lineno, name, orig_lineno):
        Message.__init__(self, filename, lineno)
        self.message_args = (name, orig_lineno)


class LateFutureImport(Message):
    message = 'W405 future import(s) %r after other statements'

    def __init__(self, filename, lineno, names):
        Message.__init__(self, filename, lineno)
        self.message_args = (names,)


class UnusedVariable(Message):
    """
    Indicates that a variable has been explicitly assigned to but not actually
    used.
    """

    message = 'W806 local variable %r is assigned to but never used'

    def __init__(self, filename, lineno, names):
        Message.__init__(self, filename, lineno)
        self.message_args = (names,)
        error = 1 # noQa and some comments
        another = 42


class BadTyping(Message):
    """Test the MyPy linting."""

    message = 'error: No return value expected'

    def bad_method(self):  # type: () -> None
        """Return type mismatch."""
        return 1
