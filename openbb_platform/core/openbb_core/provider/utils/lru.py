"""Utilities for LRU caching."""

# pylint: disable=W0613

import time
from collections.abc import Callable
from functools import lru_cache, update_wrapper
from math import floor
from typing import Any


def ttl_cache(maxsize: int = 128, typed: bool = False, ttl: int = -1):
    """Cache a function's return value each ttl seconds."""
    if ttl <= 0:
        ttl = 65536

    hash_gen = _ttl_hash_gen(ttl)

    def wrapper(func: Callable) -> Callable:
        """Wrap the function for ttl_cache."""

        @lru_cache(maxsize, typed)
        def ttl_func(ttl_hash, *args, **kwargs):
            return func(*args, **kwargs)

        def wrapped(*args, **kwargs) -> Any:
            """Wrap the function for ttl_cache."""
            th = next(hash_gen)
            return ttl_func(th, *args, **kwargs)

        return update_wrapper(wrapped, func)

    return wrapper


def _ttl_hash_gen(seconds: int):
    start_time = time.time()

    while True:
        yield floor((time.time() - start_time) / seconds)
