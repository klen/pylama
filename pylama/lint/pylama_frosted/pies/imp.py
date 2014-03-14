from __future__ import absolute_import

from imp import *

from .version_info import PY2

if PY2:
    reload = reload
