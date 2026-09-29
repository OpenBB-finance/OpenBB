"""Singleton metaclass implementation."""

from threading import Lock, RLock
from typing import Any


class SingletonMeta(type):
    """Singleton metaclass.

    Thread-safe: a class is instantiated exactly once, no matter how many
    threads race to create it. Locks are per-class and re-entrant, and the
    registry guard is never held while user code runs, so constructing one
    singleton from inside another's `__init__` cannot deadlock.
    """

    _instances: dict[type, Any] = {}
    _locks: dict[type, Any] = {}
    _locks_guard: Lock = Lock()

    def __call__(cls, *args, **kwargs) -> Any:
        """Singleton pattern implementation."""
        instance = cls._instances.get(cls)

        if instance is not None:
            return instance

        with cls._locks_guard:
            lock = cls._locks.get(cls)
            if lock is None:
                lock = cls._locks[cls] = RLock()

        with lock:
            instance = cls._instances.get(cls)
            if instance is None:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return instance
