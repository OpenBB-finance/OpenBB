"""File watcher for hot reload functionality.

Uses watchdog for cross-platform file system monitoring with per-window debouncing.
"""

from __future__ import annotations

import threading

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from watchdog.events import (
    DirModifiedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from .log import debug, warn


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class WatchedFile:
    """Information about a watched file."""

    path: Path
    callback: Callable[[Path, str], None]
    label: str
    last_triggered: float = 0.0


@dataclass
class WindowDebouncer:
    """Per-window debounce state."""

    pending_paths: set[Path] = field(default_factory=set)
    timer: threading.Timer | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)


class FileWatcher:
    """Watch files for changes and trigger callbacks with debouncing.

    Supports per-window debouncing so rapid saves across multiple files
    trigger a single callback per window.
    """

    def __init__(self, debounce_ms: int = 100) -> None:
        """Initialize the file watcher.

        Parameters
        ----------
        debounce_ms : int, optional
            Debounce time in milliseconds. Changes within this
            window will be batched into a single callback.
        """
        self._debounce_ms = debounce_ms
        self._debounce_sec = debounce_ms / 1000.0

        # Map: path -> list of (label, callback)
        self._watches: dict[Path, list[WatchedFile]] = defaultdict(list)

        # Map: label -> WindowDebouncer
        self._debouncers: dict[str, WindowDebouncer] = {}

        # Map: directory -> set of watched files
        self._watched_dirs: dict[Path, set[Path]] = defaultdict(set)

        self._observer: Any = None  # Observer instance or None
        self._handler: _WatchHandler | None = None
        self._lock = threading.Lock()
        self._running = False

    @property
    def debounce_ms(self) -> int:
        """Get the debounce time in milliseconds."""
        return self._debounce_ms

    @debounce_ms.setter
    def debounce_ms(self, value: int) -> None:
        """Set the debounce time in milliseconds."""
        self._debounce_ms = max(10, value)
        self._debounce_sec = self._debounce_ms / 1000.0

    def watch(
        self,
        path: str | Path,
        callback: Callable[[Path, str], None],
        label: str,
    ) -> None:
        """Watch a file for changes.

        Parameters
        ----------
        path : str or Path
            Path to the file to watch.
        callback : Callable[[Path, str], None]
            Function to call when file changes.
            Receives (path, label) as arguments.
        label : str
            Window label for grouping debounce.
        """
        resolved = Path(path).resolve()
        if not resolved.exists():
            warn(f"Cannot watch non-existent file: {resolved}")
            return

        with self._lock:
            watched = WatchedFile(
                path=resolved,
                callback=callback,
                label=label,
            )
            self._watches[resolved].append(watched)

            # Track directory for observer
            directory = resolved.parent
            self._watched_dirs[directory].add(resolved)

            # Add observer for this directory if running
            if self._running and self._observer:
                self._ensure_directory_watched(directory)

            debug(f"Watching file: {resolved} for window {label}")

    def unwatch(self, path: str | Path, label: str | None = None) -> None:
        """Stop watching a file.

        Parameters
        ----------
        path : str or Path
            Path to stop watching.
        label : str or None, optional
            If provided, only remove watches for this label.
        """
        resolved = Path(path).resolve()

        with self._lock:
            if resolved not in self._watches:
                return

            if label is None:
                del self._watches[resolved]
            else:
                self._watches[resolved] = [w for w in self._watches[resolved] if w.label != label]
                if not self._watches[resolved]:
                    del self._watches[resolved]

            # Update directory tracking
            directory = resolved.parent
            if directory in self._watched_dirs:
                self._watched_dirs[directory].discard(resolved)
                if not self._watched_dirs[directory]:
                    del self._watched_dirs[directory]

            debug(f"Unwatched file: {resolved}" + (f" for {label}" if label else ""))

    def unwatch_label(self, label: str) -> None:
        """Stop watching all files for a window.

        Parameters
        ----------
        label : str
            Window label to unwatch.
        """
        with self._lock:
            # Collect paths to modify
            to_clean: list[Path] = []
            for path, watches in self._watches.items():
                self._watches[path] = [w for w in watches if w.label != label]
                if not self._watches[path]:
                    to_clean.append(path)

            # Clean up empty entries
            for path in to_clean:
                del self._watches[path]
                directory = path.parent
                if directory in self._watched_dirs:
                    self._watched_dirs[directory].discard(path)
                    if not self._watched_dirs[directory]:
                        del self._watched_dirs[directory]

            # Cancel any pending debounce timer
            if label in self._debouncers:
                debouncer = self._debouncers[label]
                if debouncer.timer:
                    debouncer.timer.cancel()
                del self._debouncers[label]

            debug(f"Unwatched all files for window: {label}")

    def start(self) -> None:
        """Start the file watcher."""
        if self._running:
            return

        with self._lock:
            self._observer = Observer()
            self._handler = _WatchHandler(self)

            # Watch all tracked directories
            for directory in self._watched_dirs:
                self._ensure_directory_watched(directory)

            self._observer.start()
            self._running = True
            debug("File watcher started")

    def stop(self) -> None:
        """Stop the file watcher."""
        if not self._running:
            return

        with self._lock:
            self._running = False

            # Cancel all pending debounce timers
            for debouncer in self._debouncers.values():
                if debouncer.timer:
                    debouncer.timer.cancel()
            self._debouncers.clear()

            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=2.0)
                self._observer = None
                self._handler = None

            debug("File watcher stopped")

    def _ensure_directory_watched(self, directory: Path) -> None:
        """Ensure a directory is being watched by the observer."""
        if not self._observer or not self._handler:
            return

        # Check if already watching this directory
        for watch in self._observer.emitters:
            if Path(watch.watch.path) == directory:
                return

        try:
            self._observer.schedule(self._handler, str(directory), recursive=False)
            debug(f"Watching directory: {directory}")
        except Exception as e:
            warn(f"Failed to watch directory {directory}: {e}")

    def _on_file_change(self, path: Path) -> None:
        """Handle a file change event."""
        if path not in self._watches:
            return

        watches = self._watches[path]
        if not watches:
            return

        # Group by label for debouncing
        labels_to_notify: dict[str, list[WatchedFile]] = defaultdict(list)
        for watch in watches:
            labels_to_notify[watch.label].append(watch)

        for label, label_watches in labels_to_notify.items():
            self._schedule_debounced_callback(label, path, label_watches)

    def _schedule_debounced_callback(
        self,
        label: str,
        path: Path,
        watches: list[WatchedFile],  # pylint: disable=unused-argument
    ) -> None:
        """Schedule a debounced callback for a window.

        Note: `watches` is currently unused as callbacks are re-fetched
        from self._watches when the debounce timer fires. This ensures
        any subscription changes are reflected.
        """
        if label not in self._debouncers:
            self._debouncers[label] = WindowDebouncer()

        debouncer = self._debouncers[label]

        with debouncer.lock:
            debouncer.pending_paths.add(path)

            # Cancel existing timer
            if debouncer.timer:
                debouncer.timer.cancel()

            # Schedule new timer
            def fire_callback() -> None:
                with debouncer.lock:
                    paths = list(debouncer.pending_paths)
                    debouncer.pending_paths.clear()
                    debouncer.timer = None

                for p in paths:
                    if p in self._watches:
                        for watch in self._watches[p]:
                            if watch.label == label:
                                try:
                                    watch.callback(p, label)
                                except Exception as e:
                                    warn(f"Error in file watch callback: {e}")

            debouncer.timer = threading.Timer(self._debounce_sec, fire_callback)
            debouncer.timer.daemon = True
            debouncer.timer.start()


class _WatchHandler(FileSystemEventHandler):
    """Watchdog event handler that forwards to FileWatcher."""

    def __init__(self, watcher: FileWatcher) -> None:
        super().__init__()
        self._watcher = watcher

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        src_path = event.src_path
        if isinstance(src_path, bytes):
            src_path = src_path.decode()
        path = Path(src_path).resolve()
        self._watcher._on_file_change(path)


# Global file watcher instance
_file_watcher: FileWatcher | None = None


def get_file_watcher(debounce_ms: int = 100) -> FileWatcher:
    """Get the global file watcher instance.

    Parameters
    ----------
    debounce_ms : int, optional
        Debounce time for new watcher.

    Returns
    -------
    FileWatcher
        Global FileWatcher instance.
    """
    global _file_watcher
    if _file_watcher is None:
        _file_watcher = FileWatcher(debounce_ms=debounce_ms)
    return _file_watcher


def stop_file_watcher() -> None:
    """Stop the global file watcher if running."""
    global _file_watcher
    if _file_watcher:
        _file_watcher.stop()
        _file_watcher = None
