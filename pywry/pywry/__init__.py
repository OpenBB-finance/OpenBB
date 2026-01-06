"""PyWry - Lightweight Python window manager using PyTauri.

This package provides a simple API for displaying HTML content in native
windows with support for Plotly.js, AG Grid, and custom event handling.
"""

from .app import PyWry
from .asset_loader import AssetLoader, get_asset_loader
from .callbacks import CallbackFunc, get_registry
from .config import (
    AssetSettings,
    HotReloadSettings,
    LogSettings,
    PyWrySettings,
    SecuritySettings,
    ThemeSettings,
    TimeoutSettings,
    WindowSettings,
)
from .hot_reload import HotReloadManager
from .models import (
    HtmlContent,
    ThemeMode,
    WindowConfig,
    WindowMode,
)
from .window_manager import get_lifecycle


__version__ = "2.0.0"

__all__ = [
    "AssetLoader",
    "AssetSettings",
    "CallbackFunc",
    "HotReloadManager",
    "HotReloadSettings",
    "HtmlContent",
    "LogSettings",
    "PyWry",
    "PyWrySettings",
    "SecuritySettings",
    "ThemeMode",
    "ThemeSettings",
    "TimeoutSettings",
    "WindowConfig",
    "WindowMode",
    "WindowSettings",
    "__version__",
    "get_asset_loader",
    "get_lifecycle",
    "get_registry",
]
