"""SINGLE_WINDOW mode - reuses one window, replaces content."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...callbacks import get_registry
from ...log import debug, warn
from ..lifecycle import get_lifecycle
from .base import WindowModeBase


if TYPE_CHECKING:
    from ...models import WindowConfig


class SingleWindowMode(WindowModeBase):
    """Reuses a single window for all show() calls.

    Content is replaced in-place without creating new windows.
    """

    def __init__(self, label: str = "main") -> None:
        """Initialize the mode.

        Parameters
        ----------
        label : str, optional
            The fixed label for the single window, by default "main".
        """
        self._label = label
        self._is_created = False

        # Ensure label is available for registration
        # This handles cases where the label was previously destroyed in a persistent session
        get_registry().recover_label(label)

    @property
    def label(self) -> str:
        """Get the window label."""
        return self._label

    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, Any] | None = None,
        label: str | None = None,
    ) -> str:
        """Show content in the single window.

        If window doesn't exist, creates it. Otherwise replaces content.
        Window is never destroyed - just hidden when user clicks X.

        Parameters
        ----------
        config : WindowConfig
            Window configuration.
        html : str
            HTML content to display.
        callbacks : dict[str, Any] or None, optional
            Optional callback handlers.
        label : str or None, optional
            Ignored for single window mode.

        Returns
        -------
        str
            The window label.
        """
        lifecycle = get_lifecycle()
        registry = get_registry()
        from ... import runtime

        # SINGLE_WINDOW mode: Window is never destroyed, just hidden when user clicks X
        # So we just need to ensure runtime is started, show the window, and set content

        # Ensure label is available (might have been destroyed by close())
        registry.recover_label(self._label)

        if not self._is_created:
            # First time - create the window
            debug(f"First show - creating window '{self._label}'")
            lifecycle.create(
                self._label,
                title=config.title,
                width=config.width,
                height=config.height,
            )
            self._is_created = True
        else:
            # Window exists (possibly hidden) - just show it
            debug(f"Window '{self._label}' already created, showing it")
            runtime.show_window(self._label)

        # Register callbacks
        if callbacks:
            for event_type, handler in callbacks.items():
                registry.register(self._label, event_type, handler)

        # Ensure lifecycle has resources registered
        if not lifecycle.exists(self._label):
            debug(f"Creating lifecycle resources for '{self._label}'")
            from ...window_manager.lifecycle import WindowResources

            resources = WindowResources(label=self._label)
            lifecycle._windows[self._label] = resources

        # Send content via IPC
        theme_str = "dark" if config.theme.value in ("dark", "system") else "light"
        debug(f"Calling lifecycle.set_content for '{self._label}'")
        success = lifecycle.set_content(self._label, html, theme_str)
        debug(f"lifecycle.set_content returned: {success}")

        if not success:
            warn(f"set_content failed for '{self._label}'")

        return self._label

    def close(self, label: str) -> bool:
        """Close the window.

        Parameters
        ----------
        label : str
            The window label (must match our label).

        Returns
        -------
        bool
            True if closed successfully, False otherwise.
        """
        if label != self._label:
            warn(f"SingleWindowMode only manages '{self._label}', not '{label}'")
            return False

        if not self._is_created:
            warn(f"Window '{self._label}' not created")
            return False

        debug(f"Closing single window '{self._label}'")

        # Destroy lifecycle resources
        get_lifecycle().destroy(self._label)
        self._is_created = False

        return True

    def is_open(self, label: str) -> bool:
        """Check if the window is open.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if window is open, False otherwise.
        """
        return label == self._label and self._is_created

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
        if label != self._label or not self._is_created:
            warn(f"Window '{label}' not available")
            return False

        debug(f"Updating content for single window '{self._label}'")
        get_lifecycle().set_content(self._label, html, theme)

        return True

    def send_event(self, label: str, event_type: str, data: Any) -> bool:
        """Send an event to the window.

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
        if label != self._label or not self._is_created:
            warn(f"Window '{label}' not available")
            return False

        debug(f"Sending event '{event_type}' to single window")

        # Actually emit the event to the window
        from ...runtime import emit_event

        return emit_event(self._label, event_type, data)

    def get_labels(self) -> list[str]:
        """Get window labels.

        Returns
        -------
        list of str
            List containing the single window label if created.
        """
        return [self._label] if self._is_created else []

    def close_all(self) -> int:
        """Close all windows (just the one).

        Returns
        -------
        int
            Number of windows closed (0 or 1).
        """
        if self._is_created:
            self.close(self._label)
            return 1
        return 0
