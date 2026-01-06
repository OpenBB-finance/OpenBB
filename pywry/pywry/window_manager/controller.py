"""Window controller for managing window modes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..log import debug
from ..models import WindowConfig, WindowMode
from .lifecycle import get_lifecycle
from .modes import (
    MultiWindowMode,
    NewWindowMode,
    SingleWindowMode,
    WindowModeBase,
)


if TYPE_CHECKING:
    from ..callbacks import CallbackFunc


class WindowController:
    """Controller for window management across different modes.

    This class provides a unified interface for creating and managing windows
    regardless of the underlying window mode.
    """

    def __init__(self, mode: WindowMode = WindowMode.NEW_WINDOW) -> None:
        """Initialize the controller.

        Parameters
        ----------
        mode : WindowMode, optional
            The window mode to use.
        """
        self._mode_enum = mode
        self._mode = self._create_mode(mode)
        debug(f"WindowController initialized with {mode.value} mode")

    def _create_mode(self, mode: WindowMode) -> WindowModeBase:
        """Create the appropriate mode handler.

        Parameters
        ----------
        mode : WindowMode
            The window mode enum.

        Returns
        -------
        WindowModeBase
            The mode handler instance.
        """
        if mode == WindowMode.NEW_WINDOW:
            return NewWindowMode()
        if mode == WindowMode.SINGLE_WINDOW:
            return SingleWindowMode()
        return MultiWindowMode()

    @property
    def mode(self) -> WindowMode:
        """Get the current window mode."""
        return self._mode_enum

    def set_mode(self, mode: WindowMode) -> None:
        """Change the window mode.

        Warning: This closes all existing windows.

        Parameters
        ----------
        mode : WindowMode
            The new window mode.
        """
        if mode == self._mode_enum:
            return

        # Close all windows first
        self._mode.close_all()

        # Create new mode handler
        self._mode_enum = mode
        self._mode = self._create_mode(mode)
        debug(f"WindowController switched to {mode.value} mode")

    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, CallbackFunc] | None = None,
    ) -> str:
        """Show content in a window.

        Parameters
        ----------
        config : WindowConfig
            Window configuration.
        html : str
            HTML content to display.
        callbacks : dict[str, CallbackFunc] or None, optional
            Optional event callbacks.

        Returns
        -------
        str
            The window label.
        """
        return self._mode.show(config, html, callbacks)

    def close(self, label: str) -> bool:
        """Close a specific window.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if closed successfully.
        """
        return self._mode.close(label)

    def close_all(self) -> int:
        """Close all windows.

        Returns
        -------
        int
            Number of windows closed.
        """
        return self._mode.close_all()

    def is_open(self, label: str) -> bool:
        """Check if a window is open.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if window is open.
        """
        return self._mode.is_open(label)

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
            True if updated successfully.
        """
        return self._mode.update_content(label, html, theme)

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
            True if sent successfully.
        """
        return self._mode.send_event(label, event_type, data)

    def get_labels(self) -> list[str]:
        """Get all window labels.

        Returns
        -------
        list of str
            List of window labels.
        """
        return self._mode.get_labels()

    def get_stats(self) -> dict[str, Any]:
        """Get window statistics.

        Returns
        -------
        dict[str, Any]
            Statistics dict.
        """
        return {
            "mode": self._mode_enum.value,
            "window_count": len(self.get_labels()),
            "labels": self.get_labels(),
            "lifecycle": get_lifecycle().get_stats(),
        }
