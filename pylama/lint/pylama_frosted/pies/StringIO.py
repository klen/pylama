from __future__ import absolute_import

from .version_info import PY3

if PY3:
    from StringIO import *
else:
    try:
        from cStringIO import *
    except ImportError:
        from StringIO import *
