"""Unit tests for file watcher module.

Tests cover:
- WatchedFile dataclass
- WindowDebouncer dataclass
- FileWatcher class with mocked Observer and Timer
- Debounce functionality
- Global watcher functions

All tests use mocks for file system and threading operations.
"""

from __future__ import annotations

import threading
import time

from pathlib import Path
from unittest.mock import MagicMock, patch

from pywry.watcher import (
    FileWatcher,
    WatchedFile,
    WindowDebouncer,
    get_file_watcher,
    stop_file_watcher,
)


# =============================================================================
# WatchedFile Tests
# =============================================================================


class TestWatchedFile:
    """Test WatchedFile dataclass."""

    def test_creation(self) -> None:
        """Test creating a WatchedFile."""
        callback = MagicMock()
        watched = WatchedFile(
            path=Path("/test/file.txt"),
            callback=callback,
            label="window1",
        )
        assert watched.path == Path("/test/file.txt")
        assert watched.callback is callback
        assert watched.label == "window1"
        assert watched.last_triggered == 0.0

    def test_last_triggered_default(self) -> None:
        """Test last_triggered defaults to 0.0."""
        watched = WatchedFile(
            path=Path("/test/file.txt"),
            callback=MagicMock(),
            label="window1",
        )
        assert watched.last_triggered == 0.0

    def test_last_triggered_custom(self) -> None:
        """Test last_triggered with custom value."""
        watched = WatchedFile(
            path=Path("/test/file.txt"),
            callback=MagicMock(),
            label="window1",
            last_triggered=12345.0,
        )
        assert watched.last_triggered == 12345.0


# =============================================================================
# WindowDebouncer Tests
# =============================================================================


class TestWindowDebouncer:
    """Test WindowDebouncer dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        debouncer = WindowDebouncer()
        assert debouncer.pending_paths == set()
        assert debouncer.timer is None
        assert isinstance(debouncer.lock, type(threading.Lock()))

    def test_pending_paths(self) -> None:
        """Test adding pending paths."""
        debouncer = WindowDebouncer()
        debouncer.pending_paths.add(Path("/test/file1.txt"))
        debouncer.pending_paths.add(Path("/test/file2.txt"))
        assert len(debouncer.pending_paths) == 2

    def test_lock_is_usable(self) -> None:
        """Test that the lock is usable."""
        debouncer = WindowDebouncer()
        with debouncer.lock:
            debouncer.pending_paths.add(Path("/test/file.txt"))
        assert Path("/test/file.txt") in debouncer.pending_paths


# =============================================================================
# FileWatcher Initialization Tests
# =============================================================================


class TestFileWatcherInit:
    """Test FileWatcher initialization."""

    def test_default_debounce(self) -> None:
        """Test default debounce time."""
        watcher = FileWatcher()
        assert watcher.debounce_ms == 100

    def test_custom_debounce(self) -> None:
        """Test custom debounce time."""
        watcher = FileWatcher(debounce_ms=500)
        assert watcher.debounce_ms == 500

    def test_debounce_property_setter(self) -> None:
        """Test debounce_ms setter."""
        watcher = FileWatcher()
        watcher.debounce_ms = 250
        assert watcher.debounce_ms == 250

    def test_debounce_minimum(self) -> None:
        """Test that debounce has a minimum value."""
        watcher = FileWatcher()
        watcher.debounce_ms = 5  # Below minimum
        assert watcher.debounce_ms >= 10


# =============================================================================
# FileWatcher Watch/Unwatch Tests (with mocked filesystem)
# =============================================================================


class TestFileWatcherWatch:
    """Test FileWatcher watch/unwatch methods."""

    def test_watch_existing_file(self, tmp_path: Path) -> None:
        """Test watching an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback, "window1")

        # Verify internal state
        resolved = test_file.resolve()
        assert resolved in watcher._watches
        assert len(watcher._watches[resolved]) == 1
        assert watcher._watches[resolved][0].callback is callback

    def test_watch_nonexistent_file(self, tmp_path: Path) -> None:
        """Test watching a non-existent file does nothing."""
        test_file = tmp_path / "nonexistent.txt"
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback, "window1")

        # Should not add to watches
        resolved = test_file.resolve()
        assert resolved not in watcher._watches

    def test_watch_multiple_callbacks(self, tmp_path: Path) -> None:
        """Test watching same file with multiple callbacks."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback1 = MagicMock()
        callback2 = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback1, "window1")
        watcher.watch(test_file, callback2, "window2")

        resolved = test_file.resolve()
        assert len(watcher._watches[resolved]) == 2

    def test_unwatch_file(self, tmp_path: Path) -> None:
        """Test unwatching a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback, "window1")
        watcher.unwatch(test_file)

        resolved = test_file.resolve()
        assert resolved not in watcher._watches

    def test_unwatch_by_label(self, tmp_path: Path) -> None:
        """Test unwatching by specific label."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback1 = MagicMock()
        callback2 = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback1, "window1")
        watcher.watch(test_file, callback2, "window2")
        watcher.unwatch(test_file, label="window1")

        resolved = test_file.resolve()
        assert len(watcher._watches[resolved]) == 1
        assert watcher._watches[resolved][0].label == "window2"

    def test_unwatch_label_all(self, tmp_path: Path) -> None:
        """Test unwatching all files for a label."""
        file1 = tmp_path / "test1.txt"
        file2 = tmp_path / "test2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(file1, callback, "window1")
        watcher.watch(file2, callback, "window1")
        watcher.unwatch_label("window1")

        assert file1.resolve() not in watcher._watches
        assert file2.resolve() not in watcher._watches


# =============================================================================
# FileWatcher Start/Stop Tests (with mocked Observer)
# =============================================================================


class TestFileWatcherStartStop:
    """Test FileWatcher start/stop methods."""

    @patch("pywry.watcher.Observer")
    def test_start_creates_observer(self, mock_observer_class: MagicMock) -> None:
        """Test that start creates an Observer."""
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer

        watcher = FileWatcher()
        watcher.start()

        mock_observer_class.assert_called_once()
        mock_observer.start.assert_called_once()
        assert watcher._running is True

    @patch("pywry.watcher.Observer")
    def test_start_idempotent(self, mock_observer_class: MagicMock) -> None:
        """Test that calling start twice doesn't create two observers."""
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer

        watcher = FileWatcher()
        watcher.start()
        watcher.start()

        mock_observer_class.assert_called_once()

    @patch("pywry.watcher.Observer")
    def test_stop_stops_observer(self, mock_observer_class: MagicMock) -> None:
        """Test that stop stops the Observer."""
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer

        watcher = FileWatcher()
        watcher.start()
        watcher.stop()

        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()
        assert watcher._running is False

    @patch("pywry.watcher.Observer")
    def test_stop_without_start(self, mock_observer_class: MagicMock) -> None:
        """Test that stop without start is safe."""
        watcher = FileWatcher()
        watcher.stop()  # Should not raise

        mock_observer_class.assert_not_called()


# =============================================================================
# File Change Callback Tests (with mocked threading)
# =============================================================================


class TestFileChangeCallbacks:
    """Test file change callback triggering."""

    def test_on_file_change_triggers_callback(self, tmp_path: Path) -> None:
        """Test that file changes trigger callbacks."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher(debounce_ms=10)  # Short debounce for test
        watcher.watch(test_file, callback, "window1")

        # Simulate file change
        resolved = test_file.resolve()
        watcher._on_file_change(resolved)

        # Wait for debounce (longer wait for CI timer scheduling variance)
        time.sleep(0.2)

        callback.assert_called_once_with(resolved, "window1")

    def test_on_file_change_unwatched_file(self, tmp_path: Path) -> None:
        """Test that changes to unwatched files are ignored."""
        test_file = tmp_path / "test.txt"
        unwatched_file = tmp_path / "other.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(test_file, callback, "window1")

        # Simulate change to unwatched file
        watcher._on_file_change(unwatched_file.resolve())

        # Wait a bit (ensure debounce timer has time to fire if it would)
        time.sleep(0.2)

        callback.assert_not_called()

    def test_debounce_batches_changes(self, tmp_path: Path) -> None:
        """Test that rapid changes are batched."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher(debounce_ms=50)
        watcher.watch(test_file, callback, "window1")

        resolved = test_file.resolve()

        # Simulate rapid changes
        watcher._on_file_change(resolved)
        watcher._on_file_change(resolved)
        watcher._on_file_change(resolved)

        # Wait for debounce (longer wait for CI timer scheduling variance)
        time.sleep(0.3)

        # Should only call once despite multiple changes
        assert callback.call_count == 1


# =============================================================================
# Global Watcher Functions Tests
# =============================================================================


class TestGlobalWatcherFunctions:
    """Test global watcher utility functions."""

    def test_get_file_watcher_creates_singleton(self) -> None:
        """Test that get_file_watcher creates a singleton."""
        # Reset global state
        stop_file_watcher()

        watcher1 = get_file_watcher()
        watcher2 = get_file_watcher()

        assert watcher1 is watcher2

        # Cleanup
        stop_file_watcher()

    def test_get_file_watcher_respects_debounce(self) -> None:
        """Test that first call sets debounce time."""
        stop_file_watcher()

        watcher = get_file_watcher(debounce_ms=250)
        assert watcher.debounce_ms == 250

        stop_file_watcher()

    def test_stop_file_watcher(self) -> None:
        """Test stopping the global watcher."""
        stop_file_watcher()  # Ensure clean state

        watcher = get_file_watcher()
        watcher.start()

        stop_file_watcher()

        # Getting again should create new instance
        watcher2 = get_file_watcher()
        assert watcher2 is not watcher

        stop_file_watcher()


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_callback_exception_handled(self, tmp_path: Path) -> None:
        """Test that callback exceptions don't crash the watcher."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        bad_callback = MagicMock(side_effect=RuntimeError("Callback error"))

        watcher = FileWatcher(debounce_ms=10)
        watcher.watch(test_file, bad_callback, "window1")

        # Simulate file change - should not raise
        resolved = test_file.resolve()
        watcher._on_file_change(resolved)

        # Wait for debounce timer (longer wait for CI timer scheduling variance)
        time.sleep(0.2)

        # Callback was called (and raised)
        bad_callback.assert_called_once()

    def test_watch_path_string(self, tmp_path: Path) -> None:
        """Test watching with string path instead of Path object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        callback = MagicMock()

        watcher = FileWatcher()
        watcher.watch(str(test_file), callback, "window1")

        resolved = test_file.resolve()
        assert resolved in watcher._watches

    def test_unwatch_nonexistent(self) -> None:
        """Test unwatching a file that was never watched."""
        watcher = FileWatcher()
        # Should not raise
        watcher.unwatch(Path("/nonexistent/file.txt"))

    def test_unwatch_label_nonexistent(self) -> None:
        """Test unwatching a label that was never used."""
        watcher = FileWatcher()
        # Should not raise
        watcher.unwatch_label("nonexistent_window")
