"""frosted/reporter.py.

Defines the error messages that frosted can output

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
from collections import namedtuple

from pies.overrides import *

BY_CODE = {}
_ERROR_INDEX = 100

AbstractMessageType = namedtuple('AbstractMessageType', ('error_code', 'name', 'template',
                                                         'keyword', 'error_number'))


class MessageType(AbstractMessageType):

    class Message(namedtuple('Message', ('message', 'type', 'lineno', 'col'))):

        def __str__(self):
            return self.message

    def __new__(cls, error_code, name, template, keyword='{0!s}'):
        global _ERROR_INDEX
        new_instance = AbstractMessageType.__new__(cls, error_code, name, template,
                                                   keyword, _ERROR_INDEX)
        _ERROR_INDEX += 1
        BY_CODE[error_code] = new_instance
        return new_instance

    def __call__(self, filename, loc=None, *kargs, **kwargs):
        values = {'filename': filename, 'lineno': 0, 'col': 0}
        if loc:
            values['lineno'] = loc.lineno
            values['col'] = getattr(loc, 'col_offset', 0)
        values.update(kwargs)

        message = self.template.format(*kargs, **values)
        if kwargs.get('verbose', False):
            keyword = self.keyword.format(*kargs, **values)
            return self.Message('{0}:{1}:{2}:{3}:{4}:{5}'.format(filename, values['lineno'], values['col'],
                                                                 self.error_code, keyword, message),
                                self, values['lineno'], values['col'])
        return self.Message('{0}:{1}: {2}'.format(filename, values['lineno'], message),
                            self, values['lineno'], values['col'])



class OffsetMessageType(MessageType):
    def __call__(self, filename, loc, position=None, *kargs, **kwargs):
        if position:
            kwargs.update({'lineno': position[0], 'col': position[1]})
        return MessageType.__call__(self, filename, loc, *kargs, **kwargs)


class SyntaxErrorType(MessageType):
    def __call__(self, filename, msg, lineno, offset, text, *kargs, **kwargs):
        kwargs['lineno'] = lineno
        line = text.splitlines()[-1]
        msg += "\n" + str(line)
        if offset is not None:
            offset = offset - (len(text) - len(line))
            kwargs['col'] = offset
            msg += "\n" + re.sub(r'\S',' ', line[:offset]) + "^"

        return MessageType.__call__(self, filename, None, msg, *kargs, **kwargs)


Message = MessageType('I101', 'Generic', '{0}', '')
UnusedImport = MessageType('E101', 'UnusedImport', '{0} imported but unused')
RedefinedWhileUnused = MessageType('E301', 'RedefinedWhileUnused',
                                   'redefinition of {0!r} from line {1.lineno!r}')
RedefinedInListComp = MessageType('E302', 'RedefinedInListComp',
                                  'list comprehension redefines {0!r} from line {1.lineno!r}')
ImportShadowedByLoopVar = MessageType('E102', 'ImportShadowedByLoopVar',
                                      'import {0!r} from line {1.lineno!r} shadowed by loop variable')
ImportStarUsed = MessageType('E103', 'ImportStarUsed',
                             "'from {0!s} import *' used; unable to detect undefined names", '*')
UndefinedName = MessageType('E303', 'UndefinedName', "undefined name {0!r}")
DoctestSyntaxError = OffsetMessageType('E401', 'DoctestSyntaxError', "syntax error in doctest", '')
UndefinedExport = MessageType('E304', 'UndefinedExport', "undefined name {0!r} in __all__")
UndefinedLocal = MessageType('E305', 'UndefinedLocal',
                  'local variable {0!r} (defined in enclosing scope on line {1.lineno!r}) referenced before assignment')
DuplicateArgument = MessageType('E206', 'DuplicateArgument', "duplicate argument {0!r} in function definition")
Redefined = MessageType('E306', 'Redefined', "redefinition of {0!r} from line {1.lineno!r}")
LateFutureImport = MessageType('E207', 'LateFutureImport', "future import(s) {0!r} after other statements")
UnusedVariable = MessageType('E307', 'UnusedVariable', "local variable {0!r} is assigned to but never used")
MultipleValuesForArgument = MessageType('E201', 'MultipleValuesForArgument',
                                        "{0!s}() got multiple values for argument {1!r}")
TooFewArguments = MessageType('E202', 'TooFewArguments', "{0!s}() takes at least {1:d} argument(s)")
TooManyArguments = MessageType('E203', 'TooManyArguments', "{0!s}() takes at most {1:d} argument(s)")
UnexpectedArgument = MessageType('E204', 'UnexpectedArgument', "{0!s}() got unexpected keyword argument: {1!r}")
NeedKwOnlyArgument = MessageType('E205', 'NeedKwOnlyArgument', "{0!s}() needs kw-only argument(s): {1!s}")
ReturnWithArgsInsideGenerator = MessageType('E208', 'ReturnWithArgsInsideGenerator',
                                            "'return' with argument inside generator", 'return')
BareExcept = MessageType('W101', 'BareExcept', "bare except used: this is dangerous and should be avoided", 'except')
FileSkipped = MessageType('W201', 'FileSkipped', "Skipped because of the current configuration", 'skipped')
PythonSyntaxError = SyntaxErrorType('E402', 'PythonSyntaxError', "{0!s}", "")
