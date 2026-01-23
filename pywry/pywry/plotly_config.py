"""Plotly configuration models for PyWry v2.

This module provides Pydantic models that mirror Plotly.js configuration options:
- PlotlyConfig: Top-level configuration object (displayModeBar, responsive, etc.)
- ModeBarConfig: Configuration for the mode bar (buttons to add/remove)
- ModeBarButton: Custom button definitions

All models use camelCase (via aliases) to match Plotly's JavaScript API exactly.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StandardButton(str, Enum):
    """Standard Plotly modebar buttons."""

    # 2D Cartesian
    ZOOM_2D = "zoom2d"
    PAN_2D = "pan2d"
    SELECT_2D = "select2d"
    LASSO_2D = "lasso2d"
    ZOOM_IN_2D = "zoomIn2d"
    ZOOM_OUT_2D = "zoomOut2d"
    AUTO_SCALE_2D = "autoScale2d"
    RESET_SCALE_2D = "resetScale2d"

    # 3D Cartesian
    ZOOM_3D = "zoom3d"
    PAN_3D = "pan3d"
    ORBIT_ROTATION = "orbitRotation"
    TABLE_ROTATION = "tableRotation"
    HANDLE_DRAG_3D = "handleDrag3d"
    RESET_CAMERA_DEFAULT_3D = "resetCameraDefault3d"
    RESET_CAMERA_LAST_SAVE_3D = "resetCameraLastSave3d"
    HOVER_CLOSEST_3D = "hoverClosest3d"

    # Cartesian
    HOVER_CLOSEST_CARTESIAN = "hoverClosestCartesian"
    HOVER_COMPARE_CARTESIAN = "hoverCompareCartesian"

    # Geo
    ZOOM_IN_GEO = "zoomInGeo"
    ZOOM_OUT_GEO = "zoomOutGeo"
    RESET_GEO = "resetGeo"
    HOVER_CLOSEST_GEO = "hoverClosestGeo"

    # Other
    TO_IMAGE = "toImage"
    SEND_DATA_TO_CLOUD = "sendDataToCloud"
    HOVER_CLOSEST_GL2D = "hoverClosestGl2d"
    HOVER_CLOSEST_PIE = "hoverClosestPie"
    TOGGLE_HOVER = "toggleHover"
    RESET_VIEWS = "resetViews"
    TOGGLE_SPIKELINES = "toggleSpikelines"
    RESET_VIEW_MAPBOX = "resetViewMapbox"


class PlotlyIconName(str, Enum):
    """Built-in Plotly icon names.

    These values must exactly match the keys in Plotly.Icons (from ploticon.js).
    See: https://github.com/plotly/plotly.js/blob/master/src/fonts/ploticon.js
    """

    # Navigation & view
    AUTOSCALE = "autoscale"
    HOME = "home"
    PAN = "pan"
    ZOOMBOX = "zoombox"
    ZOOM_PLUS = "zoom_plus"
    ZOOM_MINUS = "zoom_minus"

    # Selection
    LASSO = "lasso"
    SELECTBOX = "selectbox"

    # Drawing tools
    DRAW_LINE = "drawline"
    DRAW_RECT = "drawrect"
    DRAW_CIRCLE = "drawcircle"
    DRAW_OPEN_PATH = "drawopenpath"
    DRAW_CLOSED_PATH = "drawclosedpath"
    ERASE_SHAPE = "eraseshape"
    PENCIL = "pencil"

    # Other
    CAMERA = "camera"
    CAMERA_RETRO = "camera-retro"
    DISK = "disk"  # Save icon (NOT "save" - Plotly uses "disk")
    MOVIE = "movie"
    QUESTION = "question"
    UNDO = "undo"
    SPIKELINE = "spikeline"
    TOOLTIP_BASIC = "tooltip_basic"
    TOOLTIP_COMPARE = "tooltip_compare"
    Z_AXIS = "z-axis"
    ROTATE_3D = "3d_rotate"
    PLOTLY_LOGO = "plotlylogo"
    NEW_PLOTLY_LOGO = "newplotlylogo"


class SvgIcon(BaseModel):
    """Custom icon definition using SVG path or existing Plotly icon."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra="allow",
    )

    width: int = 500
    height: int = 500
    path: str | None = None  # SVG path string
    name: str | PlotlyIconName | None = None  # Reference to existing icon or name for new one
    svg: str | None = None  # Full SVG markup (alternative to path)
    transform: str | None = None  # SVG transform attribute


class ModeBarButton(BaseModel):
    """Configuration for a custom modebar button."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra="allow",
    )

    name: str
    title: str
    icon: SvgIcon | PlotlyIconName | str | dict[str, Any]
    click: str | None = None  # JS handler (use 'event' for PyWry events)
    attr: str | None = None
    val: Any | None = None
    toggle: bool | None = None

    # PyWry extensions
    event: str | None = None  # Event name to emit when clicked
    data: dict[str, Any] | None = None  # Data to include in event payload

    def to_js_config(self) -> dict[str, Any]:
        """Convert to JS-compatible config dict, handling PyWry event logic."""
        # This will be handled in templates.py generally, but good to have a method
        return self.model_dump(by_alias=True, exclude_none=True)


class ModeBarConfig(BaseModel):
    """Configuration for the mode bar."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra="allow",
    )

    orientation: Literal["v", "h"] = "h"
    bgcolor: str | None = None
    color: str | None = None
    active_color: str | None = None
    buttons_to_add: list[ModeBarButton | dict[str, Any]] | None = None
    buttons_to_remove: list[StandardButton | str] | None = None
    add_logo: bool = True  # Can be disabled by setting to False

    # Alias handling for Plotly's inconsistent naming
    remove: list[StandardButton | str] | None = Field(default=None, alias="modeBarButtonsToRemove")
    add: list[ModeBarButton | dict[str, Any]] | None = Field(
        default=None, alias="modeBarButtonsToAdd"
    )


class PlotlyConfig(BaseModel):
    """Top-level Plotly.js configuration object."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra="allow",
    )

    static_plot: bool = False
    plotly_server_url: str | None = None
    editable: bool = False
    edits: dict[str, bool] | None = None
    autosizable: bool = False
    responsive: bool = True
    fill_frame: bool = False
    frame_margins: float | int | None = None
    scroll_zoom: bool | Literal["cartesian", "gl3d", "geo", "mapbox"] = False
    double_click: Literal["reset+autosize", "reset", "autosize", False] = "reset+autosize"
    double_click_delay: int = 300
    show_tips: bool = True
    show_axis_drag_handles: bool = True
    show_axis_range_entry_boxes: bool = True
    show_link: bool = False
    send_data: bool = True
    link_text: str = "Edit chart"
    show_sources: bool = False
    display_mode_bar: bool | Literal["hover"] = "hover"
    display_logo: bool = Field(default=False, alias="displaylogo")  # Plotly uses lowercase
    mode_bar_buttons: (
        list[list[StandardButton | str | ModeBarButton | dict[str, Any]]] | bool | None
    ) = Field(default=None, alias="modeBarButtons")
    mode_bar_buttons_to_add: list[ModeBarButton | dict[str, Any]] | None = None
    mode_bar_buttons_to_remove: list[StandardButton | str] | None = None
    watermark: bool = False

    # Plotly.js localization
    locale: str | None = None
    locales: dict[str, Any] | None = None


class DownloadImageButton(ModeBarButton):
    """Button to download the chart as an image."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="toImage",
            title="Download plot as a png",
            icon=PlotlyIconName.CAMERA_RETRO,
            **kwargs,
        )


class ResetAxesButton(ModeBarButton):
    """Button to reset axes."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="resetViews", title="Reset axes", icon=PlotlyIconName.HOME, **kwargs)


class ToggleGridButton(ModeBarButton):
    """Button to toggle grid lines (Example custom button)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="toggleGrid",
            title="Toggle Grid",
            icon=PlotlyIconName.DRAW_LINE,
            event="plotly:toggle-grid",
            toggle=True,
            **kwargs,
        )
