"""Local callback registry for event-driven callback dispatch.

Callbacks are Python functions that cannot be serialized to Redis.
This module provides a local registry that works with the event bus
for cross-worker callback routing.

The pattern:
1. Callbacks are registered locally (per-worker) when widgets are created
2. Events from JavaScript are received via WebSocket
3. If callback exists locally → execute immediately
4. If callback doesn't exist → route event to owner worker via EventBus
5. Owner worker receives event and executes the callback
"""

from __future__ import annotations

import asyncio
import logging
import time

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


logger = logging.getLogger(__name__)

# Type alias for callback functions
# Signature: (data: dict, widget_id: str, event_type: str) -> Any
CallbackFunc = Callable[[dict[str, Any], str, str], Any]
AsyncCallbackFunc = Callable[[dict[str, Any], str, str], Any]


@dataclass
class CallbackRegistration:
    """Tracks a callback registration."""

    widget_id: str
    event_type: str
    callback: CallbackFunc | AsyncCallbackFunc
    is_async: bool = False
    created_at: float = field(default_factory=time.time)
    invoke_count: int = 0
    last_invoked: float | None = None


class CallbackRegistry:
    """In-process callback registry.

    Callbacks cannot be serialized to Redis, so they remain local to each worker.
    The registry tracks which callbacks are registered per widget and event type.
    """

    def __init__(self) -> None:
        """Initialize the callback registry."""
        # widget_id -> event_type -> registration
        self._callbacks: dict[str, dict[str, CallbackRegistration]] = {}
        self._lock = asyncio.Lock()

    async def register(
        self,
        widget_id: str,
        event_type: str,
        callback: CallbackFunc | AsyncCallbackFunc,
    ) -> None:
        """Register a callback for a widget event.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type (e.g., "click", "cellValueChanged").
        callback : CallbackFunc
            The callback function to execute.
        """
        async with self._lock:
            if widget_id not in self._callbacks:
                self._callbacks[widget_id] = {}

            is_async = asyncio.iscoroutinefunction(callback)
            self._callbacks[widget_id][event_type] = CallbackRegistration(
                widget_id=widget_id,
                event_type=event_type,
                callback=callback,
                is_async=is_async,
            )
            logger.debug(  # pylint: disable=logging-too-many-args
                "Registered callback for %s:%s", widget_id, event_type
            )

    async def get(self, widget_id: str, event_type: str) -> CallbackRegistration | None:
        """Get a callback registration.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.

        Returns
        -------
        CallbackRegistration or None
            The registration if found.
        """
        async with self._lock:
            widget_callbacks = self._callbacks.get(widget_id)
            if widget_callbacks is None:
                return None
            return widget_callbacks.get(event_type)

    async def has_widget(self, widget_id: str) -> bool:
        """Check if any callbacks are registered for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        bool
            True if callbacks exist for this widget.
        """
        async with self._lock:
            return widget_id in self._callbacks

    async def has_callback(self, widget_id: str, event_type: str) -> bool:
        """Check if a specific callback is registered.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.

        Returns
        -------
        bool
            True if the callback exists.
        """
        async with self._lock:
            return widget_id in self._callbacks and event_type in self._callbacks[widget_id]

    async def invoke(
        self, widget_id: str, event_type: str, data: dict[str, Any]
    ) -> tuple[bool, Any]:
        """Invoke a callback if it exists locally.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.
        data : dict
            The event data to pass to the callback.

        Returns
        -------
        tuple[bool, Any]
            (success, result) - success is True if callback was found and executed.
        """
        registration = await self.get(widget_id, event_type)
        if registration is None:
            return (False, None)

        try:
            # Update invocation stats
            async with self._lock:
                registration.invoke_count += 1
                registration.last_invoked = time.time()

            # Execute callback
            if registration.is_async:
                result = await registration.callback(data, widget_id, event_type)
            else:
                # Run sync callback in thread pool
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, registration.callback, data, widget_id, event_type
                )

        except Exception:
            logger.exception(  # pylint: disable=logging-too-many-args
                "Error invoking callback %s:%s", widget_id, event_type
            )
            return (False, None)

        logger.debug(  # pylint: disable=logging-too-many-args
            "Invoked callback %s:%s (count: %d)",
            widget_id,
            event_type,
            registration.invoke_count,
        )
        return (True, result)

    async def unregister(self, widget_id: str, event_type: str) -> bool:
        """Unregister a specific callback.

        Parameters
        ----------
        widget_id : str
            The widget ID.
        event_type : str
            The event type.

        Returns
        -------
        bool
            True if the callback was removed.
        """
        async with self._lock:
            if widget_id not in self._callbacks:
                return False
            if event_type not in self._callbacks[widget_id]:
                return False
            del self._callbacks[widget_id][event_type]
            if not self._callbacks[widget_id]:
                del self._callbacks[widget_id]
            return True

    async def unregister_widget(self, widget_id: str) -> int:
        """Unregister all callbacks for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        int
            Number of callbacks removed.
        """
        async with self._lock:
            if widget_id not in self._callbacks:
                return 0
            count = len(self._callbacks[widget_id])
            del self._callbacks[widget_id]
            logger.debug(  # pylint: disable=logging-too-many-args
                "Unregistered %d callbacks for %s", count, widget_id
            )
            return count

    async def list_widget_events(self, widget_id: str) -> list[str]:
        """List all event types registered for a widget.

        Parameters
        ----------
        widget_id : str
            The widget ID.

        Returns
        -------
        list[str]
            List of event types.
        """
        async with self._lock:
            if widget_id not in self._callbacks:
                return []
            return list(self._callbacks[widget_id].keys())

    async def list_widgets(self) -> list[str]:
        """List all widget IDs with registered callbacks.

        Returns
        -------
        list[str]
            List of widget IDs.
        """
        async with self._lock:
            return list(self._callbacks.keys())

    async def get_stats(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns
        -------
        dict
            Statistics about registered callbacks.
        """
        async with self._lock:
            total_callbacks = sum(len(events) for events in self._callbacks.values())
            return {
                "widget_count": len(self._callbacks),
                "total_callbacks": total_callbacks,
                "widgets": {wid: list(events.keys()) for wid, events in self._callbacks.items()},
            }


# Singleton registry holder
class _RegistryHolder:
    """Holds the singleton callback registry instance."""

    instance: CallbackRegistry | None = None


def get_callback_registry() -> CallbackRegistry:
    """Get the global callback registry instance.

    Returns
    -------
    CallbackRegistry
        The singleton callback registry.
    """
    if _RegistryHolder.instance is None:
        _RegistryHolder.instance = CallbackRegistry()
    return _RegistryHolder.instance


def reset_callback_registry() -> None:
    """Reset the global callback registry (for testing)."""
    _RegistryHolder.instance = CallbackRegistry()
