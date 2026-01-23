"""Server state manager for deploy mode.

This module provides a unified interface for managing server state across
single-process and multi-process (horizontally scaled) deployments.

In deploy mode (PYWRY_HEADLESS + Redis backend):
- Widget state is stored in Redis for cross-worker access
- Connections are tracked per-worker with routing via Redis
- Events are broadcast via Redis Pub/Sub
- Sessions are managed centrally with RBAC

In local mode:
- All state is kept in-memory within the process
- No external dependencies required
"""

from __future__ import annotations

import asyncio
import queue
import threading
import uuid

from typing import TYPE_CHECKING, Any, cast

from ._factory import (
    get_connection_router,
    get_event_bus,
    get_session_store,
    get_widget_store,
    get_worker_id,
    is_deploy_mode,
)
from .callbacks import get_callback_registry
from .types import EventMessage, WidgetData


if TYPE_CHECKING:
    from fastapi import WebSocket

    from .base import ConnectionRouter, EventBus, SessionStore, WidgetStore
    from .callbacks import CallbackRegistry


class ServerStateManager:  # pylint: disable=too-many-instance-attributes
    """Unified state manager for PyWry server.

    Automatically selects the appropriate storage backend based on
    deploy mode configuration. Provides both sync and async interfaces
    where appropriate.

    Attributes
    ----------
    deploy_mode : bool
        True if running in horizontally scaled deploy mode.
    worker_id : str
        Unique identifier for this worker process.
    """

    def __init__(self) -> None:
        """Initialize the state manager."""
        self._initialized = False
        self._lock = threading.Lock()
        self._async_lock: asyncio.Lock | None = None

        # Core state (shared with original _ServerState)
        self.server: Any = None
        self.server_thread: threading.Thread | None = None
        self.server_loop: Any = None
        self.app: Any = None
        self.port: int | None = None
        self.host: str | None = None
        self.widget_prefix: str = "/widget"
        self.shutdown_event: asyncio.Event | None = None
        self.disconnect_event: threading.Event = threading.Event()
        self.internal_api_token: str | None = None

        # Sync callback queue for the callback processor thread
        self.callback_queue: queue.Queue[Any] = queue.Queue()

        # In-process connection map for local WebSocket handling
        # Even in deploy mode, WebSocket objects are per-worker
        self._local_connections: dict[str, WebSocket] = {}
        self._local_event_queues: dict[str, asyncio.Queue[Any]] = {}

        # Local mode: widget storage for non-deploy mode
        self._local_widgets: dict[str, dict[str, Any]] = {}
        self._local_widget_tokens: dict[str, str] = {}

        # Store references - lazily initialized
        self._widget_store: WidgetStore | None = None
        self._event_bus: EventBus | None = None
        self._connection_router: ConnectionRouter | None = None
        self._session_store: SessionStore | None = None
        self._callback_registry: CallbackRegistry | None = None

    @property
    def deploy_mode(self) -> bool:
        """Check if running in deploy mode."""
        return is_deploy_mode()

    @property
    def worker_id(self) -> str:
        """Get this worker's unique ID."""
        return get_worker_id()

    def _ensure_initialized(self) -> None:
        """Ensure state stores are initialized."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Initialize stores based on deploy mode
            self._widget_store = get_widget_store()
            self._event_bus = get_event_bus()
            self._connection_router = get_connection_router()
            self._session_store = get_session_store()
            self._callback_registry = get_callback_registry()
            self._initialized = True

    async def _get_async_lock(self) -> asyncio.Lock:
        """Get or create the async lock."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    # --- Widget Management ---

    async def register_widget(
        self,
        widget_id: str,
        html: str,
        token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a widget with its HTML content.

        In deploy mode, this stores in Redis. In local mode,
        stores in-memory.

        Parameters
        ----------
        widget_id : str
            Unique widget identifier.
        html : str
            The widget's HTML content.
        token : str | None
            Optional per-widget authentication token.
        metadata : dict | None
            Additional metadata (title, theme, etc.).
        """
        self._ensure_initialized()

        if self.deploy_mode:
            # Store in distributed state
            await self._widget_store.register(  # type: ignore[union-attr]
                widget_id=widget_id,
                html=html,
                token=token,
                owner_worker_id=self.worker_id,
                metadata=metadata,
            )
        else:
            self._local_widgets[widget_id] = {
                "html": html,
                "callbacks": {},
                "metadata": metadata or {},
            }
            if token:
                self._local_widget_tokens[widget_id] = token

    async def get_widget(self, widget_id: str) -> WidgetData | None:
        """Get widget data by ID.

        Parameters
        ----------
        widget_id : str
            The widget ID to retrieve.

        Returns
        -------
        WidgetData | None
            Widget data if found.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            return await self._widget_store.get(widget_id)  # type: ignore[union-attr]

        # Local mode - convert dict to WidgetData
        if widget_id not in self._local_widgets:
            return None

        local = self._local_widgets[widget_id]
        return WidgetData(
            widget_id=widget_id,
            html=local["html"],
            token=self._local_widget_tokens.get(widget_id),
            owner_worker_id=self.worker_id,
            metadata=local.get("metadata", {}),
        )

    async def get_widget_html(self, widget_id: str) -> str | None:
        """Get widget HTML content.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        str | None
            The HTML content if widget exists.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            result = await self._widget_store.get_html(widget_id)  # type: ignore[union-attr]
            return cast("str | None", result)

        # Local mode
        if widget_id in self._local_widgets:
            return cast("str", self._local_widgets[widget_id]["html"])
        return None

    async def update_widget_html(self, widget_id: str, html: str) -> bool:
        """Update widget HTML content.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        html : str
            New HTML content.

        Returns
        -------
        bool
            True if update succeeded.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            return await self._widget_store.update_html(widget_id, html)  # type: ignore[union-attr]

        # Local mode
        if widget_id in self._local_widgets:
            self._local_widgets[widget_id]["html"] = html
            return True
        return False

    async def widget_exists(self, widget_id: str) -> bool:
        """Check if a widget exists.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if widget exists.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            return await self._widget_store.exists(widget_id)  # type: ignore[union-attr]

        return widget_id in self._local_widgets

    async def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if widget was removed.
        """
        self._ensure_initialized()

        # Clean up callbacks
        if self._callback_registry:
            await self._callback_registry.unregister_widget(widget_id)

        if self.deploy_mode:
            return await self._widget_store.delete(widget_id)  # type: ignore[union-attr]

        # Local mode
        if widget_id in self._local_widgets:
            del self._local_widgets[widget_id]
            if widget_id in self._local_widget_tokens:
                del self._local_widget_tokens[widget_id]
            return True
        return False

    async def list_widgets(self) -> list[str]:
        """List all widget IDs.

        Returns
        -------
        list[str]
            List of widget IDs.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            return await self._widget_store.list_active()  # type: ignore[union-attr]

        return list(self._local_widgets.keys())

    @property
    def widgets(self) -> dict[str, dict[str, Any]]:
        """Get local widgets dict.

        Note: In deploy mode, this only returns widgets that were
        created by this worker and may not reflect the full state.
        Use async methods for accurate state in deploy mode.
        """
        return self._local_widgets

    @property
    def widget_tokens(self) -> dict[str, str]:
        """Get local widget tokens dict."""
        return self._local_widget_tokens

    @property
    def connections(self) -> dict[str, Any]:
        """Get local connections dict."""
        return self._local_connections

    @property
    def event_queues(self) -> dict[str, asyncio.Queue[Any]]:
        """Get local event queues dict."""
        return self._local_event_queues

    # --- Connection Management ---

    async def register_connection(
        self,
        widget_id: str,
        websocket: WebSocket,
    ) -> asyncio.Queue[Any]:
        """Register a WebSocket connection for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        websocket : WebSocket
            The WebSocket connection.

        Returns
        -------
        asyncio.Queue
            Event queue for this connection.
        """
        self._ensure_initialized()

        # Create event queue for this connection
        event_queue: asyncio.Queue[Any] = asyncio.Queue()
        self._local_event_queues[widget_id] = event_queue
        self._local_connections[widget_id] = websocket

        if self.deploy_mode:
            # Register in distributed router
            await self._connection_router.register_connection(  # type: ignore[union-attr]
                widget_id=widget_id,
                worker_id=self.worker_id,
            )

        return event_queue

    async def unregister_connection(self, widget_id: str) -> None:
        """Unregister a WebSocket connection.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        """
        self._ensure_initialized()

        # Clean up local state
        if widget_id in self._local_connections:
            del self._local_connections[widget_id]
        if widget_id in self._local_event_queues:
            del self._local_event_queues[widget_id]

        if self.deploy_mode:
            await self._connection_router.unregister_connection(widget_id)  # type: ignore[union-attr]

    async def get_connection(self, widget_id: str) -> WebSocket | None:
        """Get the WebSocket connection for a widget (local only).

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        WebSocket | None
            The connection if it exists on this worker.
        """
        return self._local_connections.get(widget_id)

    async def get_event_queue(self, widget_id: str) -> asyncio.Queue[Any] | None:
        """Get the event queue for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        asyncio.Queue | None
            The event queue if widget is connected on this worker.
        """
        return self._local_event_queues.get(widget_id)

    # --- Callback Management ---

    async def register_callback(
        self,
        widget_id: str,
        event_type: str,
        callback: Any,
    ) -> None:
        """Register a callback for widget events.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type to handle.
        callback : callable
            The callback function.
        """
        self._ensure_initialized()

        # Register in local callback registry
        await self._callback_registry.register(widget_id, event_type, callback)  # type: ignore[union-attr]

        if widget_id in self._local_widgets:
            if "callbacks" not in self._local_widgets[widget_id]:
                self._local_widgets[widget_id]["callbacks"] = {}
            self._local_widgets[widget_id]["callbacks"][event_type] = callback

    async def get_callback(self, widget_id: str, event_type: str) -> Any | None:
        """Get a callback for a widget event.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.

        Returns
        -------
        callable | None
            The callback if registered.
        """
        self._ensure_initialized()

        registration = await self._callback_registry.get(widget_id, event_type)  # type: ignore[union-attr]
        if registration:
            return registration.callback
        return None

    async def invoke_callback(
        self,
        widget_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> tuple[bool, Any]:
        """Invoke a callback for a widget event.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.
        data : dict
            Event data.

        Returns
        -------
        tuple[bool, Any]
            (success, result) tuple.
        """
        self._ensure_initialized()
        return await self._callback_registry.invoke(widget_id, event_type, data)  # type: ignore[union-attr]

    # --- Event Broadcasting ---

    async def broadcast_event(
        self,
        widget_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Broadcast an event to a widget.

        In deploy mode, uses Redis Pub/Sub to reach the correct worker.
        In local mode, sends directly to the local event queue.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.
        data : dict
            Event data.
        """
        self._ensure_initialized()

        if self.deploy_mode:
            # Publish via Redis to reach the correct worker
            event_msg = EventMessage(
                event_type=event_type,
                widget_id=widget_id,
                data=data,
                source_worker_id=self.worker_id,
            )
            await self._event_bus.publish(  # type: ignore[union-attr]
                channel=f"widget:{widget_id}",
                event=event_msg,
            )
        else:
            # Direct local delivery
            event_queue = self._local_event_queues.get(widget_id)
            if event_queue:
                await event_queue.put({"type": event_type, "data": data})

    async def send_to_widget(
        self,
        widget_id: str,
        event: dict[str, Any],
    ) -> bool:
        """Send an event to a specific widget's WebSocket.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event : dict
            The event to send.

        Returns
        -------
        bool
            True if event was queued for sending.
        """
        event_queue = self._local_event_queues.get(widget_id)
        if event_queue:
            await event_queue.put(event)
            return True

        # In deploy mode, try broadcasting to find the right worker
        if self.deploy_mode:
            event_msg = EventMessage(
                event_type=event.get("type", "message"),
                widget_id=widget_id,
                data=event.get("data", {}),
                source_worker_id=self.worker_id,
            )
            await self._event_bus.publish(  # type: ignore[union-attr]
                channel=f"widget:{widget_id}",
                event=event_msg,
            )
            return True

        return False

    # --- Session Management ---

    async def create_session(
        self,
        user_id: str,
        roles: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new user session.

        Parameters
        ----------
        user_id : str
            The user identifier.
        roles : list[str] | None
            User roles for RBAC.
        metadata : dict | None
            Additional session metadata.

        Returns
        -------
        str
            The session ID.
        """
        self._ensure_initialized()
        session_id = str(uuid.uuid4())
        session = await self._session_store.create_session(  # type: ignore[union-attr]
            session_id=session_id,
            user_id=user_id,
            roles=roles or ["viewer"],
            metadata=metadata,
        )
        return session.session_id

    async def get_session(self, session_id: str) -> Any | None:
        """Get a session by ID.

        Parameters
        ----------
        session_id : str
            The session ID.

        Returns
        -------
        UserSession | None
            The session if found.
        """
        self._ensure_initialized()
        return await self._session_store.get_session(session_id)  # type: ignore[union-attr]

    # --- Cleanup ---

    async def cleanup(self) -> None:
        """Clean up all state and connections."""
        self._ensure_initialized()

        # Close all local connections
        for widget_id in list(self._local_connections.keys()):
            await self.unregister_connection(widget_id)

        # Clear local state
        self._local_widgets.clear()
        self._local_widget_tokens.clear()


# Singleton holder
class _StateHolder:
    """Holds the singleton server state manager instance."""

    instance: ServerStateManager | None = None


def get_server_state() -> ServerStateManager:
    """Get the global server state manager.

    Returns
    -------
    ServerStateManager
        The singleton state manager instance.
    """
    if _StateHolder.instance is None:
        _StateHolder.instance = ServerStateManager()
    return _StateHolder.instance


def reset_server_state() -> None:
    """Reset the server state manager (for testing)."""
    _StateHolder.instance = ServerStateManager()
