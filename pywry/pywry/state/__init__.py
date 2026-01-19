"""PyWry state management package.

Provides pluggable state storage backends for horizontal scaling.
The default is in-memory storage for single-process deployments.
Redis backend is available for multi-worker production deployments.

Usage
-----
For single-process (default):
    from pywry.state import get_widget_store, get_event_bus

For Redis backend (deploy mode):
    # Configure via environment variables:
    # PYWRY_DEPLOY__STATE_BACKEND=redis
    # PYWRY_DEPLOY__REDIS_URL=redis://localhost:6379/0

Examples
--------
>>> from pywry.state import get_widget_store
>>> store = get_widget_store()
>>> await store.register("widget-123", "<h1>Hello</h1>")
>>> html = await store.get_html("widget-123")
"""

from __future__ import annotations

from ._factory import (
    clear_state_caches,
    get_connection_router,
    get_event_bus,
    get_session_store,
    get_state_backend,
    get_widget_store,
    get_worker_id,
    is_deploy_mode,
)
from .base import ConnectionRouter, EventBus, SessionStore, WidgetStore
from .callbacks import (
    CallbackRegistry,
    get_callback_registry,
    reset_callback_registry,
)
from .memory import (
    MemoryConnectionRouter,
    MemoryEventBus,
    MemorySessionStore,
    MemoryWidgetStore,
)
from .server import ServerStateManager, get_server_state, reset_server_state
from .sync_helpers import run_async, run_async_fire_and_forget
from .types import (
    ConnectionInfo,
    EventMessage,
    StateBackend,
    UserSession,
    WidgetData,
)


__all__ = [
    # Callbacks
    "CallbackRegistry",
    # Types
    "ConnectionInfo",
    # Abstract interfaces
    "ConnectionRouter",
    "EventBus",
    "EventMessage",
    # Memory implementations
    "MemoryConnectionRouter",
    "MemoryEventBus",
    "MemorySessionStore",
    "MemoryWidgetStore",
    # Server state
    "ServerStateManager",
    "SessionStore",
    "StateBackend",
    "UserSession",
    "WidgetData",
    "WidgetStore",
    # Factory functions
    "clear_state_caches",
    "get_callback_registry",
    "get_connection_router",
    "get_event_bus",
    "get_server_state",
    "get_session_store",
    "get_state_backend",
    "get_widget_store",
    "get_worker_id",
    "is_deploy_mode",
    "reset_callback_registry",
    "reset_server_state",
    # Sync helpers
    "run_async",
    "run_async_fire_and_forget",
]
