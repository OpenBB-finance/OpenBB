import asyncio
import functools
import pkg_resources
import threading
import weakref
from time import time


__author__ = "Martin Larralde"
__email__ = "martin.larralde@ens-paris-saclay.fr"
__license__ = "BSD"
__version__ = pkg_resources.resource_string(__name__, "_version.txt").decode('utf-8').strip()


class cached_property(property):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    _sentinel = object()
    _update_wrapper = functools.update_wrapper

    def __init__(self, func):
        self.cache = weakref.WeakKeyDictionary()
        self.func = func
        self._update_wrapper(func)

    def __get__(self, obj, cls):
        if obj is None:
            return self

        if asyncio and asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj)

        value = self.cache.get(obj, self._sentinel)
        if value is self._sentinel:
            value = self.cache[obj] = self.func(obj)

        return value

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __set__(self, obj, value):
        self.cache[obj] = value

    def __delete__(self, obj):
        del self.cache[obj]

    def _wrap_in_coroutine(self, obj):

        @functools.wraps(obj)
        @asyncio.coroutine
        def wrapper():
            value = self.cache.get(obj, self._sentinel)
            if value is self._sentinel:
                self.cache[obj] = value = asyncio.ensure_future(self.func(obj))
            return value

        return wrapper()


class threaded_cached_property(cached_property):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, func):
        super(threaded_cached_property, self).__init__(func)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        if obj is None:
            return self
        with self.lock:
            return super(threaded_cached_property, self).__get__(obj, cls)

    def __set__(self, obj, value):
        with self.lock:
            super(threaded_cached_property, self).__set__(obj, value)

    def __delete__(self, obj):
        with self.lock:
            super(threaded_cached_property, self).__delete__(obj)


class cached_property_with_ttl(cached_property):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Setting the ttl to a number expresses how long
    the property will last before being timed out.
    """

    def __init__(self, ttl=None):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        super(cached_property_with_ttl, self).__init__(func)

    def __call__(self, func):
        super(cached_property_with_ttl, self).__init__(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        if obj in self.cache:
            value, last_updated = self.cache[obj]
            if not self.ttl or self.ttl > now - last_updated:
                return value

        value, _ = self.cache[obj] = (self.func(obj), now)
        return value

    def __set__(self, obj, value):
        super(cached_property_with_ttl, self).__set__(obj, (value, time()))


# Aliases to make cached_property_with_ttl easier to use
cached_property_ttl = cached_property_with_ttl
timed_cached_property = cached_property_with_ttl


class threaded_cached_property_with_ttl(
    cached_property_with_ttl, threaded_cached_property
):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, ttl=None):
        super(threaded_cached_property_with_ttl, self).__init__(ttl)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__get__(obj, cls)

    def __set__(self, obj, value):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__set__(obj, value)

    def __delete__(self, obj):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__delete__(obj)


# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl
