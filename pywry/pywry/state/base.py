"""Abstract base classes for pluggable state storage.

These interfaces define the contract for state backends, enabling
horizontal scaling via Redis or other external stores.
"""

# pylint: disable=unnecessary-ellipsis
# Ellipsis (...) is the standard Python idiom for abstract method bodies

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from .types import ConnectionInfo, EventMessage, UserSession, WidgetData


class WidgetStore(ABC):
    """Abstract widget storage interface.

    Handles storage and retrieval of widget HTML content and metadata.
    Implementations must be thread-safe and support async operations.
    """

    @abstractmethod
    async def register(
        self,
        widget_id: str,
        html: str,
        token: str | None = None,
        owner_worker_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a widget with its HTML content.

        Parameters
        ----------
        widget_id : str
            Unique identifier for the widget.
        html : str
            The HTML content of the widget.
        token : str or None
            Optional per-widget authentication token.
        owner_worker_id : str or None
            ID of the worker that created this widget.
        metadata : dict[str, Any] or None
            Additional metadata (title, theme, etc.).
        """
        ...

    @abstractmethod
    async def get(self, widget_id: str) -> WidgetData | None:
        """Get complete widget data.

        Parameters
        ----------
        widget_id : str
            The widget ID to retrieve.

        Returns
        -------
        WidgetData or None
            The widget data if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_html(self, widget_id: str) -> str | None:
        """Get widget HTML content.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        str or None
            The HTML content if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_token(self, widget_id: str) -> str | None:
        """Get widget authentication token.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        str or None
            The token if set, None otherwise.
        """
        ...

    @abstractmethod
    async def exists(self, widget_id: str) -> bool:
        """Check if a widget exists.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if the widget exists.
        """
        ...

    @abstractmethod
    async def delete(self, widget_id: str) -> bool:
        """Delete a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID to delete.

        Returns
        -------
        bool
            True if the widget was deleted, False if it didn't exist.
        """
        ...

    @abstractmethod
    async def list_active(self) -> list[str]:
        """List all active widget IDs.

        Returns
        -------
        list[str]
            List of active widget IDs.
        """
        ...

    @abstractmethod
    async def update_html(self, widget_id: str, html: str) -> bool:
        """Update widget HTML content.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        html : str
            The new HTML content.

        Returns
        -------
        bool
            True if updated, False if widget doesn't exist.
        """
        ...

    @abstractmethod
    async def update_token(self, widget_id: str, token: str) -> bool:
        """Update widget authentication token.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        token : str
            The new authentication token.

        Returns
        -------
        bool
            True if updated, False if widget doesn't exist.
        """
        ...

    @abstractmethod
    async def count(self) -> int:
        """Get the number of active widgets.

        Returns
        -------
        int
            Number of active widgets.
        """
        ...


class EventBus(ABC):
    """Abstract event publishing interface.

    Handles cross-worker event delivery for callback dispatch
    and real-time updates.
    """

    @abstractmethod
    async def publish(self, channel: str, event: EventMessage) -> None:
        """Publish an event to a channel.

        Parameters
        ----------
        channel : str
            The channel name (e.g., "widget:{id}", "worker:{id}").
        event : EventMessage
            The event to publish.
        """
        ...

    @abstractmethod
    async def subscribe(self, channel: str) -> AsyncIterator[EventMessage]:
        """Subscribe to events on a channel.

        Parameters
        ----------
        channel : str
            The channel name.

        Yields
        ------
        EventMessage
            Events received on the channel.
        """
        ...
        yield  # type: ignore[misc]  # pragma: no cover

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Parameters
        ----------
        channel : str
            The channel to unsubscribe from.
        """
        ...


class ConnectionRouter(ABC):
    """Abstract connection routing interface.

    Tracks which worker owns which WebSocket connection,
    enabling cross-worker message routing.
    """

    @abstractmethod
    async def register_connection(
        self,
        widget_id: str,
        worker_id: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Register that a widget is connected to a specific worker.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        worker_id : str
            The worker ID that owns this connection.
        user_id : str or None
            Optional user ID for RBAC.
        session_id : str or None
            Optional session ID for tracking.
        """
        ...

    @abstractmethod
    async def get_connection_info(self, widget_id: str) -> ConnectionInfo | None:
        """Get connection information for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        ConnectionInfo or None
            Connection information if connected, None otherwise.
        """
        ...

    @abstractmethod
    async def get_owner(self, widget_id: str) -> str | None:
        """Get the worker ID that owns this widget's connection.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        str or None
            The worker ID if connected, None otherwise.
        """
        ...

    @abstractmethod
    async def refresh_heartbeat(self, widget_id: str) -> bool:
        """Refresh the heartbeat timestamp for a connection.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if refreshed, False if connection doesn't exist.
        """
        ...

    @abstractmethod
    async def unregister_connection(self, widget_id: str) -> bool:
        """Unregister a connection.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if unregistered, False if didn't exist.
        """
        ...

    @abstractmethod
    async def list_worker_connections(self, worker_id: str) -> list[str]:
        """List all widget IDs connected to a specific worker.

        Parameters
        ----------
        worker_id : str
            The worker ID.

        Returns
        -------
        list[str]
            List of widget IDs connected to this worker.
        """
        ...


class SessionStore(ABC):
    """Abstract session storage interface for RBAC support.

    Handles user sessions and access control for multi-tenant deployments.
    """

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        roles: list[str] | None = None,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UserSession:
        """Create a new user session.

        Parameters
        ----------
        session_id : str
            Unique session identifier.
        user_id : str
            User identifier.
        roles : list[str] or None
            User roles for access control.
        ttl : int or None
            Time-to-live in seconds (None for no expiry).
        metadata : dict[str, Any] or None
            Additional session metadata.

        Returns
        -------
        UserSession
            The created session.
        """
        ...

    @abstractmethod
    async def get_session(self, session_id: str) -> UserSession | None:
        """Get a session by ID.

        Parameters
        ----------
        session_id : str
            The session ID.

        Returns
        -------
        UserSession or None
            The session if found and not expired, None otherwise.
        """
        ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> bool:
        """Validate a session is active and not expired.

        Parameters
        ----------
        session_id : str
            The session ID.

        Returns
        -------
        bool
            True if the session is valid.
        """
        ...

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Parameters
        ----------
        session_id : str
            The session ID.

        Returns
        -------
        bool
            True if deleted, False if didn't exist.
        """
        ...

    @abstractmethod
    async def refresh_session(self, session_id: str, extend_ttl: int | None = None) -> bool:
        """Refresh a session's expiry time.

        Parameters
        ----------
        session_id : str
            The session ID.
        extend_ttl : int or None
            New TTL in seconds (None to use original TTL).

        Returns
        -------
        bool
            True if refreshed, False if session doesn't exist.
        """
        ...

    @abstractmethod
    async def list_user_sessions(self, user_id: str) -> list[UserSession]:
        """List all sessions for a user.

        Parameters
        ----------
        user_id : str
            The user ID.

        Returns
        -------
        list[UserSession]
            List of active sessions for this user.
        """
        ...

    @abstractmethod
    async def check_permission(
        self,
        session_id: str,
        resource_type: str,
        resource_id: str,
        permission: str,
    ) -> bool:
        """Check if a session has permission to access a resource.

        Parameters
        ----------
        session_id : str
            The session ID.
        resource_type : str
            The type of resource (e.g., "widget", "user").
        resource_id : str
            The resource identifier.
        permission : str
            The required permission (e.g., "read", "write", "admin").

        Returns
        -------
        bool
            True if the session has the required permission.
        """
        ...
