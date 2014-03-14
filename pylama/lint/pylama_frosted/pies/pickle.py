from __future__ import absolute_import

from .version_info import PY3

if PY3:
    from pickle import *
else:
    try:
        from cPickle import *
    except ImportError:
        from pickle import *
