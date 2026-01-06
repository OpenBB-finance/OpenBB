"""Hot reload manager for automatic CSS/JS reloading.

Coordinates file watching, asset loading, and IPC injection for
live development workflow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .asset_loader import AssetLoader, get_asset_loader
from .log import debug, info, warn
from .watcher import FileWatcher, get_file_watcher


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from .config import HotReloadSettings
    from .models import HtmlContent


class HotReloadManager:
    """Manages hot reload for CSS and JavaScript files.

    - CSS changes: Inject updated styles without page reload
    - JS changes: Trigger full page refresh (with scroll position preservation)
    """

    def __init__(
        self,
        settings: HotReloadSettings | None = None,
        asset_loader: AssetLoader | None = None,
        file_watcher: FileWatcher | None = None,
    ) -> None:
        """Initialize the hot reload manager.

        Parameters
        ----------
        settings : HotReloadSettings or None, optional
            Hot reload settings. Uses defaults if not provided.
        asset_loader : AssetLoader or None, optional
            Asset loader instance. Creates default if not provided.
        file_watcher : FileWatcher or None, optional
            File watcher instance. Creates default if not provided.
        """
        if settings is None:
            from .config import HotReloadSettings
            settings = HotReloadSettings()

        self._settings = settings
        self._asset_loader = asset_loader or get_asset_loader()
        self._file_watcher = file_watcher or get_file_watcher(settings.debounce_ms)

        # Track watched files per window: label -> {path -> type}
        self._window_files: dict[str, dict[Path, str]] = {}

        # Track asset IDs for CSS injection: label -> {path -> asset_id}
        self._asset_ids: dict[str, dict[Path, str]] = {}

        # Callback for IPC commands (set by PyWry)
        self._inject_css_callback: Callable[..., Any] | None = None
        self._refresh_callback: Callable[..., Any] | None = None

        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if hot reload is active."""
        return self._running

    @property
    def settings(self) -> HotReloadSettings:
        """Get current settings."""
        return self._settings

    def set_inject_css_callback(
        self,
        callback: Callable[..., Any],
    ) -> None:
        """Set the callback for CSS injection.

        Parameters
        ----------
        callback : Callable[..., Any]
            Function(label, css, asset_id) to inject CSS.
        """
        self._inject_css_callback = callback

    def set_refresh_callback(
        self,
        callback: Callable[..., Any],
    ) -> None:
        """Set the callback for page refresh.

        Parameters
        ----------
        callback : Callable[..., Any]
            Function(label) to refresh a window.
        """
        self._refresh_callback = callback

    def start(self) -> None:
        """Start the hot reload manager."""
        if self._running:
            return

        self._file_watcher.start()
        self._running = True
        info("Hot reload manager started")

    def stop(self) -> None:
        """Stop the hot reload manager."""
        if not self._running:
            return

        self._file_watcher.stop()
        self._running = False
        self._window_files.clear()
        self._asset_ids.clear()
        info("Hot reload manager stopped")

    def enable_for_window(
        self,
        label: str,
        content: HtmlContent,
    ) -> None:
        """Enable hot reload for a window's assets.

        Parameters
        ----------
        label : str
            Window label.
        content : HtmlContent
            HTML content with file references.
        """
        if not content.watch:
            return

        self._window_files[label] = {}
        self._asset_ids[label] = {}

        # Watch CSS files
        if content.css_files:
            for path in content.css_files:
                resolved = self._asset_loader.resolve_path(path)
                self._window_files[label][resolved] = "css"
                asset_id = self._asset_loader.get_asset_id(resolved)
                self._asset_ids[label][resolved] = asset_id
                self._file_watcher.watch(
                    resolved,
                    self._on_file_change,
                    label,
                )
                debug(f"Watching CSS: {resolved} for window {label}")

        # Watch script files
        if content.script_files:
            for path in content.script_files:
                resolved = self._asset_loader.resolve_path(path)
                self._window_files[label][resolved] = "script"
                self._file_watcher.watch(
                    resolved,
                    self._on_file_change,
                    label,
                )
                debug(f"Watching script: {resolved} for window {label}")

        if self._window_files[label]:
            info(
                f"Hot reload enabled for window {label}: "
                f"{len(self._window_files[label])} file(s)"
            )

    def disable_for_window(self, label: str) -> None:
        """Disable hot reload for a window.

        Parameters
        ----------
        label : str
            Window label.
        """
        self._file_watcher.unwatch_label(label)
        self._window_files.pop(label, None)
        self._asset_ids.pop(label, None)
        debug(f"Hot reload disabled for window {label}")

    def reload_css(self, label: str, path: Path | None = None) -> bool:
        """Reload CSS for a window.

        Parameters
        ----------
        label : str
            Window label.
        path : Path or None, optional
            Specific CSS file to reload. If None, reloads all.

        Returns
        -------
        bool
            True if CSS was injected, False otherwise.
        """
        if label not in self._window_files:
            return False

        if not self._inject_css_callback:
            warn("No CSS injection callback configured")
            return False

        files = self._window_files[label]
        css_files = [p for p, t in files.items() if t == "css"]

        if path is not None:
            resolved = self._asset_loader.resolve_path(path)
            if resolved in css_files:
                css_files = [resolved]
            else:
                return False

        success = False
        for css_path in css_files:
            # Invalidate cache and reload
            self._asset_loader.invalidate(css_path)
            css_content = self._asset_loader.load_css(css_path, use_cache=False)

            if css_content:
                asset_id = self._asset_ids.get(label, {}).get(css_path)
                if asset_id:
                    try:
                        self._inject_css_callback(label, css_content, asset_id)
                        debug(f"Injected CSS: {css_path} into window {label}")
                        success = True
                    except Exception as e:
                        warn(f"Failed to inject CSS: {e}")

        return success

    def refresh_window(self, label: str) -> bool:
        """Trigger a full page refresh for a window.

        Parameters
        ----------
        label : str
            Window label.

        Returns
        -------
        bool
            True if refresh was triggered, False otherwise.
        """
        if not self._refresh_callback:
            warn("No refresh callback configured")
            return False

        try:
            self._refresh_callback(label)
            debug(f"Refreshed window {label}")
            return True
        except Exception as e:
            warn(f"Failed to refresh window: {e}")
            return False

    def _on_file_change(self, path: Path, label: str) -> None:
        """Handle file change event.

        Parameters
        ----------
        path : Path
            Path to changed file.
        label : str
            Window label.
        """
        if label not in self._window_files:
            return

        file_type = self._window_files[label].get(path)
        if not file_type:
            return

        debug(f"File changed: {path} ({file_type}) for window {label}")

        if file_type == "css":
            if self._settings.css_reload == "inject":
                self.reload_css(label, path)
            else:
                self.refresh_window(label)
        elif file_type == "script":
            # Scripts always trigger full refresh
            self.refresh_window(label)

    def get_watched_files(self, label: str | None = None) -> dict[str, list[Path]]:
        """Get list of watched files.

        Parameters
        ----------
        label : str or None, optional
            Specific window label. If None, returns all.

        Returns
        -------
        dict[str, list[Path]]
            Dict mapping labels to lists of watched paths.
        """
        if label is not None:
            if label in self._window_files:
                return {label: list(self._window_files[label].keys())}
            return {}

        return {
            lbl: list(files.keys())
            for lbl, files in self._window_files.items()
        }


# Global hot reload manager instance
_hot_reload_manager: HotReloadManager | None = None


def get_hot_reload_manager(
    settings: HotReloadSettings | None = None,
) -> HotReloadManager:
    """Get the global hot reload manager instance.

    Parameters
    ----------
    settings : HotReloadSettings or None, optional
        Settings for new manager creation.

    Returns
    -------
    HotReloadManager
        Global HotReloadManager instance.
    """
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = HotReloadManager(settings=settings)
    return _hot_reload_manager


def stop_hot_reload_manager() -> None:
    """Stop the global hot reload manager if running."""
    global _hot_reload_manager
    if _hot_reload_manager:
        _hot_reload_manager.stop()
        _hot_reload_manager = None
