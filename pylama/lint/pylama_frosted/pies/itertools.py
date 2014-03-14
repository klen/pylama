from __future__ import absolute_import

from itertools import *

from .version_info import PY2

if PY2:
    filterfalse = ifilterfalse
