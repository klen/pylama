"""frosted/checker.py.

The core functionality of frosted lives here. Implements the core checking capability models Bindings and Scopes

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
OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import builtins
import doctest
import itertools
import os
import sys

from frosted import messages
from pies import ast
from pies.overrides import *

PY34_GTE = sys.version_info >= (3, 4)
BUILTIN_VARS = set(dir(builtins) + ['__file__', '__builtins__', '__debug__', '__name__', 'WindowsError'] +
                   os.environ.get('PYFLAKES_BUILTINS', '').split(','))


def node_name(node):
    """
        Convenience function: Returns node.id, or node.name, or None
    """
    return hasattr(node, 'id') and node.id or hasattr(node, 'name') and node.name


class Binding(object):
    """Represents the binding of a value to a name.

    The checker uses this to keep track of which names have been bound and which names have not. See Assignment for a
    special type of binding that is checked with stricter rules.

    """
    __slots__ = ('name', 'source', 'used')

    def __init__(self, name, source):
        self.name = name
        self.source = source
        self.used = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s object %r from line %r at 0x%x>' % (self.__class__.__name__,
                                                        self.name,
                                                        self.source.lineno,
                                                        id(self))


class Importation(Binding):
    """A binding created by an import statement."""
    __slots__ = ('fullName', )

    def __init__(self, name, source):
        self.fullName = name
        name = name.split('.')[0]
        super(Importation, self).__init__(name, source)


class Argument(Binding):
    """Represents binding a name as an argument."""
    __slots__ = ()


class Definition(Binding):
    """A binding that defines a function or a class."""
    __slots__ = ()


class Assignment(Binding):
    """Represents binding a name with an explicit assignment.

    The checker will raise warnings for any Assignment that isn't used. Also, the checker does not consider assignments
    in tuple/list unpacking to be Assignments, rather it treats them as simple Bindings.

    """
    __slots__ = ()


class FunctionDefinition(Definition):
    __slots__ = ('signature', )

    def __init__(self, name, source):
        super(FunctionDefinition, self).__init__(name, source)
        self.signature = FunctionSignature(source)


class ClassDefinition(Definition):
    __slots__ = ()


class ExportBinding(Binding):
    """A binding created by an __all__ assignment.  If the names in the list
    can be determined statically, they will be treated as names for export and
    additional checking applied to them.

    The only __all__ assignment that can be recognized is one which takes
    the value of a literal list containing literal strings.  For example:

        __all__ = ["foo", "bar"]

    Names which are imported and not otherwise used but appear in the value of
    __all__ will not have an unused import warning reported for them.

    """
    __slots__ = ()

    def names(self):
        """Return a list of the names referenced by this binding."""
        names = []
        if isinstance(self.source, ast.List):
            for node in self.source.elts:
                if isinstance(node, ast.Str):
                    names.append(node.s)
        return names


class Scope(dict):
    importStarred = False       # set to True when import * is found

    def __repr__(self):
        scope_cls = self.__class__.__name__
        return '<%s at 0x%x %s>' % (scope_cls, id(self), dict.__repr__(self))


class ClassScope(Scope):
    pass


class FunctionScope(Scope):
    """Represents the name scope for a function."""
    uses_locals = False
    always_used = set(['__tracebackhide__', '__traceback_info__', '__traceback_supplement__'])

    def __init__(self):
        Scope.__init__(self)
        self.globals = self.always_used.copy()

    def unusedAssignments(self):
        """Return a generator for the assignments which have not been used."""
        for name, binding in self.items():
            if (not binding.used and name not in self.globals
                    and not self.uses_locals
                    and isinstance(binding, Assignment)):
                yield name, binding


class GeneratorScope(Scope):
    pass


class ModuleScope(Scope):
    pass


class FunctionSignature(object):
    __slots__ = ('decorated', 'argument_names', 'default_count', 'kw_only_argument_names', 'default_count',
                 'kw_only_argument_names', 'kw_only_default_count', 'has_var_arg', 'has_kw_arg')

    def __init__(self, node):
        self.decorated = bool(any(node.decorator_list))
        self.argument_names = ast.argument_names(node)
        self.default_count = len(node.args.defaults)
        self.kw_only_argument_names = ast.kw_only_argument_names(node)
        self.kw_only_default_count = ast.kw_only_default_count(node)
        self.has_var_arg = node.args.vararg is not None
        self.has_kw_arg = node.args.kwarg is not None

    def min_argument_count(self):
        return len(self.argument_names) - self.default_count

    def maxArgumentCount(self):
        return len(self.argument_names)

    def checkCall(self, call_node, reporter, name):
        if self.decorated:
            return

        filledSlots = set()
        filledKwOnlySlots = set()
        for item, arg in enumerate(call_node.args):
            if item >= len(self.argument_names):
                if not self.has_var_arg:
                    return reporter.report(messages.TooManyArguments, call_node, name, self.maxArgumentCount())
                break
            filledSlots.add(item)

        for kw in call_node.keywords:
            slots = None
            try:
                argIndex = self.argument_names.index(kw.arg)
                slots = filledSlots
            except ValueError:
                try:
                    argIndex = self.kw_only_argument_names.index(kw.arg)
                    slots = filledKwOnlySlots
                except ValueError:
                    if self.has_kw_arg:
                        continue
                    else:
                        return reporter.report(messages.UnexpectedArgument, call_node, name, kw.arg)
            if argIndex in slots:
                return reporter.report(messages.MultipleValuesForArgument, call_node, name, kw.arg)
            slots.add(argIndex)

        filledSlots.update(range(len(self.argument_names) - self.default_count, len(self.argument_names)))
        filledKwOnlySlots.update(range(len(self.kw_only_argument_names) - self.kw_only_default_count,
                                       len(self.kw_only_argument_names)))

        if (len(filledSlots) < len(self.argument_names) and not call_node.starargs and not call_node.kwargs):
            return reporter.report(messages.TooFewArguments, call_node, name, self.min_argument_count())
        if (len(filledKwOnlySlots) < len(self.kw_only_argument_names) and not call_node.kwargs):
            missing_arguments = [repr(arg) for i, arg in enumerate(self.kw_only_argument_names)
                                if i not in filledKwOnlySlots]
            return reporter.report(messages.NeedKwOnlyArgument, call_node, name, ', '.join(missing_arguments))


class Checker(object):
    """The core of frosted, checks the cleanliness and sanity of Python code."""

    node_depth = 0
    offset = None
    trace_tree = False
    builtin_vars = BUILTIN_VARS

    def __init__(self, tree, filename='(none)', builtins=None, **settings):
        self.settings = settings
        self.ignore_errors = settings.get('ignore_frosted_errors', [])
        file_specifc_ignores = settings.get('ignore_frosted_errors_for_' + (os.path.basename(filename) or ""), None)
        if file_specifc_ignores:
            self.ignore_errors += file_specifc_ignores

        self._node_handlers = {}
        self._deferred_functions = []
        self._deferred_assignments = []
        self.dead_scopes = []
        self.messages = []
        self.filename = filename
        if builtins:
            self.builtin_vars = self.builtin_vars.union(builtins)
        self.scope_stack = [ModuleScope()]
        self.except_handlers = [()]
        self.futures_allowed = True
        self.root = tree
        self.handle_children(tree)
        self.run_deferred(self._deferred_functions)
        self._deferred_functions = None
        self.run_deferred(self._deferred_assignments)
        self._deferred_assignments = None
        del self.scope_stack[1:]
        self.pop_scope()
        self.check_dead_scopes()

    def defer_function(self, callable):
        """Schedule a function handler to be called just before completion.

        This is used for handling function bodies, which must be deferred because code later in the file might modify
        the global scope. When 'callable' is called, the scope at the time this is called will be restored, however it
        will contain any new bindings added to it.

        """
        self._deferred_functions.append((callable, self.scope_stack[:], self.offset))

    def defer_assignment(self, callable):
        """Schedule an assignment handler to be called just after deferred
        function handlers."""
        self._deferred_assignments.append((callable, self.scope_stack[:], self.offset))

    def run_deferred(self, deferred):
        """Run the callables in deferred using their associated scope stack."""
        for handler, scope, offset in deferred:
            self.scope_stack = scope
            self.offset = offset
            handler()

    @property
    def scope(self):
        return self.scope_stack[-1]

    def pop_scope(self):
        self.dead_scopes.append(self.scope_stack.pop())

    def check_dead_scopes(self):
        """Look at scopes which have been fully examined and report names in
        them which were imported but unused."""
        for scope in self.dead_scopes:
            export = isinstance(scope.get('__all__'), ExportBinding)
            if export:
                all = scope['__all__'].names()
                # Look for possible mistakes in the export list
                if not scope.importStarred and os.path.basename(self.filename) != '__init__.py':
                    undefined = set(all) - set(scope)
                    for name in undefined:
                        self.report(messages.UndefinedExport, scope['__all__'].source, name)
            else:
                all = []

            # Look for imported names that aren't used without checking imports in namespace definition
            for importation in scope.values():
                if isinstance(importation, Importation) and not importation.used and importation.name not in all:
                    self.report(messages.UnusedImport, importation.source, importation.name)

    def push_scope(self, scope_class=FunctionScope):
        self.scope_stack.append(scope_class())

    def push_function_scope(self):    # XXX Deprecated
        self.push_scope(FunctionScope)

    def push_class_scope(self):       # XXX Deprecated
        self.push_scope(ClassScope)

    def report(self, message_class, *args, **kwargs):
        error_code = message_class.error_code

        if(not error_code[:2] + "00" in self.ignore_errors and not error_code in self.ignore_errors and not
           str(message_class.error_number) in self.ignore_errors):
            kwargs['verbose'] = self.settings.get('verbose')
            self.messages.append(message_class(self.filename, *args, **kwargs))

    def has_parent(self, node, kind):
        while hasattr(node, 'parent'):
            node = node.parent
            if isinstance(node, kind):
                return True

    def get_common_ancestor(self, lnode, rnode, stop=None):
        stop = stop or self.root
        if lnode is rnode:
            return lnode
        if stop in (lnode, rnode):
            return stop

        if not hasattr(lnode, 'parent') or not hasattr(rnode, 'parent'):
            return
        if (lnode.level > rnode.level):
            return self.get_common_ancestor(lnode.parent, rnode, stop)
        if (rnode.level > lnode.level):
            return self.get_common_ancestor(lnode, rnode.parent, stop)
        return self.get_common_ancestor(lnode.parent, rnode.parent, stop)

    def descendant_of(self, node, ancestors, stop=None):
        for ancestor in ancestors:
            if self.get_common_ancestor(node, ancestor, stop) not in (stop, None):
                return True
        return False

    def on_fork(self, parent, lnode, rnode, items):
        return (self.descendant_of(lnode, items, parent) ^ self.descendant_of(rnode, items, parent))

    def different_forks(self, lnode, rnode):
        """True, if lnode and rnode are located on different forks of
        IF/TRY."""
        ancestor = self.get_common_ancestor(lnode, rnode)
        if isinstance(ancestor, ast.If):
            for fork in (ancestor.body, ancestor.orelse):
                if self.on_fork(ancestor, lnode, rnode, fork):
                    return True
        elif isinstance(ancestor, ast.Try):
            body = ancestor.body + ancestor.orelse
            for fork in [body] + [[hdl] for hdl in ancestor.handlers]:
                if self.on_fork(ancestor, lnode, rnode, fork):
                    return True
        elif isinstance(ancestor, ast.TryFinally):
            if self.on_fork(ancestor, lnode, rnode, ancestor.body):
                return True
        return False

    def add_binding(self, node, value, report_redef=True):
        """Called when a binding is altered.

        - `node` is the statement responsible for the change
        - `value` is the optional new value, a Binding instance, associated
        with the binding; if None, the binding is deleted if it exists.
        - if `report_redef` is True (default), rebinding while unused will be
        reported.

        """
        redefinedWhileUnused = False
        if not isinstance(self.scope, ClassScope):
            for scope in self.scope_stack[::-1]:
                existing = scope.get(value.name)
                if (isinstance(existing, Importation)
                        and not existing.used
                        and (not isinstance(value, Importation) or
                             value.fullName == existing.fullName)
                        and report_redef
                        and not self.different_forks(node, existing.source)):
                    redefinedWhileUnused = True
                    self.report(messages.RedefinedWhileUnused,
                                node, value.name, existing.source)

        existing = self.scope.get(value.name)
        if not redefinedWhileUnused and self.has_parent(value.source, ast.ListComp):
            if (existing and report_redef
                    and not self.has_parent(existing.source, (ast.For, ast.ListComp))
                    and not self.different_forks(node, existing.source)):
                self.report(messages.RedefinedInListComp,
                            node, value.name, existing.source)

        if (isinstance(existing, Definition)
                and not existing.used
                and not self.different_forks(node, existing.source)):
            self.report(messages.RedefinedWhileUnused,
                        node, value.name, existing.source)
        else:
            self.scope[value.name] = value

    def get_node_handler(self, node_class):
        try:
            return self._node_handlers[node_class]
        except KeyError:
            nodeType = str(node_class.__name__).upper()
        self._node_handlers[node_class] = handler = getattr(self, nodeType)
        return handler

    def iter_visible_scopes(self):
        outerScopes = itertools.islice(self.scope_stack, len(self.scope_stack) - 1)
        scopes = [scope for scope in outerScopes
                  if isinstance(scope, (FunctionScope, ModuleScope))]
        if (isinstance(self.scope, GeneratorScope)
            and scopes[-1] != self.scope_stack[-2]):
            scopes.append(self.scope_stack[-2])
        scopes.append(self.scope_stack[-1])
        return iter(reversed(scopes))

    def handle_node_load(self, node):
        name = node_name(node)
        if not name:
            return

        importStarred = False
        for scope in self.iter_visible_scopes():
            importStarred = importStarred or scope.importStarred
            try:
                scope[name].used = (self.scope, node)
            except KeyError:
                pass
            else:
                return

        # look in the built-ins
        if importStarred or name in self.builtin_vars:
            return
        if name == '__path__' and os.path.basename(self.filename) == '__init__.py':
            # the special name __path__ is valid only in packages
            return

        # protected with a NameError handler?
        if 'NameError' not in self.except_handlers[-1]:
            self.report(messages.UndefinedName, node, name)

    def handle_node_store(self, node):
        name = node_name(node)
        if not name:
            return
        # if the name hasn't already been defined in the current scope
        if isinstance(self.scope, FunctionScope) and name not in self.scope:
            # for each function or module scope above us
            for scope in self.scope_stack[:-1]:
                if not isinstance(scope, (FunctionScope, ModuleScope)):
                    continue
                # if the name was defined in that scope, and the name has
                # been accessed already in the current scope, and hasn't
                # been declared global
                used = name in scope and scope[name].used
                if used and used[0] is self.scope and name not in self.scope.globals:
                    # then it's probably a mistake
                    self.report(messages.UndefinedLocal,
                                scope[name].used[1], name, scope[name].source)
                    break

        parent = getattr(node, 'parent', None)
        if isinstance(parent, (ast.For, ast.comprehension, ast.Tuple, ast.List)):
            binding = Binding(name, node)
        elif (parent is not None and name == '__all__' and
              isinstance(self.scope, ModuleScope)):
            binding = ExportBinding(name, parent.value)
        else:
            binding = Assignment(name, node)
        if name in self.scope:
            binding.used = self.scope[name].used
        self.add_binding(node, binding)

    def handle_node_delete(self, node):
        name = node_name(node)
        if not name:
            return
        if isinstance(self.scope, FunctionScope) and name in self.scope.globals:
            self.scope.globals.remove(name)
        else:
            try:
                del self.scope[name]
            except KeyError:
                self.report(messages.UndefinedName, node, name)

    def handle_children(self, tree):
        for node in ast.iter_child_nodes(tree):
            self.handleNode(node, tree)

    def is_docstring(self, node):
        """Determine if the given node is a docstring, as long as it is at the
        correct place in the node tree."""
        return isinstance(node, ast.Str) or (isinstance(node, ast.Expr) and
                                             isinstance(node.value, ast.Str))

    def docstring(self, node):
        if isinstance(node, ast.Expr):
            node = node.value
        if not isinstance(node, ast.Str):
            return (None, None)
        # Computed incorrectly if the docstring has backslash
        doctest_lineno = node.lineno - node.s.count('\n') - 1
        return (node.s, doctest_lineno)

    def handleNode(self, node, parent):
        if node is None:
            return
        if self.offset and getattr(node, 'lineno', None) is not None:
            node.lineno += self.offset[0]
            node.col_offset += self.offset[1]
        if self.trace_tree:
            print('  ' * self.node_depth + node.__class__.__name__)
        if self.futures_allowed and not (isinstance(node, ast.ImportFrom) or
                                        self.is_docstring(node)):
            self.futures_allowed = False
        self.node_depth += 1
        node.level = self.node_depth
        node.parent = parent
        try:
            handler = self.get_node_handler(node.__class__)
            handler(node)
        finally:
            self.node_depth -= 1
        if self.trace_tree:
            print('  ' * self.node_depth + 'end ' + node.__class__.__name__)

    _get_doctest_examples = doctest.DocTestParser().get_examples

    def handle_doctests(self, node):
        try:
            docstring, node_lineno = self.docstring(node.body[0])
            if not docstring:
                return
            examples = self._get_doctest_examples(docstring)
        except (ValueError, IndexError):
            # e.g. line 6 of the docstring for <string> has inconsistent
            # leading whitespace: ...
            return
        node_offset = self.offset or (0, 0)
        self.push_scope()
        for example in examples:
            try:
                tree = compile(example.source, "<doctest>", "exec", ast.PyCF_ONLY_AST)
            except SyntaxError:
                e = sys.exc_info()[1]
                position = (node_lineno + example.lineno + e.lineno,
                            example.indent + 4 + (e.offset or 0))
                self.report(messages.DoctestSyntaxError, node, position)
            else:
                self.offset = (node_offset[0] + node_lineno + example.lineno,
                               node_offset[1] + example.indent + 4)
                self.handle_children(tree)
                self.offset = node_offset
        self.pop_scope()

    def find_return_with_argument(self, node):
        """Finds and returns a return statment that has an argument.

        Note that we should use node.returns in Python 3, but this method is never called in Python 3 so we don't bother
        checking.

        """
        for item in node.body:
            if isinstance(item, ast.Return) and item.value:
                return item
            elif not isinstance(item, ast.FunctionDef) and hasattr(item, 'body'):
                return_with_argument = self.find_return_with_argument(item)
                if return_with_argument:
                    return return_with_argument

    def is_generator(self, node):
        """Checks whether a function is a generator by looking for a yield
        statement or expression."""
        if not isinstance(node.body, list):
            # lambdas can not be generators
            return False
        for item in node.body:
            if isinstance(item, (ast.Assign, ast.Expr)):
                if isinstance(item.value, ast.Yield):
                    return True
            elif not isinstance(item, ast.FunctionDef) and hasattr(item, 'body'):
                if self.is_generator(item):
                    return True
        return False

    def ignore(self, node):
        pass

    # "stmt" type nodes
    RETURN = DELETE = PRINT = WHILE = IF = WITH = WITHITEM = RAISE = TRYFINALLY = ASSERT = EXEC = EXPR = handle_children

    CONTINUE = BREAK = PASS = ignore

    # "expr" type nodes
    BOOLOP = BINOP = UNARYOP = IFEXP = DICT = SET = YIELD = YIELDFROM = COMPARE = REPR = ATTRIBUTE = SUBSCRIPT = \
             LIST = TUPLE = STARRED = NAMECONSTANT = handle_children

    NUM = STR = BYTES = ELLIPSIS = ignore

    # "slice" type nodes
    SLICE = EXTSLICE = INDEX = handle_children

    # expression contexts are node instances too, though being constants
    LOAD = STORE = DEL = AUGLOAD = AUGSTORE = PARAM = ignore

    # same for operators
    AND = OR = ADD = SUB = MULT = DIV = MOD = POW = LSHIFT = RSHIFT = BITOR = BITXOR = BITAND = FLOORDIV = INVERT = \
          NOT = UADD = USUB = EQ = NOTEQ = LT = LTE = GT = GTE = IS = ISNOT = IN = NOTIN = ignore

    # additional node types
    COMPREHENSION = KEYWORD = handle_children

    def GLOBAL(self, node):
        """Keep track of globals declarations."""
        if isinstance(self.scope, FunctionScope):
            self.scope.globals.update(node.names)

    NONLOCAL = GLOBAL

    def LISTCOMP(self, node):
        # handle generators before element
        for gen in node.generators:
            self.handleNode(gen, node)
        self.handleNode(node.elt, node)

    def GENERATOREXP(self, node):
        self.push_scope(GeneratorScope)
        # handle generators before element
        for gen in node.generators:
            self.handleNode(gen, node)
        self.handleNode(node.elt, node)
        self.pop_scope()

    SETCOMP = GENERATOREXP

    def DICTCOMP(self, node):
        self.push_scope(GeneratorScope)
        for gen in node.generators:
            self.handleNode(gen, node)
        self.handleNode(node.key, node)
        self.handleNode(node.value, node)
        self.pop_scope()

    def FOR(self, node):
        """Process bindings for loop variables."""
        vars = []

        def collectLoopVars(n):
            if isinstance(n, ast.Name):
                vars.append(n.id)
            elif isinstance(n, ast.expr_context):
                return
            else:
                for c in ast.iter_child_nodes(n):
                    collectLoopVars(c)

        collectLoopVars(node.target)
        for varn in vars:
            if (isinstance(self.scope.get(varn), Importation)
                    # unused ones will get an unused import warning
                    and self.scope[varn].used):
                self.report(messages.ImportShadowedByLoopVar,
                            node, varn, self.scope[varn].source)

        self.handle_children(node)

    def NAME(self, node):
        """Handle occurrence of Name (which can be a load/store/delete
        access.)"""
        # Locate the name in locals / function / globals scopes.
        if isinstance(node.ctx, (ast.Load, ast.AugLoad)):
            self.handle_node_load(node)
            if (node.id == 'locals' and isinstance(self.scope, FunctionScope)
                    and isinstance(node.parent, ast.Call)):
                # we are doing locals() call in current scope
                self.scope.uses_locals = True
        elif isinstance(node.ctx, (ast.Store, ast.AugStore)):
            self.handle_node_store(node)
        elif isinstance(node.ctx, ast.Del):
            self.handle_node_delete(node)
        else:
            # must be a Param context -- this only happens for names in function
            # arguments, but these aren't dispatched through here
            raise RuntimeError("Got impossible expression context: %r" % (node.ctx,))

    def CALL(self, node):
        f = node.func
        if isinstance(f, ast.Name):
            for scope in self.iter_visible_scopes():
                definition = scope.get(f.id)
                if definition:
                    if isinstance(definition, FunctionDefinition):
                        definition.signature.checkCall(node, self, f.id)
                    break


        self.handle_children(node)

    def FUNCTIONDEF(self, node):
        for deco in node.decorator_list:
            self.handleNode(deco, node)
        self.add_binding(node, FunctionDefinition(node.name, node))
        self.LAMBDA(node)
        if self.settings.get('run_doctests', False):
            self.defer_function(lambda: self.handle_doctests(node))

    def LAMBDA(self, node):
        args = []
        annotations = []

        if PY2:
            def addArgs(arglist):
                for arg in arglist:
                    if isinstance(arg, ast.Tuple):
                        addArgs(arg.elts)
                    else:
                        if arg.id in args:
                            self.report(messages.DuplicateArgument,
                                        node, arg.id)
                        args.append(arg.id)
            addArgs(node.args.args)
            defaults = node.args.defaults
        else:
            for arg in node.args.args + node.args.kwonlyargs:
                annotations.append(arg.annotation)
                args.append(arg.arg)
            defaults = node.args.defaults + node.args.kw_defaults

        # Only for Python3 FunctionDefs
        is_py3_func = hasattr(node, 'returns')

        for arg_name in ('vararg', 'kwarg'):
            wildcard = getattr(node.args, arg_name)
            if not wildcard:
                continue
            args.append(getattr(wildcard, 'arg', wildcard))
            if is_py3_func:
                if PY34_GTE:
                    annotations.append(wildcard.annotation)
                else:
                    argannotation = arg_name + 'annotation'
                    annotations.append(getattr(node.args, argannotation))
        if is_py3_func:
            annotations.append(node.returns)

        if PY3:
            if len(set(args)) < len(args):
                for (idx, arg) in enumerate(args):
                    if arg in args[:idx]:
                        self.report(messages.DuplicateArgument, node, arg)

        for child in annotations + defaults:
            if child:
                self.handleNode(child, node)

        def runFunction():

            self.push_scope()
            for name in args:
                self.add_binding(node, Argument(name, node), report_redef=False)
            if isinstance(node.body, list):
                # case for FunctionDefs
                for stmt in node.body:
                    self.handleNode(stmt, node)
            else:
                # case for Lambdas
                self.handleNode(node.body, node)

            def checkUnusedAssignments():
                """Check to see if any assignments have not been used."""
                for name, binding in self.scope.unusedAssignments():
                    self.report(messages.UnusedVariable, binding.source, name)
            self.defer_assignment(checkUnusedAssignments)

            if PY2:
                def checkReturnWithArgumentInsideGenerator():
                    """Check to see if there are any return statements with
                    arguments but the function is a generator."""
                    if self.is_generator(node):
                        stmt = self.find_return_with_argument(node)
                        if stmt is not None:
                            self.report(messages.ReturnWithArgsInsideGenerator, stmt)
                self.defer_assignment(checkReturnWithArgumentInsideGenerator)
            self.pop_scope()

        self.defer_function(runFunction)

    def CLASSDEF(self, node):
        """Check names used in a class definition, including its decorators,
        base classes, and the body of its definition.

        Additionally, add its name to the current scope.

        """
        for deco in node.decorator_list:
            self.handleNode(deco, node)
        for baseNode in node.bases:
            self.handleNode(baseNode, node)
        if not PY2:
            for keywordNode in node.keywords:
                self.handleNode(keywordNode, node)
        self.push_scope(ClassScope)
        if self.settings.get('run_doctests', False):
            self.defer_function(lambda: self.handle_doctests(node))
        for stmt in node.body:
            self.handleNode(stmt, node)
        self.pop_scope()
        self.add_binding(node, ClassDefinition(node.name, node))

    def ASSIGN(self, node):
        self.handleNode(node.value, node)
        for target in node.targets:
            self.handleNode(target, node)

    def AUGASSIGN(self, node):
        self.handle_node_load(node.target)
        self.handleNode(node.value, node)
        self.handleNode(node.target, node)

    def IMPORT(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            importation = Importation(name, node)
            self.add_binding(node, importation)

    def IMPORTFROM(self, node):
        if node.module == '__future__':
            if not self.futures_allowed:
                self.report(messages.LateFutureImport,
                            node, [n.name for n in node.names])
        else:
            self.futures_allowed = False

        for alias in node.names:
            if alias.name == '*':
                self.scope.importStarred = True
                self.report(messages.ImportStarUsed, node, node.module)
                continue
            name = alias.asname or alias.name
            importation = Importation(name, node)
            if node.module == '__future__':
                importation.used = (self.scope, node)
            self.add_binding(node, importation)

    def TRY(self, node):
        handler_names = []
        # List the exception handlers
        for handler in node.handlers:
            if isinstance(handler.type, ast.Tuple):
                for exc_type in handler.type.elts:
                    handler_names.append(node_name(exc_type))
            elif handler.type:
                handler_names.append(node_name(handler.type))
        # Memorize the except handlers and process the body
        self.except_handlers.append(handler_names)
        for child in node.body:
            self.handleNode(child, node)
        self.except_handlers.pop()
        # Process the other nodes: "except:", "else:", "finally:"
        for child in ast.iter_child_nodes(node):
            if child not in node.body:
                self.handleNode(child, node)

    TRYEXCEPT = TRY

    def EXCEPTHANDLER(self, node):
        # 3.x: in addition to handling children, we must handle the name of
        # the exception, which is not a Name node, but a simple string.
        if node.type is None:
            self.report(messages.BareExcept, node)
        if isinstance(node.name, str):
            self.handle_node_store(node)
        self.handle_children(node)
