"""PyWry - Lightweight Python window manager using PyTauri.

This package provides a simple API for displaying HTML content in native
windows with support for Plotly.js, AG Grid, and custom event handling.
"""

# Inline notebook module - import functions directly
from . import inline
from .app import PyWry
from .asset_loader import AssetLoader, get_asset_loader
from .callbacks import CallbackFunc, WidgetType, get_registry
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
from .grid import (
    ColDef,
    ColGroupDef,
    DefaultColDef,
    GridOptions,
    RowSelection,
    build_grid_config,
    to_js_grid_config,
)
from .hot_reload import HotReloadManager
from .inline import block, show_dataframe, show_plotly
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
from .plotly_config import (
    ModeBarButton,
    ModeBarConfig,
    PlotlyConfig,
    PlotlyIconName,
    StandardButton,
    SvgIcon,
)
from .state_mixins import (
    GridStateMixin,
    PlotlyStateMixin,
    ToolbarStateMixin,
)
from .toolbar import (
    Button,
    Checkbox,
    DateInput,
    Div,
    Marquee,
    MultiSelect,
    NumberInput,
    Option,
    RadioGroup,
    RangeInput,
    SearchInput,
    SecretInput,
    Select,
    SliderInput,
    TabGroup,
    TextArea,
    TextInput,
    TickerItem,
    Toggle,
    Toolbar,
    ToolbarItem,
)
from .widget import PyWryAgGridWidget, PyWryPlotlyWidget, PyWryWidget
from .window_manager import BrowserMode, get_lifecycle


__version__ = "2.0.0"

__all__ = [
    "AssetLoader",
    "AssetSettings",
    "BrowserMode",
    "Button",
    "CallbackFunc",
    "Checkbox",
    "ColDef",
    "ColGroupDef",
    "DateInput",
    "DefaultColDef",
    "Div",
    "GridOptions",
    "GridStateMixin",
    "HotReloadManager",
    "HotReloadSettings",
    "HtmlContent",
    "LogSettings",
    "Marquee",
    "ModeBarButton",
    "ModeBarConfig",
    "MultiSelect",
    "NotebookEnvironment",
    "NumberInput",
    "Option",
    "PlotlyConfig",
    "PlotlyIconName",
    "PlotlyStateMixin",
    "PyWry",
    "PyWryAgGridWidget",
    "PyWryPlotlyWidget",
    "PyWrySettings",
    "PyWryWidget",
    "RadioGroup",
    "RangeInput",
    "RowSelection",
    "SearchInput",
    "SecretInput",
    "SecuritySettings",
    "Select",
    "SliderInput",
    "StandardButton",
    "SvgIcon",
    "TabGroup",
    "TextArea",
    "TextInput",
    "ThemeMode",
    "ThemeSettings",
    "TickerItem",
    "TimeoutSettings",
    "Toggle",
    "Toolbar",
    "ToolbarItem",
    "ToolbarStateMixin",
    "WidgetType",
    "WindowConfig",
    "WindowMode",
    "WindowSettings",
    "__version__",
    "block",
    "build_grid_config",
    "detect_notebook_environment",
    "get_asset_loader",
    "get_lifecycle",
    "get_registry",
    "inline",
    "is_anywidget_available",
    "should_use_inline_rendering",
    "show_dataframe",
    "show_plotly",
    "to_js_grid_config",
]
