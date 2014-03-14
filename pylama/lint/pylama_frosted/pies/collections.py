from __future__ import absolute_import

from collections import *

from .version_info import PY2

if PY2:
    from UserString import *
    from UserList import *

    import sys
    if sys.version_info < (2, 7):
        from ordereddict import OrderedDict
