"""In-memory state store implementations.

Default backend for single-process deployments and development.
"""

from __future__ import annotations

import asyncio
import contextlib
import time

from typing import TYPE_CHECKING, Any

from .base import ConnectionRouter, EventBus, SessionStore, WidgetStore
from .types import ConnectionInfo, EventMessage, UserSession, WidgetData


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class MemoryWidgetStore(WidgetStore):
    """In-memory widget store for single-process deployments.

    Thread-safe implementation using asyncio locks.
    """

    def __init__(self) -> None:
        """Initialize the memory widget store."""
        self._widgets: dict[str, WidgetData] = {}
        self._lock = asyncio.Lock()

    async def register(
        self,
        widget_id: str,
        html: str,
        token: str | None = None,
        owner_worker_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a widget with its HTML content."""
        async with self._lock:
            self._widgets[widget_id] = WidgetData(
                widget_id=widget_id,
                html=html,
                token=token,
                created_at=time.time(),
                owner_worker_id=owner_worker_id,
                metadata=metadata or {},
            )

    async def get(self, widget_id: str) -> WidgetData | None:
        """Get complete widget data."""
        async with self._lock:
            return self._widgets.get(widget_id)

    async def get_html(self, widget_id: str) -> str | None:
        """Get widget HTML content."""
        async with self._lock:
            widget = self._widgets.get(widget_id)
            return widget.html if widget else None

    async def get_token(self, widget_id: str) -> str | None:
        """Get widget authentication token."""
        async with self._lock:
            widget = self._widgets.get(widget_id)
            return widget.token if widget else None

    async def exists(self, widget_id: str) -> bool:
        """Check if a widget exists."""
        async with self._lock:
            return widget_id in self._widgets

    async def delete(self, widget_id: str) -> bool:
        """Delete a widget."""
        async with self._lock:
            if widget_id in self._widgets:
                del self._widgets[widget_id]
                return True
            return False

    async def list_active(self) -> list[str]:
        """List all active widget IDs."""
        async with self._lock:
            return list(self._widgets.keys())

    async def update_html(self, widget_id: str, html: str) -> bool:
        """Update widget HTML content."""
        async with self._lock:
            if widget_id in self._widgets:
                self._widgets[widget_id].html = html
                return True
            return False

    async def update_token(self, widget_id: str, token: str) -> bool:
        """Update widget authentication token."""
        async with self._lock:
            if widget_id in self._widgets:
                self._widgets[widget_id].token = token
                return True
            return False

    async def count(self) -> int:
        """Get the number of active widgets."""
        async with self._lock:
            return len(self._widgets)


class MemoryEventBus(EventBus):
    """In-memory event bus for single-process deployments.

    Uses asyncio.Queue for inter-task communication.
    """

    def __init__(self) -> None:
        """Initialize the memory event bus."""
        self._channels: dict[str, list[asyncio.Queue[EventMessage]]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, channel: str, event: EventMessage) -> None:
        """Publish an event to a channel."""
        async with self._lock:
            queues = self._channels.get(channel, [])
            for q in queues:
                with contextlib.suppress(asyncio.QueueFull):
                    q.put_nowait(event)

    async def subscribe(self, channel: str) -> AsyncIterator[EventMessage]:
        """Subscribe to events on a channel."""
        q: asyncio.Queue[EventMessage] = asyncio.Queue(maxsize=1000)

        async with self._lock:
            if channel not in self._channels:
                self._channels[channel] = []
            self._channels[channel].append(q)

        try:
            while True:
                event = await q.get()
                yield event
        finally:
            async with self._lock:
                if channel in self._channels:
                    with contextlib.suppress(ValueError):
                        self._channels[channel].remove(q)
                    if not self._channels[channel]:
                        del self._channels[channel]

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel (clears all subscriptions)."""
        async with self._lock:
            self._channels.pop(channel, None)


class MemoryConnectionRouter(ConnectionRouter):
    """In-memory connection router for single-process deployments."""

    def __init__(self) -> None:
        """Initialize the memory connection router."""
        self._connections: dict[str, ConnectionInfo] = {}
        self._worker_connections: dict[str, set[str]] = {}
        self._lock = asyncio.Lock()

    async def register_connection(
        self,
        widget_id: str,
        worker_id: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Register that a widget is connected to a specific worker."""
        async with self._lock:
            now = time.time()
            self._connections[widget_id] = ConnectionInfo(
                widget_id=widget_id,
                worker_id=worker_id,
                connected_at=now,
                last_heartbeat=now,
                user_id=user_id,
                session_id=session_id,
            )
            if worker_id not in self._worker_connections:
                self._worker_connections[worker_id] = set()
            self._worker_connections[worker_id].add(widget_id)

    async def get_connection_info(self, widget_id: str) -> ConnectionInfo | None:
        """Get connection information for a widget."""
        async with self._lock:
            return self._connections.get(widget_id)

    async def get_owner(self, widget_id: str) -> str | None:
        """Get the worker ID that owns this widget's connection."""
        async with self._lock:
            conn = self._connections.get(widget_id)
            return conn.worker_id if conn else None

    async def refresh_heartbeat(self, widget_id: str) -> bool:
        """Refresh the heartbeat timestamp for a connection."""
        async with self._lock:
            if widget_id in self._connections:
                self._connections[widget_id].last_heartbeat = time.time()
                return True
            return False

    async def unregister_connection(self, widget_id: str) -> bool:
        """Unregister a connection."""
        async with self._lock:
            if widget_id in self._connections:
                conn = self._connections.pop(widget_id)
                if conn.worker_id in self._worker_connections:
                    self._worker_connections[conn.worker_id].discard(widget_id)
                return True
            return False

    async def list_worker_connections(self, worker_id: str) -> list[str]:
        """List all widget IDs connected to a specific worker."""
        async with self._lock:
            return list(self._worker_connections.get(worker_id, set()))


class MemorySessionStore(SessionStore):
    """In-memory session store for RBAC support.

    For single-process deployments and development.
    """

    def __init__(self) -> None:
        """Initialize the memory session store."""
        self._sessions: dict[str, UserSession] = {}
        self._user_sessions: dict[str, set[str]] = {}
        # Simple role-based permissions: role -> set of permissions
        self._role_permissions: dict[str, set[str]] = {
            "admin": {"read", "write", "admin"},
            "editor": {"read", "write"},
            "viewer": {"read"},
        }
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        roles: list[str] | None = None,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UserSession:
        """Create a new user session."""
        async with self._lock:
            now = time.time()
            expires_at = now + ttl if ttl else None

            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                roles=roles or [],
                created_at=now,
                expires_at=expires_at,
                metadata=metadata or {},
            )

            self._sessions[session_id] = session
            if user_id not in self._user_sessions:
                self._user_sessions[user_id] = set()
            self._user_sessions[user_id].add(session_id)

            return session

    async def get_session(self, session_id: str) -> UserSession | None:
        """Get a session by ID."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            # Check expiry
            if session.expires_at and session.expires_at < time.time():
                # Session expired, clean up
                self._sessions.pop(session_id, None)
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(session_id)
                return None

            return session

    async def validate_session(self, session_id: str) -> bool:
        """Validate a session is active and not expired."""
        session = await self.get_session(session_id)
        return session is not None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        async with self._lock:
            if session_id in self._sessions:
                session = self._sessions.pop(session_id)
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(session_id)
                return True
            return False

    async def refresh_session(self, session_id: str, extend_ttl: int | None = None) -> bool:
        """Refresh a session's expiry time."""
        async with self._lock:
            if session_id not in self._sessions:
                return False

            session = self._sessions[session_id]

            # Check if already expired
            if session.expires_at and session.expires_at < time.time():
                return False

            # Extend TTL if provided
            if extend_ttl is not None:
                session.expires_at = time.time() + extend_ttl
            elif session.expires_at is not None:
                # Use original TTL duration
                original_ttl = session.expires_at - session.created_at
                session.expires_at = time.time() + original_ttl

            return True

    async def list_user_sessions(self, user_id: str) -> list[UserSession]:
        """List all sessions for a user."""
        async with self._lock:
            session_ids = self._user_sessions.get(user_id, set())
            sessions = []
            now = time.time()

            for sid in list(session_ids):
                session = self._sessions.get(sid)
                if session:
                    # Check expiry
                    if session.expires_at and session.expires_at < now:
                        # Clean up expired
                        self._sessions.pop(sid, None)
                        session_ids.discard(sid)
                    else:
                        sessions.append(session)

            return sessions

    async def check_permission(
        self,
        session_id: str,
        _resource_type: str,
        _resource_id: str,
        permission: str,
    ) -> bool:
        """Check if a session has permission to access a resource.

        Currently implements simple role-based access control.
        Resource-specific permissions can be added via metadata.
        """
        session = await self.get_session(session_id)
        if session is None:
            return False

        # Check role-based permissions
        for role in session.roles:
            role_perms = self._role_permissions.get(role, set())
            if permission in role_perms:
                return True

        return False

    def set_role_permissions(self, role: str, permissions: set[str]) -> None:
        """Configure permissions for a role (sync for setup)."""
        self._role_permissions[role] = permissions


# Factory function for creating memory stores
def create_memory_stores() -> tuple[
    MemoryWidgetStore,
    MemoryEventBus,
    MemoryConnectionRouter,
    MemorySessionStore,
]:
    """Create all in-memory state stores.

    Returns
    -------
    tuple
        (widget_store, event_bus, connection_router, session_store)
    """
    return (
        MemoryWidgetStore(),
        MemoryEventBus(),
        MemoryConnectionRouter(),
        MemorySessionStore(),
    )
