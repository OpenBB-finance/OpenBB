"""NEW_WINDOW mode - creates a new window for each request."""

from __future__ import annotations

import uuid

from typing import TYPE_CHECKING, Any

from ...callbacks import get_registry
from ...log import debug, warn
from ..lifecycle import get_lifecycle
from .base import WindowModeBase


if TYPE_CHECKING:
    from ...models import WindowConfig


class NewWindowMode(WindowModeBase):
    """Creates a new window for each show() call.

    Each window is independent and has its own lifecycle.
    """

    def __init__(self) -> None:
        """Initialize the mode."""
        self._windows: dict[str, bool] = {}  # label -> is_visible

    def _generate_label(self, prefix: str = "pywry") -> str:
        """Generate a unique window label.

        Parameters
        ----------
        prefix : str, optional
            Label prefix, by default "pywry".

        Returns
        -------
        str
            Unique label string.
        """
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, Any] | None = None,
        label: str | None = None,
    ) -> str:
        """Show content in a new window.

        Parameters
        ----------
        config : WindowConfig
            Window configuration.
        html : str
            HTML content to display.
        callbacks : dict[str, Any] or None, optional
            Optional callback handlers.
        label : str or None, optional
            Ignored in new window mode.

        Returns
        -------
        str
            The window label.
        """
        # Generate unique label if not provided
        if label is None:
            label = self._generate_label(config.title.lower().replace(" ", "-"))

        debug(f"Creating new window '{label}'")

        # Register callbacks FIRST, before window is created
        # This ensures pywry:ready callback is registered before the window sends its ready event
        if callbacks:
            registry = get_registry()
            for event_type, handler in callbacks.items():
                registry.register(label, event_type, handler)

        # Register visibility handler for block() support
        registry = get_registry()

        def on_hidden(_data: dict[str, Any], _event_type: str, hidden_label: str) -> None:
            if hidden_label in self._windows:
                self._windows[hidden_label] = False

        registry.register(label, "window:hidden", on_hidden)

        # Register close handler for when window is destroyed
        # This is essential for block() to detect when the window is closed
        def on_closed(_data: dict[str, Any], _event_type: str, closed_label: str) -> None:
            if closed_label in self._windows:
                del self._windows[closed_label]

        registry.register(label, "window:closed", on_closed)

        # Create lifecycle tracking and actual window
        lifecycle = get_lifecycle()
        lifecycle.create(
            label,
            title=config.title,
            width=config.width,
            height=config.height,
        )
        # MUST pass theme so window background matches content
        # Also pass config so content-request handler has access to theme
        theme_str = "dark" if config.theme.value in ("dark", "system") else "light"
        lifecycle.set_content(label, html, theme_str, config=config)

        # Track the window as visible
        self._windows[label] = True

        # Actual pytauri window creation will be added in controller

        return label

    def close(self, label: str) -> bool:
        """Close a window.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if closed successfully, False otherwise.
        """
        if label not in self._windows:
            warn(f"Window '{label}' not found")
            return False

        debug(f"Closing window '{label}'")

        # Destroy lifecycle resources
        get_lifecycle().destroy(label)

        # Remove from tracking
        del self._windows[label]

        return True

    def is_open(self, label: str) -> bool:
        """Check if a window is open.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if window is open and visible, False otherwise.
        """
        return self._windows.get(label, False) and get_lifecycle().exists(label)

    def update_content(self, label: str, html: str, theme: str = "dark") -> bool:
        """Update window content.

        Parameters
        ----------
        label : str
            The window label.
        html : str
            New HTML content.
        theme : str
            Theme mode ('dark' or 'light') - MUST match window background.

        Returns
        -------
        bool
            True if updated successfully, False otherwise.
        """
        if label not in self._windows:
            warn(f"Window '{label}' not found")
            return False

        debug(f"Updating content for window '{label}'")

        # Update lifecycle tracking
        get_lifecycle().set_content(label, html, theme)

        return True

    def send_event(self, label: str, event_type: str, data: Any) -> bool:
        """Send an event to a window.

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
            True if sent successfully, False otherwise.
        """
        if label not in self._windows:
            warn(f"Window '{label}' not found")
            return False

        debug(f"Sending event '{event_type}' to window '{label}'")

        # Actually emit the event to the window
        from ...runtime import emit_event

        return emit_event(label, event_type, data)

    def get_labels(self) -> list[str]:
        """Get all visible window labels managed by this mode.

        Returns
        -------
        list of str
            List of visible window labels.
        """
        return [label for label, visible in self._windows.items() if visible]

    def close_all(self) -> int:
        """Close all windows.

        Returns
        -------
        int
            Number of windows closed.
        """
        labels = list(self._windows.keys())
        count = 0
        for label in labels:
            if self.close(label):
                count += 1
        return count
