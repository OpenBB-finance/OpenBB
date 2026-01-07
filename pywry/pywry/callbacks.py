"""Callback registry for PyWry event handling."""

from __future__ import annotations

import asyncio
import inspect
import re

from collections.abc import Awaitable, Callable
from typing import Any

from .log import debug, warn
from .models import validate_event_type


# Type alias for callback functions (sync or async)
CallbackFunc = Callable[..., None] | Callable[..., Awaitable[None]]


class CallbackRegistry:
    """Registry for managing event callbacks.

    Supports both sync and async callbacks with namespace:event-name pattern.
    Thread-safe singleton pattern.
    """

    _instance: CallbackRegistry | None = None
    _initialized: bool = False

    def __new__(cls) -> CallbackRegistry:
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if self._initialized:
            return
        self._initialized = True
        # Structure: {window_label: {event_type: [callbacks]}}
        self._callbacks: dict[str, dict[str, list[CallbackFunc]]] = {}
        self._destroyed_labels: set[str] = set()

    def register(
        self,
        label: str,
        event_type: str,
        handler: CallbackFunc,
    ) -> bool:
        """Register an event handler.

        Parameters
        ----------
        label : str
            The window label.
        event_type : str
            The event type (namespace:event-name or * for wildcard).
        handler : CallbackFunc
            The callback function.

        Returns
        -------
        bool
            True if registered successfully, False otherwise.
        """
        # Validate event type
        if not validate_event_type(event_type):
            warn(
                f"Invalid event type '{event_type}'. "
                "Must match 'namespace:event-name' pattern or '*'."
            )
            return False

        # Check if label was destroyed
        if label in self._destroyed_labels:
            warn(f"Cannot register handler for destroyed window '{label}'")
            return False

        # Initialize structures
        if label not in self._callbacks:
            self._callbacks[label] = {}
        if event_type not in self._callbacks[label]:
            self._callbacks[label][event_type] = []

        self._callbacks[label][event_type].append(handler)
        debug(f"Registered handler for '{event_type}' on window '{label}'")
        return True

    def unregister(
        self,
        label: str,
        event_type: str | None = None,
        handler: CallbackFunc | None = None,
    ) -> bool:
        """Unregister event handler(s).

        Parameters
        ----------
        label : str
            The window label.
        event_type : str or None, optional
            The event type (None to unregister all for this label).
        handler : CallbackFunc or None, optional
            Specific handler to remove (None to remove all for event_type).

        Returns
        -------
        bool
            True if any handlers were removed, False otherwise.
        """
        if label not in self._callbacks:
            return False

        if event_type is None:
            # Remove all handlers for this label
            del self._callbacks[label]
            debug(f"Unregistered all handlers for window '{label}'")
            return True

        if event_type not in self._callbacks[label]:
            return False

        if handler is None:
            # Remove all handlers for this event type
            del self._callbacks[label][event_type]
            debug(f"Unregistered all handlers for '{event_type}' on window '{label}'")
            return True

        # Remove specific handler
        try:
            self._callbacks[label][event_type].remove(handler)
            debug(f"Unregistered specific handler for '{event_type}' on window '{label}'")
            return True
        except ValueError:
            return False

    def dispatch(
        self,
        label: str,
        event_type: str,
        data: Any,
    ) -> bool:
        """Dispatch an event to registered handlers.

        Parameters
        ----------
        label : str
            The window label.
        event_type : str
            The event type.
        data : Any
            The event data.

        Returns
        -------
        bool
            True if any handlers were called, False otherwise.
        """
        if label in self._destroyed_labels:
            debug(f"Ignoring event for destroyed window '{label}'")
            return False

        if label not in self._callbacks:
            return False

        handlers_called = False

        # Get handlers for this specific event
        handlers = self._callbacks[label].get(event_type, [])

        # Also get wildcard handlers
        wildcard_handlers = self._callbacks[label].get("*", [])

        # Also check for namespace wildcard (e.g., "plotly:*")
        namespace_match = re.match(r"^([a-z][a-z0-9]*):", event_type)
        namespace_wildcard_handlers: list[CallbackFunc] = []
        if namespace_match:
            namespace = namespace_match.group(1)
            namespace_wildcard = f"{namespace}:*"
            namespace_wildcard_handlers = self._callbacks[label].get(namespace_wildcard, [])

        all_handlers = handlers + wildcard_handlers + namespace_wildcard_handlers

        for handler in all_handlers:
            try:
                # Try to call with all args first, fall back to just data
                sig = inspect.signature(handler)
                num_params = len(
                    [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
                )
                if num_params >= 3:
                    result = handler(data, event_type, label)
                elif num_params == 2:
                    result = handler(data, event_type)
                else:
                    result = handler(data)
                # Handle async callbacks
                if asyncio.iscoroutine(result):
                    # Schedule the coroutine
                    try:
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(result)
                        # Store reference to prevent garbage collection
                        task.add_done_callback(lambda t: None)
                    except RuntimeError:
                        # No running loop, try to run synchronously
                        asyncio.run(result)
                handlers_called = True
            except (
                RuntimeError,
                TypeError,
                ValueError,
                AttributeError,
                KeyError,
            ) as e:
                warn(f"Error in callback for '{event_type}' on window '{label}': {e}")

        return handlers_called

    def destroy(self, label: str) -> bool:
        """Completely destroy all resources for a window label.

        This removes all callbacks and marks the label as destroyed
        to prevent future registrations.

        Args:
            label: The window label to destroy.

        Returns
        -------
            True if the label was destroyed, False if it didn't exist.
        """
        existed = label in self._callbacks

        # Remove all callbacks
        if existed:
            del self._callbacks[label]

        # Mark as destroyed
        self._destroyed_labels.add(label)

        if existed:
            debug(f"Destroyed callback registry for window '{label}'")

        return existed

    def is_destroyed(self, label: str) -> bool:
        """Check if a window label has been destroyed.

        Args:
            label: The window label.

        Returns
        -------
            True if destroyed, False otherwise.
        """
        return label in self._destroyed_labels

    def has_handlers(self, label: str) -> bool:
        """Check if a window has any registered handlers.

        Args:
            label: The window label.

        Returns
        -------
            True if handlers exist, False otherwise.
        """
        return label in self._callbacks and bool(self._callbacks[label])

    def get_labels(self) -> list[str]:
        """Get all window labels with registered handlers.

        Returns
        -------
            List of window labels.
        """
        return list(self._callbacks.keys())

    def clear(self) -> None:
        """Clear all callbacks and destroyed labels.

        Use with caution - primarily for testing.
        """
        self._callbacks.clear()
        self._destroyed_labels.clear()
        debug("Cleared all callbacks")


def get_registry() -> CallbackRegistry:
    """Get the global callback registry instance.

    Returns
    -------
        The callback registry singleton.
    """
    return CallbackRegistry()
