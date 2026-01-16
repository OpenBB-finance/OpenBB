"""Base window mode interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from ...models import WindowConfig


class WindowModeBase(ABC):
    """Abstract base class for window modes."""

    @abstractmethod
    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, Any] | None = None,
        label: str | None = None,
    ) -> str:
        """Show content in a window.

        Parameters
        ----------
        config : WindowConfig
            Window configuration.
        html : str
            HTML content to display.
        callbacks : dict[str, Any] or None, optional
            Optional callback handlers.
        label : str or None, optional
            Optional window label (for multi-window mode).

        Returns
        -------
        str
            The window label.
        """

    @abstractmethod
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

    @abstractmethod
    def is_open(self, label: str) -> bool:
        """Check if a window is open.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if window is open, False otherwise.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def get_labels(self) -> list[str]:
        """Get all window labels managed by this mode.

        Returns
        -------
        list of str
            List of window labels.
        """

    @abstractmethod
    def close_all(self) -> int:
        """Close all windows.

        Returns
        -------
        int
            Number of windows closed.
        """

    def show_window(self, label: str) -> bool:
        """Show a hidden window.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if shown successfully, False otherwise.
        """
        from ... import runtime

        return runtime.show_window(label)

    def hide_window(self, label: str) -> bool:
        """Hide a window (keeps it alive, just not visible).

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if hidden successfully, False otherwise.
        """
        from ... import runtime

        return runtime.hide_window(label)
