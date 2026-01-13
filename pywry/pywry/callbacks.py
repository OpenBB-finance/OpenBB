"""Callback registry for PyWry event handling."""

from __future__ import annotations

import asyncio
import fnmatch
import inspect
import re

from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

from .log import debug, warn
from .models import validate_event_type


# Type alias for callback functions (sync or async)
CallbackFunc = Callable[..., None] | Callable[..., Awaitable[None]]


class WidgetType(str, Enum):
    """Widget types for event routing."""

    GRID = "grid"
    CHART = "chart"
    TOOLBAR = "toolbar"
    HTML = "html"
    WINDOW = "window"


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
        # Structure: {window_label: {event_type: [(pattern, handler)]}}
        # Pattern is a tuple: (widget_type_pattern, widget_id_pattern)
        self._callbacks: dict[str, dict[str, list[CallbackFunc]]] = {}
        # Extended structure for widget-scoped callbacks
        # {window_label: {event_type: [(widget_type, widget_id, handler)]}}
        self._scoped_callbacks: dict[str, dict[str, list[tuple[str, str, CallbackFunc]]]] = {}
        self._destroyed_labels: set[str] = set()

    @staticmethod
    def _matches(pattern: str, source: str) -> bool:
        """Check if a pattern matches a source string.

        Supports wildcards (*) for flexible matching.

        Parameters
        ----------
        pattern : str
            Pattern to match (can contain * wildcards).
        source : str
            Source string to match against.

        Returns
        -------
        bool
            True if pattern matches source.

        Examples
        --------
        >>> CallbackRegistry._matches("*", "anything")
        True
        >>> CallbackRegistry._matches("grid_*", "grid_123")
        True
        >>> CallbackRegistry._matches("chart", "chart")
        True
        """
        if pattern == "*":
            return True
        return fnmatch.fnmatch(source, pattern)

    def register(
        self,
        label: str,
        event_type: str,
        handler: CallbackFunc,
        widget_type: str = "*",
        widget_id: str = "*",
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
        widget_type : str, optional
            Widget type filter ("grid", "chart", "toolbar", "html", "window", or "*").
        widget_id : str, optional
            Widget ID filter (specific ID or "*" for all).

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

        # Initialize structures for simple callbacks (backward compat)
        if label not in self._callbacks:
            self._callbacks[label] = {}
        if event_type not in self._callbacks[label]:
            self._callbacks[label][event_type] = []

        # If widget scoping is used, store in scoped structure
        if widget_type != "*" or widget_id != "*":
            if label not in self._scoped_callbacks:
                self._scoped_callbacks[label] = {}
            if event_type not in self._scoped_callbacks[label]:
                self._scoped_callbacks[label][event_type] = []
            self._scoped_callbacks[label][event_type].append((widget_type, widget_id, handler))
            debug(
                f"Registered scoped handler for '{event_type}' "
                f"[{widget_type}:{widget_id}] on window '{label}'"
            )
        else:
            # Store in simple structure for backward compat
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

    def _collect_simple_handlers(self, label: str, event_type: str) -> list[CallbackFunc]:
        """Collect handlers from simple (non-scoped) callback structure."""
        handlers: list[CallbackFunc] = []
        if label not in self._callbacks:
            return handlers

        # 1. Exact match
        handlers.extend(self._callbacks[label].get(event_type, []))

        # 2. Base match (e.g., "plotly:click" if event is "plotly:click:chart1")
        if event_type.count(":") >= 2:
            parts = event_type.split(":")
            base_event = f"{parts[0]}:{parts[1]}"
            handlers.extend(self._callbacks[label].get(base_event, []))

        # 3. Wildcard ("*")
        handlers.extend(self._callbacks[label].get("*", []))

        # 4. Namespace wildcard (e.g., "plotly:*")
        namespace_match = re.match(r"^([a-z][a-z0-9]*):", event_type)
        if namespace_match:
            namespace_wildcard = f"{namespace_match.group(1)}:*"
            handlers.extend(self._callbacks[label].get(namespace_wildcard, []))

        return handlers

    def _collect_scoped_handlers(
        self, label: str, event_type: str, widget_type: str, widget_id: str
    ) -> list[CallbackFunc]:
        """Collect handlers from scoped callback structure with pattern matching."""
        handlers: list[CallbackFunc] = []
        if label not in self._scoped_callbacks:
            return handlers

        # Check exact event type and wildcard
        for evt_pattern in [event_type, "*"]:
            for wtype_pattern, wid_pattern, handler in self._scoped_callbacks[label].get(
                evt_pattern, []
            ):
                if self._matches(wtype_pattern, widget_type) and self._matches(
                    wid_pattern, widget_id
                ):
                    handlers.append(handler)

        # Check namespace wildcards
        namespace_match = re.match(r"^([a-z][a-z0-9]*):", event_type)
        if namespace_match:
            namespace_wildcard = f"{namespace_match.group(1)}:*"
            for wtype_pattern, wid_pattern, handler in self._scoped_callbacks[label].get(
                namespace_wildcard, []
            ):
                if self._matches(wtype_pattern, widget_type) and self._matches(
                    wid_pattern, widget_id
                ):
                    handlers.append(handler)

        return handlers

    def _invoke_handler(
        self, handler: CallbackFunc, data: Any, event_type: str, label: str
    ) -> bool:
        """Invoke a single handler with appropriate arguments."""
        try:
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
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(result)
                    task.add_done_callback(lambda t: None)
                except RuntimeError:
                    asyncio.run(result)
            return True
        except (RuntimeError, TypeError, ValueError, AttributeError, KeyError) as e:
            warn(f"Error in callback for '{event_type}' on window '{label}': {e}")
            return False

    def dispatch(
        self,
        label: str,
        event_type: str,
        data: Any,
    ) -> bool:
        """Dispatch an event to registered handlers.

        Matches handlers based on event type and optional widget_type/widget_id
        from the event data. Scoped handlers are matched using wildcard patterns.

        Parameters
        ----------
        label : str
            The window label.
        event_type : str
            The event type.
        data : Any
            The event data. May contain widget_type and widget_id/gridId/chartId.

        Returns
        -------
        bool
            True if any handlers were called, False otherwise.
        """
        if label in self._destroyed_labels:
            debug(f"Ignoring event for destroyed window '{label}'")
            return False

        # Extract widget routing info from event data
        widget_type = "*"
        widget_id = "*"
        if isinstance(data, dict):
            widget_type = data.get("widget_type", "*")
            widget_id = (
                data.get("widget_id")
                or data.get("gridId")
                or data.get("chartId")
                or data.get("toolbarId")
                or "*"
            )

        # Collect all matching handlers
        all_handlers = self._collect_simple_handlers(label, event_type)
        all_handlers.extend(
            self._collect_scoped_handlers(label, event_type, widget_type, widget_id)
        )

        # Invoke handlers
        handlers_called = False
        for handler in all_handlers:
            if self._invoke_handler(handler, data, event_type, label):
                handlers_called = True

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
        existed = label in self._callbacks or label in self._scoped_callbacks

        # Remove all callbacks
        if label in self._callbacks:
            del self._callbacks[label]
        if label in self._scoped_callbacks:
            del self._scoped_callbacks[label]

        # Mark as destroyed
        self._destroyed_labels.add(label)

        if existed:
            debug(f"Destroyed callback registry for window '{label}'")

        return existed

    def recover_label(self, label: str) -> bool:
        """Recover a destroyed label to allow new registrations.

        This is useful when restarting the application or reusing a label
        that was previously destroyed.

        Args:
            label: The window label to recover.

        Returns
        -------
            True if the label was recovered (was in destroyed set).
        """
        if label in self._destroyed_labels:
            self._destroyed_labels.remove(label)
            debug(f"Recovered destroyed label '{label}'")
            return True
        return False

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
        has_simple = label in self._callbacks and bool(self._callbacks[label])
        has_scoped = label in self._scoped_callbacks and bool(self._scoped_callbacks[label])
        return has_simple or has_scoped

    def get_labels(self) -> list[str]:
        """Get all window labels with registered handlers.

        Returns
        -------
            List of window labels.
        """
        labels = set(self._callbacks.keys())
        labels.update(self._scoped_callbacks.keys())
        return list(labels)

    def clear(self) -> None:
        """Clear all callbacks and destroyed labels.

        Use with caution - primarily for testing.
        """
        self._callbacks.clear()
        self._scoped_callbacks.clear()
        self._destroyed_labels.clear()
        debug("Cleared all callbacks")


def get_registry() -> CallbackRegistry:
    """Get the global callback registry instance.

    Returns
    -------
        The callback registry singleton.
    """
    return CallbackRegistry()
