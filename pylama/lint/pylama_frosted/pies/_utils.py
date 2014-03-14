"""pies/_utils.py.

Utils internal to the pies library and not meant for direct external usage.

Copyright (C) 2013  Timothy Edmund Crosley

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
import abc
import sys


def with_metaclass(meta, *bases):
    """Enables use of meta classes across Python Versions. taken from jinja2/_compat.py.

    Use it like this::

        class BaseForm(object):
            pass

        class FormType(type):
            pass

        class Form(with_metaclass(FormType, BaseForm)):
            pass

    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


def unmodified_isinstance(*bases):
    """When called in the form

    MyOverrideClass(unmodified_isinstance(BuiltInClass))

    it allows calls against passed in built in instances to pass even if there not a subclass

    """
    class UnmodifiedIsInstance(type):
        if sys.version_info[0] == 2 and sys.version_info[1] <= 6:

            @classmethod
            def __instancecheck__(cls, instance):
                if cls.__name__ in (str(base.__name__) for base in bases):
                    return isinstance(instance, bases)

                subclass = getattr(instance, '__class__', None)
                subtype = type(instance)
                instance_type = getattr(abc, '_InstanceType', None)
                if not instance_type:
                    class test_object:
                        pass
                    instance_type = type(test_object)
                if subtype is instance_type:
                    subtype = subclass
                if subtype is subclass or subclass is None:
                    return cls.__subclasscheck__(subtype)
                return (cls.__subclasscheck__(subclass) or cls.__subclasscheck__(subtype))
        else:
            @classmethod
            def __instancecheck__(cls, instance):
                if cls.__name__ in (str(base.__name__) for base in bases):
                    return isinstance(instance, bases)

                return type.__instancecheck__(cls, instance)

    return with_metaclass(UnmodifiedIsInstance, *bases)

