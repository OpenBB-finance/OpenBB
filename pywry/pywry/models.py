"""Pydantic models for PyWry v2."""

from __future__ import annotations

import re

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ThemeMode(str, Enum):
    """Window theme mode."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class WindowMode(str, Enum):
    """Window management mode."""

    NEW_WINDOW = "new_window"
    SINGLE_WINDOW = "single_window"
    MULTI_WINDOW = "multi_window"


class WindowConfig(BaseModel):
    """Configuration for window creation."""

    title: str = "PyWry"
    width: int = Field(default=1280, ge=200)
    height: int = Field(default=720, ge=150)
    min_width: int = Field(default=400, ge=100)
    min_height: int = Field(default=300, ge=100)
    theme: ThemeMode = ThemeMode.DARK
    center: bool = True
    resizable: bool = True
    decorations: bool = True
    always_on_top: bool = False
    devtools: bool = False
    allow_network: bool = True
    enable_plotly: bool = False
    enable_aggrid: bool = False
    plotly_theme: Literal[
        "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"
    ] = "plotly_dark"
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine"


class HtmlContent(BaseModel):
    """HTML content to display in a window."""

    html: str
    json_data: dict[str, Any] | None = None
    init_script: str | None = None
    css_files: list[Path | str] | None = None
    script_files: list[Path | str] | None = None
    inline_css: str | None = None
    watch: bool = False

    @field_validator("css_files", "script_files", mode="before")
    @classmethod
    def convert_paths(cls, v: Any) -> list[Path | str] | None:
        """Convert string paths to Path objects.

        Parameters
        ----------
        v : Any
            The value to convert.

        Returns
        -------
        list of Path or str, or None
            Converted path list or None.
        """
        if v is None:
            return None
        if isinstance(v, (str, Path)):
            return [Path(v) if isinstance(v, str) else v]
        return [Path(p) if isinstance(p, str) else p for p in v]


EVENT_NAMESPACE_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$")
RESERVED_NAMESPACES = frozenset({"pywry", "plotly", "grid"})


def validate_event_type(event_type: str) -> bool:
    """Validate event type matches namespace:event-name pattern or is wildcard.

    Parameters
    ----------
    event_type : str
        The event type string to validate.

    Returns
    -------
    bool
        True if valid, False otherwise.
    """
    if event_type == "*":
        return True
    return bool(EVENT_NAMESPACE_PATTERN.match(event_type))


class GenericEvent(BaseModel):
    """Generic event for custom event handling."""

    event_type: str
    data: Any = None
    window_label: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("event_type")
    @classmethod
    def validate_event_type_format(cls, v: str) -> str:
        """Validate event type matches namespace:event-name pattern.

        Parameters
        ----------
        v : str
            The event type string to validate.

        Returns
        -------
        str
            The validated event type.

        Raises
        ------
        ValueError
            If the event type is invalid.
        """
        if not validate_event_type(v):
            raise ValueError(
                f"Invalid event type '{v}'. Must match 'namespace:event-name' pattern "
                f"(lowercase, alphanumeric + hyphens) or '*' for wildcard."
            )
        return v


class ResultEvent(BaseModel):
    """Result sent from JavaScript via window.pywry.result()."""

    data: Any
    window_label: str


class PlotlyClickEvent(BaseModel):
    """Plotly click event data."""

    point_indices: list[int] = Field(default_factory=list)
    curve_number: int = 0
    point_data: dict[str, Any] = Field(default_factory=dict)
    window_label: str = ""


class PlotlySelectEvent(BaseModel):
    """Plotly selection event data."""

    points: list[dict[str, Any]] = Field(default_factory=list)
    range: dict[str, Any] | None = None
    window_label: str = ""


class PlotlyHoverEvent(BaseModel):
    """Plotly hover event data."""

    point_indices: list[int] = Field(default_factory=list)
    curve_number: int = 0
    point_data: dict[str, Any] = Field(default_factory=dict)
    window_label: str = ""


class PlotlyRelayoutEvent(BaseModel):
    """Plotly relayout event data (zoom, pan, etc.)."""

    relayout_data: dict[str, Any] = Field(default_factory=dict)
    window_label: str = ""


class GridSelectionEvent(BaseModel):
    """AG Grid selection event data."""

    selected_rows: list[dict[str, Any]] = Field(default_factory=list)
    selected_row_ids: list[str] = Field(default_factory=list)
    window_label: str = ""


class GridCellEvent(BaseModel):
    """AG Grid cell edit event data."""

    row_id: str = ""
    row_index: int = 0
    column: str = ""
    old_value: Any = None
    new_value: Any = None
    window_label: str = ""


class GridRowClickEvent(BaseModel):
    """AG Grid row click event data."""

    row_data: dict[str, Any] = Field(default_factory=dict)
    row_id: str = ""
    row_index: int = 0
    window_label: str = ""


class ResultPayload(BaseModel):
    """Payload for pywry_result command."""

    data: Any
    window_label: str


class GenericEventPayload(BaseModel):
    """Payload for pywry_event command."""

    event_type: str
    data: Any = None
    window_label: str

    @field_validator("event_type")
    @classmethod
    def validate_event_type_format(cls, v: str) -> str:
        """Validate event type matches namespace:event-name pattern.

        Parameters
        ----------
        v : str
            The event type string to validate.

        Returns
        -------
        str
            The validated event type.

        Raises
        ------
        ValueError
            If the event type is invalid.
        """
        if not validate_event_type(v):
            raise ValueError(
                f"Invalid event type '{v}'. Must match 'namespace:event-name' pattern."
            )
        return v


class FilePathPayload(BaseModel):
    """Payload for open_file command."""

    path: str


class WindowClosedPayload(BaseModel):
    """Payload for window closed notification."""

    window_label: str
