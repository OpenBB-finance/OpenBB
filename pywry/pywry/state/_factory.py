"""Internal factory functions for state stores.

This module contains the factory functions to avoid circular imports
between __init__.py and server.py.
"""

from __future__ import annotations

import os
import uuid

from functools import lru_cache
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .base import (
        ConnectionRouter,
        EventBus,
        SessionStore,
        WidgetStore,
    )

# pylint: disable=wrong-import-position
from .memory import (
    MemoryConnectionRouter,
    MemoryEventBus,
    MemorySessionStore,
    MemoryWidgetStore,
)
from .types import StateBackend


# pylint: enable=wrong-import-position


class _WorkerIdHolder:
    """Holder for worker ID to avoid global statement."""

    value: str | None = None


_worker_id_holder = _WorkerIdHolder()


def get_worker_id() -> str:
    """Get the unique worker ID for this process.

    The worker ID is used for connection routing and callback dispatch
    in multi-worker deployments.

    Returns
    -------
    str
        Unique worker identifier.
    """
    if _worker_id_holder.value is None:
        # Check environment variable first
        _worker_id_holder.value = os.environ.get("PYWRY_DEPLOY__WORKER_ID")
        if not _worker_id_holder.value:
            # Generate a unique ID for this worker
            _worker_id_holder.value = f"worker-{uuid.uuid4().hex[:8]}"
    return _worker_id_holder.value


def get_state_backend() -> StateBackend:
    """Get the configured state backend.

    Returns
    -------
    StateBackend
        The configured backend (MEMORY or REDIS).
    """
    backend = os.environ.get("PYWRY_DEPLOY__STATE_BACKEND", "memory").lower()
    if backend == "redis":
        return StateBackend.REDIS
    return StateBackend.MEMORY


def is_deploy_mode() -> bool:
    """Check if running in deploy mode.

    Deploy mode enables:
    - Redis state backend (if configured)
    - Multi-worker support
    - External state storage
    - Session/RBAC support

    Returns
    -------
    bool
        True if running in deploy mode.
    """
    # Check for explicit deploy mode flag
    deploy_mode = os.environ.get("PYWRY_DEPLOY_MODE", "").lower()
    if deploy_mode in ("1", "true", "yes", "on"):
        return True

    # If Redis backend is configured, that implies deploy mode
    backend = os.environ.get("PYWRY_DEPLOY__STATE_BACKEND", "").lower()
    if backend == "redis":
        return True

    # Check for PYWRY_HEADLESS with state backend
    headless = os.environ.get("PYWRY_HEADLESS", "").lower()
    return headless in ("1", "true", "yes", "on") and bool(backend)


def _get_deploy_settings() -> DeploySettings:
    """Get deploy settings from configuration.

    Imports lazily to avoid circular imports.
    """
    from pywry.config import DeploySettings

    return DeploySettings()


if TYPE_CHECKING:
    from pywry.config import DeploySettings


@lru_cache(maxsize=1)
def get_widget_store() -> WidgetStore:
    """Get the configured widget store instance.

    Uses Redis backend in deploy mode if configured, otherwise memory.

    Returns
    -------
    WidgetStore
        The widget store instance.
    """
    backend = get_state_backend()

    if backend == StateBackend.REDIS:
        from .redis import RedisWidgetStore

        settings = _get_deploy_settings()
        return RedisWidgetStore(
            redis_url=settings.redis_url,
            prefix=settings.redis_prefix,
            widget_ttl=settings.widget_ttl,
            pool_size=settings.redis_pool_size,
        )

    return MemoryWidgetStore()


@lru_cache(maxsize=1)
def get_event_bus() -> EventBus:
    """Get the configured event bus instance.

    Uses Redis Pub/Sub in deploy mode if configured, otherwise memory.

    Returns
    -------
    EventBus
        The event bus instance.
    """
    backend = get_state_backend()

    if backend == StateBackend.REDIS:
        from .redis import RedisEventBus

        settings = _get_deploy_settings()
        return RedisEventBus(
            redis_url=settings.redis_url,
            prefix=settings.redis_prefix,
            pool_size=settings.redis_pool_size,
        )

    return MemoryEventBus()


@lru_cache(maxsize=1)
def get_connection_router() -> ConnectionRouter:
    """Get the configured connection router instance.

    Uses Redis in deploy mode if configured, otherwise memory.

    Returns
    -------
    ConnectionRouter
        The connection router instance.
    """
    backend = get_state_backend()

    if backend == StateBackend.REDIS:
        from .redis import RedisConnectionRouter

        settings = _get_deploy_settings()
        return RedisConnectionRouter(
            redis_url=settings.redis_url,
            prefix=settings.redis_prefix,
            connection_ttl=settings.connection_ttl,
            pool_size=settings.redis_pool_size,
        )

    return MemoryConnectionRouter()


@lru_cache(maxsize=1)
def get_session_store() -> SessionStore:
    """Get the configured session store instance.

    Uses Redis in deploy mode if configured, otherwise memory.

    Returns
    -------
    SessionStore
        The session store instance.
    """
    backend = get_state_backend()

    if backend == StateBackend.REDIS:
        from .redis import RedisSessionStore

        settings = _get_deploy_settings()
        return RedisSessionStore(
            redis_url=settings.redis_url,
            prefix=settings.redis_prefix,
            default_ttl=settings.session_ttl,
            pool_size=settings.redis_pool_size,
        )

    return MemorySessionStore()


def clear_state_caches() -> None:
    """Clear all cached state store instances.

    Call this to force re-creation of stores (e.g., after config change).
    """
    get_widget_store.cache_clear()
    get_event_bus.cache_clear()
    get_connection_router.cache_clear()
    get_session_store.cache_clear()
