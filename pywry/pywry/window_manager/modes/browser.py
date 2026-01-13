"""BROWSER mode - opens content in system default browser."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import WindowModeBase


if TYPE_CHECKING:
    from ...models import WindowConfig


class BrowserMode(WindowModeBase):
    """Opens content in the system's default browser.

    Uses the inline FastAPI server and opens the widget URL in a browser tab.
    Each show() call creates a new widget instance with its own state.

    This mode is ideal for headless environments (servers, SSH sessions)
    or when native window support is not available.
    """

    def __init__(self) -> None:
        """Initialize the browser mode."""
        self._widgets: dict[str, Any] = {}

    def show(
        self,
        config: WindowConfig,
        html: str,
        callbacks: dict[str, Any] | None = None,
        label: str | None = None,
    ) -> str:
        """Show content in the system browser.

        Parameters
        ----------
        config : WindowConfig
            Window configuration (width/height used for suggestion only).
        html : str
            HTML content to display.
        callbacks : dict[str, Any] or None, optional
            Optional callback handlers.
        label : str or None, optional
            Optional widget label (used as prefix for widget_id).

        Returns
        -------
        str
            The widget ID (used as window_label for GenericEvent).
        """
        from ... import inline as pywry_inline

        # Determine theme
        theme = "dark"
        if hasattr(config, "theme"):
            theme_val = config.theme
            if hasattr(theme_val, "value"):
                theme = "light" if "light" in theme_val.value.lower() else "dark"
            elif isinstance(theme_val, str):
                theme = "light" if "light" in theme_val.lower() else "dark"

        # Create widget via inline module
        widget = pywry_inline.show(
            content=html,
            title=config.title,
            width="100%",
            height=config.height,
            theme=theme,  # type: ignore[arg-type]
            callbacks=callbacks,
        )

        # Store reference
        self._widgets[widget.widget_id] = widget

        # Open in system browser
        widget.open_in_browser()

        return widget.widget_id

    def close(self, label: str) -> bool:
        """Close a widget by removing it from tracking.

        Note: This does not close the browser tab - that's user-controlled.
        It does trigger the disconnect callback and cleanup.

        Parameters
        ----------
        label : str
            The widget ID.

        Returns
        -------
        bool
            True if widget was found and cleaned up.
        """
        from ... import inline as pywry_inline

        if label in self._widgets:
            del self._widgets[label]
            # Trigger disconnect handling
            pywry_inline._handle_widget_disconnect(label, "close_called")
            return True
        return False

    def close_all(self) -> int:
        """Close all tracked widgets.

        Returns
        -------
        int
            Number of widgets closed.
        """
        widget_ids = list(self._widgets.keys())
        count = 0
        for widget_id in widget_ids:
            if self.close(widget_id):
                count += 1
        return count

    def is_open(self, label: str) -> bool:
        """Check if a widget is being tracked.

        Note: This only checks if we're tracking the widget, not if the
        browser tab is actually open (we can't know that).

        Parameters
        ----------
        label : str
            The widget ID.

        Returns
        -------
        bool
            True if widget is being tracked.
        """
        return label in self._widgets

    def update_content(self, label: str, html: str, theme: str = "dark") -> bool:
        """Update widget content.

        Parameters
        ----------
        label : str
            The widget ID.
        html : str
            New HTML content.
        theme : str
            Theme mode ('dark' or 'light').

        Returns
        -------
        bool
            True if updated successfully.
        """
        widget = self._widgets.get(label)
        if widget is None:
            return False

        # Use the widget's update method
        widget.update_html(html)
        return True

    def send_event(self, label: str, event_type: str, data: Any) -> bool:
        """Send an event to a widget's browser.

        Parameters
        ----------
        label : str
            The widget ID.
        event_type : str
            The event type.
        data : Any
            The event data.

        Returns
        -------
        bool
            True if sent successfully.
        """
        widget = self._widgets.get(label)
        if widget is None:
            return False

        widget.emit(event_type, data)
        return True

    def get_labels(self) -> list[str]:
        """Get all tracked widget IDs.

        Returns
        -------
        list of str
            List of widget IDs.
        """
        return list(self._widgets.keys())

    def get_widget(self, widget_id: str) -> Any | None:
        """Get an InlineWidget by ID for further interaction.

        Parameters
        ----------
        widget_id : str
            The widget ID returned from show().

        Returns
        -------
        InlineWidget or None
            The widget instance, or None if not found.
        """
        return self._widgets.get(widget_id)
