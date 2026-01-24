"""PyTauri type definitions for WebviewWindow API.

These types mirror the pytauri.webview and pytauri.window types for use
in the WindowProxy IPC layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, TypedDict


if TYPE_CHECKING:
    from collections.abc import Sequence

# Color is RGBA tuple, each component 0-255
Color = tuple[int, int, int, int]


@dataclass(frozen=True)
class PhysicalSize:
    """Physical size in pixels."""

    width: int
    height: int

    def to_dict(self) -> dict[str, int]:
        """Serialize to dictionary for IPC."""
        return {"width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhysicalSize:
        """Deserialize from dictionary."""
        return cls(width=int(data["width"]), height=int(data["height"]))


@dataclass(frozen=True)
class LogicalSize:
    """Logical size (scaled by DPI factor)."""

    width: float
    height: float

    def to_dict(self) -> dict[str, float]:
        """Serialize to dictionary for IPC."""
        return {"width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogicalSize:
        """Deserialize from dictionary."""
        return cls(width=float(data["width"]), height=float(data["height"]))


@dataclass(frozen=True)
class PhysicalPosition:
    """Physical position in pixels."""

    x: int
    y: int

    def to_dict(self) -> dict[str, int]:
        """Serialize to dictionary for IPC."""
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhysicalPosition:
        """Deserialize from dictionary."""
        return cls(x=int(data["x"]), y=int(data["y"]))


@dataclass(frozen=True)
class LogicalPosition:
    """Logical position (scaled by DPI factor)."""

    x: float
    y: float

    def to_dict(self) -> dict[str, float]:
        """Serialize to dictionary for IPC."""
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogicalPosition:
        """Deserialize from dictionary."""
        return cls(x=float(data["x"]), y=float(data["y"]))


SizeType = PhysicalSize | LogicalSize
PositionType = PhysicalPosition | LogicalPosition


class Theme(Enum):
    """Window theme mode."""

    LIGHT = "Light"
    DARK = "Dark"


class TitleBarStyle(Enum):
    """Title bar style options."""

    VISIBLE = "Visible"
    TRANSPARENT = "Transparent"
    OVERLAY = "Overlay"


class UserAttentionType(Enum):
    """User attention request type."""

    CRITICAL = "Critical"
    INFORMATIONAL = "Informational"


class CursorIcon(Enum):
    """Cursor icon options."""

    DEFAULT = "Default"
    CROSSHAIR = "Crosshair"
    HAND = "Hand"
    ARROW = "Arrow"
    MOVE = "Move"
    TEXT = "Text"
    WAIT = "Wait"
    HELP = "Help"
    PROGRESS = "Progress"
    NOT_ALLOWED = "NotAllowed"
    CONTEXT_MENU = "ContextMenu"
    CELL = "Cell"
    VERTICAL_TEXT = "VerticalText"
    ALIAS = "Alias"
    COPY = "Copy"
    NO_DROP = "NoDrop"
    GRAB = "Grab"
    GRABBING = "Grabbing"
    ALL_SCROLL = "AllScroll"
    ZOOM_IN = "ZoomIn"
    ZOOM_OUT = "ZoomOut"
    E_RESIZE = "EResize"
    N_RESIZE = "NResize"
    NE_RESIZE = "NeResize"
    NW_RESIZE = "NwResize"
    S_RESIZE = "SResize"
    SE_RESIZE = "SeResize"
    SW_RESIZE = "SwResize"
    W_RESIZE = "WResize"
    EW_RESIZE = "EwResize"
    NS_RESIZE = "NsResize"
    NESW_RESIZE = "NeswResize"
    NWSE_RESIZE = "NwseResize"
    COL_RESIZE = "ColResize"
    ROW_RESIZE = "RowResize"


class Effect(Enum):
    """Visual effects for window background (platform-specific)."""

    # macOS vibrancy effects
    APPEARANCE_BASED = "AppearanceBased"
    LIGHT = "Light"
    DARK = "Dark"
    MEDIUM_LIGHT = "MediumLight"
    ULTRA_DARK = "UltraDark"
    TITLEBAR = "Titlebar"
    SELECTION = "Selection"
    MENU = "Menu"
    POPOVER = "Popover"
    SIDEBAR = "Sidebar"
    HEADER_VIEW = "HeaderView"
    SHEET = "Sheet"
    WINDOW_BACKGROUND = "WindowBackground"
    HUD_WINDOW = "HudWindow"
    FULL_SCREEN_UI = "FullScreenUI"
    TOOLTIP = "Tooltip"
    CONTENT_BACKGROUND = "ContentBackground"
    UNDER_WINDOW_BACKGROUND = "UnderWindowBackground"
    UNDER_PAGE_BACKGROUND = "UnderPageBackground"
    # Windows effects
    MICA = "Mica"
    MICA_DARK = "MicaDark"
    MICA_LIGHT = "MicaLight"
    TABBED = "Tabbed"
    TABBED_DARK = "TabbedDark"
    TABBED_LIGHT = "TabbedLight"
    BLUR = "Blur"
    ACRYLIC = "Acrylic"


class EffectState(Enum):
    """Effect state options."""

    FOLLOWS_WINDOW_ACTIVE_STATE = "FollowsWindowActiveState"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ProgressBarStatus(Enum):
    """Progress bar status options."""

    NONE = "None"
    NORMAL = "Normal"
    INDETERMINATE = "Indeterminate"
    PAUSED = "Paused"
    ERROR = "Error"


class SameSite(Enum):
    """Cookie SameSite attribute."""

    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"


class Effects(TypedDict, total=False):
    """Visual effects configuration."""

    effects: Sequence[Effect]
    state: EffectState
    radius: float
    color: Color


class ProgressBarState(TypedDict, total=False):
    """Progress bar state configuration."""

    status: ProgressBarStatus
    progress: int  # 0-100


@dataclass
class Cookie:
    """HTTP Cookie representation."""

    name: str
    value: str
    domain: str = ""
    path: str = "/"
    secure: bool = False
    http_only: bool = False
    same_site: SameSite = SameSite.LAX
    expires: float | None = None  # Unix timestamp

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for IPC."""
        return {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
            "path": self.path,
            "secure": self.secure,
            "http_only": self.http_only,
            "same_site": self.same_site.value,
            "expires": self.expires,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Cookie:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            value=data["value"],
            domain=data.get("domain", ""),
            path=data.get("path", "/"),
            secure=data.get("secure", False),
            http_only=data.get("http_only", False),
            same_site=SameSite(data.get("same_site", "Lax")),
            expires=data.get("expires"),
        )


@dataclass
class Monitor:
    """Display monitor information."""

    name: str | None
    size: PhysicalSize
    position: PhysicalPosition
    scale_factor: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for IPC."""
        return {
            "name": self.name,
            "size": self.size.to_dict(),
            "position": self.position.to_dict(),
            "scale_factor": self.scale_factor,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Monitor:
        """Deserialize from dictionary."""
        return cls(
            name=data.get("name"),
            size=PhysicalSize.from_dict(data["size"]),
            position=PhysicalPosition.from_dict(data["position"]),
            scale_factor=float(data["scale_factor"]),
        )


def serialize_size(size: SizeType) -> dict[str, Any]:
    """Serialize a size value for IPC."""
    if isinstance(size, PhysicalSize):
        return {"type": "Physical", **size.to_dict()}
    return {"type": "Logical", **size.to_dict()}


def serialize_position(position: PositionType) -> dict[str, Any]:
    """Serialize a position value for IPC."""
    if isinstance(position, PhysicalPosition):
        return {"type": "Physical", **position.to_dict()}
    return {"type": "Logical", **position.to_dict()}


def serialize_effects(effects: Effects) -> dict[str, Any]:
    """Serialize effects configuration for IPC."""
    result: dict[str, Any] = {}
    if "effects" in effects:
        result["effects"] = [e.value for e in effects["effects"]]
    if "state" in effects:
        result["state"] = effects["state"].value
    if "radius" in effects:
        result["radius"] = effects["radius"]
    if "color" in effects:
        result["color"] = list(effects["color"])
    return result


def serialize_progress_bar(state: ProgressBarState) -> dict[str, Any]:
    """Serialize progress bar state for IPC."""
    result: dict[str, Any] = {}
    if "status" in state:
        result["status"] = state["status"].value
    if "progress" in state:
        result["progress"] = state["progress"]
    return result
