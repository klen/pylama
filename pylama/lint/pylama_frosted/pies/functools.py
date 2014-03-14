from __future__ import absolute_import

import sys
from functools import *

from .version_info import PY2

if PY2:
    reduce = reduce

if sys.version_info < (3, 2):
    try:
        from threading import Lock
    except ImportError:
        from dummy_threading import Lock

    from .collections import OrderedDict

    def lru_cache(maxsize=100):
        """Least-recently-used cache decorator.

        Taking from: https://github.com/MiCHiLU/python-functools32/blob/master/functools32/functools32.py
        with slight modifications.

        If *maxsize* is set to None, the LRU features are disabled and the cache
        can grow without bound.

        Arguments to the cached function must be hashable.

        View the cache statistics named tuple (hits, misses, maxsize, currsize) with
        f.cache_info().  Clear the cache and statistics with f.cache_clear().
        Access the underlying function with f.__wrapped__.

        See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
        
        """
        def decorating_function(user_function, tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):
            hits, misses = [0], [0]
            kwd_mark = (object(),)          # separates positional and keyword args
            lock = Lock()

            if maxsize is None:
                CACHE = dict()

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    try:
                        result = CACHE[key]
                        hits[0] += 1
                        return result
                    except KeyError:
                        pass
                    result = user_function(*args, **kwds)
                    CACHE[key] = result
                    misses[0] += 1
                    return result
            else:
                CACHE = OrderedDict()

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    with lock:
                        cached = CACHE.get(key, None)
                        if cached:
                            del CACHE[key]
                            CACHE[key] = cached
                            hits[0] += 1
                            return cached
                    result = user_function(*args, **kwds)
                    with lock:
                        CACHE[key] = result     # record recent use of this key
                        misses[0] += 1
                        while len(CACHE) > maxsize:
                            CACHE.popitem(last=False)
                    return result

            def cache_info():
                """Report CACHE statistics."""
                with lock:
                    return _CacheInfo(hits[0], misses[0], maxsize, len(CACHE))

            def cache_clear():
                """Clear the CACHE and CACHE statistics."""
                with lock:
                    CACHE.clear()
                    hits[0] = misses[0] = 0

            wrapper.cache_info = cache_info
            wrapper.cache_clear = cache_clear
            return wrapper

        return decorating_function
