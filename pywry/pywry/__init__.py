"""PyWry - Lightweight Python window manager using PyTauri.

This package provides a simple API for displaying HTML content in native
windows with support for Plotly.js, AG Grid, and custom event handling.
"""

# Inline notebook module - import functions directly
from . import inline
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
from .inline import show_dataframe, show_plotly
from .models import (
    HtmlContent,
    ThemeMode,
    WindowConfig,
    WindowMode,
)
from .notebook import (
    NotebookEnvironment,
    detect_notebook_environment,
    is_anywidget_available,
    should_use_inline_rendering,
)
from .widget import PyWryAgGridWidget, PyWryPlotlyWidget, PyWryWidget
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
    "NotebookEnvironment",
    "PyWry",
    "PyWryAgGridWidget",
    "PyWryPlotlyWidget",
    "PyWrySettings",
    "PyWryWidget",
    "SecuritySettings",
    "ThemeMode",
    "ThemeSettings",
    "TimeoutSettings",
    "WindowConfig",
    "WindowMode",
    "WindowSettings",
    "__version__",
    "detect_notebook_environment",
    "get_asset_loader",
    "get_lifecycle",
    "get_registry",
    "inline",
    "is_anywidget_available",
    "should_use_inline_rendering",
    "show_dataframe",
    "show_plotly",
]
