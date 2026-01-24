"""Window lifecycle management for aggressive resource cleanup."""

from __future__ import annotations

import gc

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..callbacks import get_registry
from ..log import debug, warn


if TYPE_CHECKING:
    from pathlib import Path

    from ..models import HtmlContent, WindowConfig


@dataclass
class WindowResources:
    """Tracks resources associated with a window."""

    label: str
    created_at: datetime = field(default_factory=datetime.now)
    html_content: str | None = None
    scripts_injected: list[str] = field(default_factory=list)
    libraries_loaded: list[str] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)
    is_destroyed: bool = False

    # For hot reload - store original content and config
    last_content: HtmlContent | None = None
    last_config: WindowConfig | None = None

    # Watched files for hot reload
    watched_css: list[Path] = field(default_factory=list)
    watched_scripts: list[Path] = field(default_factory=list)
    css_asset_ids: dict[Path, str] = field(default_factory=dict)

    # Timestamp when content was last set via IPC (to debounce content-request)
    content_set_at: datetime | None = None


class WindowLifecycle:
    """Manages window lifecycle with aggressive cleanup.

    Uses subprocess IPC to communicate with pytauri process.
    """

    _instance: WindowLifecycle | None = None
    _initialized: bool = False

    def __new__(cls) -> WindowLifecycle:
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        if self._initialized:
            return
        self._initialized = True
        self._windows: dict[str, WindowResources] = {}

    def clear(self) -> None:
        """Clear all tracked windows.

        This resets the lifecycle manager to its initial state.
        Useful for test cleanup when the runtime is stopped.
        """
        self._windows.clear()

    def create(
        self, label: str, title: str = "PyWry", width: int = 800, height: int = 600
    ) -> WindowResources:
        """Create or register a window via subprocess IPC.

        Parameters
        ----------
        label : str
            The window label.
        title : str, optional
            Window title.
        width : int, optional
            Window width.
        height : int, optional
            Window height.

        Returns
        -------
        WindowResources
            The window resources object.
        """
        from .. import runtime

        if label in self._windows:
            warn(f"Window '{label}' already exists, destroying first")
            self.destroy(label)

        # After destroying, recover the label so callbacks can be registered again
        get_registry().recover_label(label)

        # Ensure runtime subprocess is started
        if not runtime.is_running():
            debug("Starting pytauri subprocess...")
            if not runtime.start():
                warn("Failed to start pytauri subprocess")
                resources = WindowResources(label=label)
                self._windows[label] = resources
                return resources

            # Fresh subprocess start - main window is auto-created by Tauri.toml
            # Just show it, don't check (IPC might not be ready for checks yet)
            if label == "main":
                debug("Fresh start - showing auto-created 'main' window")
                runtime.show_window(label)
                resources = WindowResources(label=label)
                self._windows[label] = resources
                return resources

        # Runtime already running - check window state
        if label == "main":
            # Check if main window still exists
            if runtime.check_window_open(label):
                runtime.show_window(label)
                debug("Showing pre-existing 'main' window")
            else:
                # Main was closed - recreate it
                debug("Main window was closed, recreating...")
                runtime.create_window(label, title, width, height)
                debug("Recreated 'main' window via IPC")
        else:
            runtime.create_window(label, title, width, height)
            debug(f"Created window '{label}' via IPC")

        resources = WindowResources(label=label)
        self._windows[label] = resources
        return resources

    def get(self, label: str) -> WindowResources | None:
        """Get resources for a window."""
        return self._windows.get(label)

    def exists(self, label: str) -> bool:
        """Check if a window exists."""
        resources = self._windows.get(label)
        return resources is not None and not resources.is_destroyed

    def register_window(self, label: str) -> WindowResources:
        """Register a window in lifecycle tracking without creating via IPC.

        Use this when the window already exists (e.g., from previous PyWry instance)
        and just needs to be tracked.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        WindowResources
            The window resources object.
        """
        if label in self._windows:
            # Already tracked - just ensure not marked destroyed
            self._windows[label].is_destroyed = False
            return self._windows[label]

        resources = WindowResources(label=label)
        self._windows[label] = resources
        return resources

    def get_active_windows(self) -> list[str]:
        """Get labels of all tracked active windows."""
        return [label for label, res in self._windows.items() if not res.is_destroyed]

    def set_content(
        self,
        label: str,
        html: str,
        theme: str = "dark",
        config: WindowConfig | None = None,
    ) -> bool:
        """Set the HTML content for a window via IPC.

        Parameters
        ----------
        label : str
            The window label.
        html : str
            The HTML content.
        theme : str
            Theme mode ('dark' or 'light') - MUST match window background.
        config : WindowConfig or None, optional
            Store config for content-request handler to use.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        from .. import runtime

        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False

        resources.html_content = html
        if config is not None:
            resources.last_config = config

        # Record timestamp BEFORE calling runtime.set_content to debounce
        # content-request events that arrive during the blocking IPC call
        resources.content_set_at = datetime.now()

        success = runtime.set_content(label, html, theme)

        if success:
            debug(f"Sent content to window '{label}' via IPC with theme '{theme}'")
        else:
            # Only warn if we think it should be open
            debug(f"Failed to set content for window '{label}' - it may be closed")

        return success

    def is_open(self, label: str) -> bool:
        """Check if window is truly open via IPC.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if window is verified open in backend.
        """
        from .. import runtime

        if not self.exists(label):
            return False

        return runtime.check_window_open(label)

    def store_content_for_refresh(
        self,
        label: str,
        content: HtmlContent,
        config: WindowConfig,
    ) -> bool:
        """Store content and config for window refresh.

        Parameters
        ----------
        label : str
            The window label.
        content : HtmlContent
            The HtmlContent object.
        config : WindowConfig
            The WindowConfig object.

        Returns
        -------
        bool
            True if stored successfully.
        """
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False
        resources.last_content = content
        resources.last_config = config
        return True

    def get_content_for_refresh(
        self,
        label: str,
    ) -> tuple[HtmlContent | None, WindowConfig | None]:
        """Get stored content and config for window refresh.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        tuple[HtmlContent or None, WindowConfig or None]
            Tuple of (content, config) or (None, None) if not found.
        """
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return None, None
        return resources.last_content, resources.last_config

    def add_watched_file(
        self,
        label: str,
        path: Path,
        file_type: str,
        asset_id: str | None = None,
    ) -> bool:
        """Track a file for hot reload.

        Parameters
        ----------
        label : str
            The window label.
        path : Path
            Path to the watched file.
        file_type : str
            Either "css" or "script".
        asset_id : str or None, optional
            Asset ID for CSS files.

        Returns
        -------
        bool
            True if tracked successfully.
        """
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False

        if file_type == "css":
            if path not in resources.watched_css:
                resources.watched_css.append(path)
            if asset_id:
                resources.css_asset_ids[path] = asset_id
        elif file_type == "script":
            if path not in resources.watched_scripts:
                resources.watched_scripts.append(path)
        return True

    def clear_watched_files(self, label: str) -> bool:
        """Clear all watched files for a window.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if cleared successfully.
        """
        resources = self._windows.get(label)
        if resources is None:
            return False
        resources.watched_css.clear()
        resources.watched_scripts.clear()
        resources.css_asset_ids.clear()
        return True

    def add_script(self, label: str, script_name: str) -> bool:
        """Track a script injection."""
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False
        if script_name not in resources.scripts_injected:
            resources.scripts_injected.append(script_name)
        return True

    def add_library(self, label: str, library_name: str) -> bool:
        """Track a library load."""
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False
        if library_name not in resources.libraries_loaded:
            resources.libraries_loaded.append(library_name)
        return True

    def set_data(self, label: str, key: str, value: Any) -> bool:
        """Set custom data for a window."""
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return False
        resources.custom_data[key] = value
        return True

    def get_data(self, label: str, key: str, default: Any = None) -> Any:
        """Get custom data for a window."""
        resources = self._windows.get(label)
        if resources is None or resources.is_destroyed:
            return default
        return resources.custom_data.get(key, default)

    def destroy(self, label: str) -> bool:
        """Destroy a window via IPC.

        Parameters
        ----------
        label : str
            The window label.

        Returns
        -------
        bool
            True if resources were destroyed, False if window not found.
        """
        from .. import runtime

        resources = self._windows.get(label)
        if resources is None:
            return False

        if resources.is_destroyed:
            debug(f"Window '{label}' already destroyed")
            return False

        debug(f"Destroying window '{label}'")

        # Clear all stored data
        resources.html_content = None
        resources.scripts_injected.clear()
        resources.libraries_loaded.clear()
        resources.custom_data.clear()
        resources.is_destroyed = True

        # Close via IPC
        runtime.close_window(label)

        # Destroy callbacks
        get_registry().destroy(label)

        # Remove from tracking
        del self._windows[label]

        # Force garbage collection
        gc.collect()

        debug(f"Destroyed window '{label}'")
        return True

    def destroy_all(self) -> int:
        """Destroy all tracked windows.

        Returns
        -------
        int
            Number of windows destroyed.
        """
        labels = list(self._windows.keys())
        count = 0
        for label in labels:
            if self.destroy(label):
                count += 1
        debug(f"Destroyed {count} windows")
        return count

    def get_labels(self) -> list[str]:
        """Get all active window labels.

        Returns
        -------
        list of str
            List of window labels.
        """
        return [label for label, resources in self._windows.items() if not resources.is_destroyed]

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about tracked windows.

        Returns
        -------
        dict[str, Any]
            Statistics dict.
        """
        active = [r for r in self._windows.values() if not r.is_destroyed]
        return {
            "total_tracked": len(self._windows),
            "active": len(active),
            "labels": self.get_labels(),
        }


class _LifecycleHolder:
    """Holder for the global lifecycle instance."""

    instance: WindowLifecycle | None = None


def get_lifecycle() -> WindowLifecycle:
    """Get the global window lifecycle manager.

    Returns
    -------
    WindowLifecycle
        The window lifecycle singleton.
    """
    if _LifecycleHolder.instance is None:
        _LifecycleHolder.instance = WindowLifecycle()
    return _LifecycleHolder.instance
