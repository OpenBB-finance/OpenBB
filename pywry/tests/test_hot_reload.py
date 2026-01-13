"""Unit tests for hot reload manager.

Tests cover:
- HotReloadManager initialization
- Start/stop lifecycle
- Window enable/disable for hot reload
- CSS injection
- Page refresh
- File change handling

All tests use mocks for dependencies (FileWatcher, AssetLoader, callbacks).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from pywry.hot_reload import HotReloadManager


# =============================================================================
# Mock Fixtures
# =============================================================================


def create_mock_settings() -> MagicMock:
    """Create a mock HotReloadSettings."""
    settings = MagicMock()
    settings.debounce_ms = 100
    settings.css_reload = "inject"
    settings.enabled = True
    return settings


def create_mock_asset_loader() -> MagicMock:
    """Create a mock AssetLoader."""
    loader = MagicMock()
    loader.resolve_path = MagicMock(side_effect=lambda p: Path(p).resolve())
    loader.get_asset_id = MagicMock(side_effect=lambda p: f"asset_{p.name}")
    loader.load_css = MagicMock(return_value="body { color: red; }")
    loader.invalidate = MagicMock()
    return loader


def create_mock_file_watcher() -> MagicMock:
    """Create a mock FileWatcher."""
    watcher = MagicMock()
    watcher.start = MagicMock()
    watcher.stop = MagicMock()
    watcher.watch = MagicMock()
    watcher.unwatch = MagicMock()
    watcher.unwatch_label = MagicMock()
    return watcher


def create_mock_content(
    css_files: list[Path] | None = None,
    script_files: list[Path] | None = None,
    watch: bool = True,
) -> MagicMock:
    """Create a mock HtmlContent."""
    content = MagicMock()
    content.css_files = css_files or []
    content.script_files = script_files or []
    content.watch = watch
    return content


# =============================================================================
# Initialization Tests
# =============================================================================


class TestHotReloadManagerInit:
    """Test HotReloadManager initialization."""

    def test_default_initialization(self) -> None:
        """Test initialization with defaults."""
        with (
            patch("pywry.hot_reload.get_asset_loader") as mock_get_loader,
            patch("pywry.hot_reload.get_file_watcher") as mock_get_watcher,
        ):
            mock_get_loader.return_value = create_mock_asset_loader()
            mock_get_watcher.return_value = create_mock_file_watcher()

            manager = HotReloadManager()

            assert manager.is_running is False
            assert manager.settings is not None

    def test_initialization_with_settings(self) -> None:
        """Test initialization with custom settings."""
        settings = create_mock_settings()
        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()

        manager = HotReloadManager(
            settings=settings,
            asset_loader=loader,
            file_watcher=watcher,
        )

        assert manager.settings is settings
        assert manager.is_running is False

    def test_is_running_property(self) -> None:
        """Test is_running property."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        assert manager.is_running is False


# =============================================================================
# Start/Stop Tests
# =============================================================================


class TestHotReloadManagerStartStop:
    """Test HotReloadManager start/stop lifecycle."""

    def test_start(self) -> None:
        """Test starting the manager."""
        watcher = create_mock_file_watcher()
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.start()

        assert manager.is_running is True
        watcher.start.assert_called_once()

    def test_start_idempotent(self) -> None:
        """Test that starting twice doesn't call watcher.start twice."""
        watcher = create_mock_file_watcher()
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.start()
        manager.start()

        watcher.start.assert_called_once()

    def test_stop(self) -> None:
        """Test stopping the manager."""
        watcher = create_mock_file_watcher()
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.start()
        manager.stop()

        assert manager.is_running is False
        watcher.stop.assert_called_once()

    def test_stop_without_start(self) -> None:
        """Test stopping without starting is safe."""
        watcher = create_mock_file_watcher()
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.stop()  # Should not raise

        watcher.stop.assert_not_called()


# =============================================================================
# Enable/Disable Window Tests
# =============================================================================


class TestEnableDisableWindow:
    """Test enabling/disabling hot reload for windows."""

    def test_enable_for_window_with_css(self, tmp_path: Path) -> None:
        """Test enabling hot reload with CSS files."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=loader,
            file_watcher=watcher,
        )

        manager.enable_for_window("window1", content)

        # Verify watcher.watch was called
        watcher.watch.assert_called_once()
        call_args = watcher.watch.call_args
        assert call_args[0][2] == "window1"  # label

    def test_enable_for_window_with_script(self, tmp_path: Path) -> None:
        """Test enabling hot reload with script files."""
        script_file = tmp_path / "app.js"
        script_file.write_text("console.log('hello');")

        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(script_files=[script_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=loader,
            file_watcher=watcher,
        )

        manager.enable_for_window("window1", content)

        watcher.watch.assert_called_once()

    def test_enable_for_window_watch_false(self, tmp_path: Path) -> None:
        """Test that watch=False prevents watching."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file], watch=False)

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.enable_for_window("window1", content)

        watcher.watch.assert_not_called()

    def test_disable_for_window(self, tmp_path: Path) -> None:
        """Test disabling hot reload for a window."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=watcher,
        )

        manager.enable_for_window("window1", content)
        manager.disable_for_window("window1")

        watcher.unwatch_label.assert_called_once_with("window1")


# =============================================================================
# Callback Tests
# =============================================================================


class TestCallbacks:
    """Test callback configuration."""

    def test_set_inject_css_callback(self) -> None:
        """Test setting CSS injection callback."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        callback = MagicMock()
        manager.set_inject_css_callback(callback)

        assert manager._inject_css_callback is callback

    def test_set_refresh_callback(self) -> None:
        """Test setting refresh callback."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        callback = MagicMock()
        manager.set_refresh_callback(callback)

        assert manager._refresh_callback is callback


# =============================================================================
# CSS Reload Tests
# =============================================================================


class TestReloadCss:
    """Test CSS reloading functionality."""

    def test_reload_css_success(self, tmp_path: Path) -> None:
        """Test successful CSS reload."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body { color: blue; }")

        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=loader,
            file_watcher=watcher,
        )

        inject_callback = MagicMock()
        manager.set_inject_css_callback(inject_callback)
        manager.enable_for_window("window1", content)

        result = manager.reload_css("window1")

        assert result is True
        inject_callback.assert_called_once()

    def test_reload_css_no_callback(self, tmp_path: Path) -> None:
        """Test CSS reload without callback configured."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        manager.enable_for_window("window1", content)
        result = manager.reload_css("window1")

        assert result is False

    def test_reload_css_unknown_window(self) -> None:
        """Test CSS reload for unknown window."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        result = manager.reload_css("unknown_window")

        assert result is False


# =============================================================================
# Refresh Window Tests
# =============================================================================


class TestRefreshWindow:
    """Test window refresh functionality."""

    def test_refresh_window_success(self) -> None:
        """Test successful window refresh."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        refresh_callback = MagicMock()
        manager.set_refresh_callback(refresh_callback)

        result = manager.refresh_window("window1")

        assert result is True
        refresh_callback.assert_called_once_with("window1")

    def test_refresh_window_no_callback(self) -> None:
        """Test refresh without callback configured."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        result = manager.refresh_window("window1")

        assert result is False

    def test_refresh_window_callback_exception(self) -> None:
        """Test refresh when callback raises exception."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        refresh_callback = MagicMock(side_effect=RuntimeError("Refresh failed"))
        manager.set_refresh_callback(refresh_callback)

        result = manager.refresh_window("window1")

        assert result is False


# =============================================================================
# File Change Handler Tests
# =============================================================================


class TestFileChangeHandler:
    """Test file change event handling."""

    def test_css_change_injects(self, tmp_path: Path) -> None:
        """Test that CSS change triggers injection."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        settings = create_mock_settings()
        settings.css_reload = "inject"
        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=settings,
            asset_loader=loader,
            file_watcher=watcher,
        )

        inject_callback = MagicMock()
        manager.set_inject_css_callback(inject_callback)
        manager.enable_for_window("window1", content)

        # Simulate file change
        resolved_path = loader.resolve_path(css_file)
        manager._on_file_change(resolved_path, "window1")

        inject_callback.assert_called_once()

    def test_css_change_refresh_mode(self, tmp_path: Path) -> None:
        """Test that CSS change in refresh mode triggers refresh."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        settings = create_mock_settings()
        settings.css_reload = "refresh"
        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=settings,
            asset_loader=loader,
            file_watcher=watcher,
        )

        refresh_callback = MagicMock()
        manager.set_refresh_callback(refresh_callback)
        manager.enable_for_window("window1", content)

        resolved_path = loader.resolve_path(css_file)
        manager._on_file_change(resolved_path, "window1")

        refresh_callback.assert_called_once_with("window1")

    def test_script_change_always_refreshes(self, tmp_path: Path) -> None:
        """Test that script change always triggers refresh."""
        script_file = tmp_path / "app.js"
        script_file.write_text("console.log('hello');")

        settings = create_mock_settings()
        loader = create_mock_asset_loader()
        watcher = create_mock_file_watcher()
        content = create_mock_content(script_files=[script_file])

        manager = HotReloadManager(
            settings=settings,
            asset_loader=loader,
            file_watcher=watcher,
        )

        refresh_callback = MagicMock()
        manager.set_refresh_callback(refresh_callback)
        manager.enable_for_window("window1", content)

        resolved_path = loader.resolve_path(script_file)
        manager._on_file_change(resolved_path, "window1")

        refresh_callback.assert_called_once_with("window1")

    def test_unknown_window_ignored(self) -> None:
        """Test that changes for unknown windows are ignored."""
        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=create_mock_asset_loader(),
            file_watcher=create_mock_file_watcher(),
        )

        refresh_callback = MagicMock()
        manager.set_refresh_callback(refresh_callback)

        # Simulate change for unknown window
        manager._on_file_change(Path("/some/file.css"), "unknown_window")

        refresh_callback.assert_not_called()


# =============================================================================
# Get Watched Files Tests
# =============================================================================


class TestGetWatchedFiles:
    """Test get_watched_files method."""

    def test_get_watched_files_specific_window(self, tmp_path: Path) -> None:
        """Test getting watched files for specific window."""
        css_file = tmp_path / "style.css"
        css_file.write_text("body {}")

        loader = create_mock_asset_loader()
        content = create_mock_content(css_files=[css_file])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=loader,
            file_watcher=create_mock_file_watcher(),
        )

        manager.enable_for_window("window1", content)
        files = manager.get_watched_files("window1")

        assert "window1" in files
        assert len(files["window1"]) == 1

    def test_get_watched_files_all(self, tmp_path: Path) -> None:
        """Test getting all watched files."""
        css_file1 = tmp_path / "style1.css"
        css_file2 = tmp_path / "style2.css"
        css_file1.write_text("body {}")
        css_file2.write_text("p {}")

        loader = create_mock_asset_loader()
        content1 = create_mock_content(css_files=[css_file1])
        content2 = create_mock_content(css_files=[css_file2])

        manager = HotReloadManager(
            settings=create_mock_settings(),
            asset_loader=loader,
            file_watcher=create_mock_file_watcher(),
        )

        manager.enable_for_window("window1", content1)
        manager.enable_for_window("window2", content2)

        files = manager.get_watched_files()

        assert "window1" in files
        assert "window2" in files
