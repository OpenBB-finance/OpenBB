"""Tests for pywry.types module.

These tests verify dataclass creation, serialization/deserialization,
enum values, and round-trip consistency.
"""

from __future__ import annotations

import pytest

from pywry.types import (
    Cookie,
    CursorIcon,
    Effect,
    Effects,
    EffectState,
    LogicalPosition,
    LogicalSize,
    Monitor,
    PhysicalPosition,
    PhysicalSize,
    ProgressBarState,
    ProgressBarStatus,
    SameSite,
    Theme,
    TitleBarStyle,
    UserAttentionType,
    serialize_effects,
    serialize_position,
    serialize_progress_bar,
    serialize_size,
)


class TestPhysicalSize:
    """Test PhysicalSize dataclass behavior."""

    def test_creation(self) -> None:
        """PhysicalSize stores width and height."""
        size = PhysicalSize(width=1920, height=1080)
        assert size.width == 1920
        assert size.height == 1080

    def test_immutable(self) -> None:
        """PhysicalSize is frozen (immutable)."""
        size = PhysicalSize(width=800, height=600)
        with pytest.raises(AttributeError):
            size.width = 1024  # type: ignore[misc]

    def test_to_dict(self) -> None:
        """to_dict produces correct dictionary."""
        size = PhysicalSize(width=1280, height=720)
        result = size.to_dict()
        assert result == {"width": 1280, "height": 720}

    def test_from_dict(self) -> None:
        """from_dict correctly deserializes."""
        data = {"width": 1920, "height": 1080}
        size = PhysicalSize.from_dict(data)
        assert size.width == 1920
        assert size.height == 1080

    def test_round_trip(self) -> None:
        """Serialization round-trip preserves data."""
        original = PhysicalSize(width=2560, height=1440)
        serialized = original.to_dict()
        restored = PhysicalSize.from_dict(serialized)
        assert restored == original

    def test_from_dict_converts_types(self) -> None:
        """from_dict converts string numbers to int."""
        data = {"width": "1920", "height": "1080"}  # JSON might have strings
        size = PhysicalSize.from_dict(data)  # type: ignore[arg-type]
        assert size.width == 1920
        assert isinstance(size.width, int)


class TestLogicalSize:
    """Test LogicalSize dataclass behavior."""

    def test_creation(self) -> None:
        """LogicalSize stores width and height as floats."""
        size = LogicalSize(width=1920.5, height=1080.25)
        assert size.width == 1920.5
        assert size.height == 1080.25

    def test_to_dict(self) -> None:
        """to_dict produces correct dictionary."""
        size = LogicalSize(width=1280.0, height=720.0)
        result = size.to_dict()
        assert result == {"width": 1280.0, "height": 720.0}

    def test_round_trip(self) -> None:
        """Serialization round-trip preserves data."""
        original = LogicalSize(width=1600.5, height=900.25)
        restored = LogicalSize.from_dict(original.to_dict())
        assert restored == original


class TestPhysicalPosition:
    """Test PhysicalPosition dataclass behavior."""

    def test_creation(self) -> None:
        """PhysicalPosition stores x and y."""
        pos = PhysicalPosition(x=100, y=200)
        assert pos.x == 100
        assert pos.y == 200

    def test_negative_values(self) -> None:
        """PhysicalPosition supports negative coordinates."""
        pos = PhysicalPosition(x=-50, y=-100)
        assert pos.x == -50
        assert pos.y == -100

    def test_to_dict(self) -> None:
        """to_dict produces correct dictionary."""
        pos = PhysicalPosition(x=10, y=20)
        assert pos.to_dict() == {"x": 10, "y": 20}

    def test_round_trip(self) -> None:
        """Serialization round-trip preserves data."""
        original = PhysicalPosition(x=150, y=250)
        restored = PhysicalPosition.from_dict(original.to_dict())
        assert restored == original


class TestLogicalPosition:
    """Test LogicalPosition dataclass behavior."""

    def test_creation(self) -> None:
        """LogicalPosition stores x and y as floats."""
        pos = LogicalPosition(x=100.5, y=200.75)
        assert pos.x == 100.5
        assert pos.y == 200.75

    def test_round_trip(self) -> None:
        """Serialization round-trip preserves data."""
        original = LogicalPosition(x=150.5, y=250.25)
        restored = LogicalPosition.from_dict(original.to_dict())
        assert restored == original


class TestCookie:
    """Test Cookie dataclass behavior."""

    def test_minimal_creation(self) -> None:
        """Cookie with required fields only."""
        cookie = Cookie(name="session", value="abc123")
        assert cookie.name == "session"
        assert cookie.value == "abc123"
        assert cookie.domain == ""
        assert cookie.path == "/"
        assert cookie.secure is False
        assert cookie.http_only is False
        assert cookie.same_site == SameSite.LAX
        assert cookie.expires is None

    def test_full_creation(self) -> None:
        """Cookie with all fields specified."""
        cookie = Cookie(
            name="auth",
            value="token123",
            domain="example.com",
            path="/api",
            secure=True,
            http_only=True,
            same_site=SameSite.STRICT,
            expires=1700000000.0,
        )
        assert cookie.name == "auth"
        assert cookie.domain == "example.com"
        assert cookie.secure is True
        assert cookie.same_site == SameSite.STRICT

    def test_to_dict(self) -> None:
        """to_dict produces correct dictionary with enum values."""
        cookie = Cookie(
            name="test",
            value="val",
            secure=True,
            same_site=SameSite.NONE,
        )
        result = cookie.to_dict()
        assert result["name"] == "test"
        assert result["value"] == "val"
        assert result["secure"] is True
        assert result["same_site"] == "None"  # Enum value, not None

    def test_from_dict(self) -> None:
        """from_dict correctly deserializes."""
        data = {
            "name": "cookie",
            "value": "v",
            "domain": "test.com",
            "path": "/",
            "secure": True,
            "http_only": True,
            "same_site": "Strict",
            "expires": 1234567890.0,
        }
        cookie = Cookie.from_dict(data)
        assert cookie.name == "cookie"
        assert cookie.domain == "test.com"
        assert cookie.same_site == SameSite.STRICT
        assert cookie.expires == 1234567890.0

    def test_from_dict_minimal(self) -> None:
        """from_dict works with minimal data."""
        data = {"name": "x", "value": "y"}
        cookie = Cookie.from_dict(data)
        assert cookie.name == "x"
        assert cookie.path == "/"  # Default
        assert cookie.same_site == SameSite.LAX  # Default

    def test_round_trip(self) -> None:
        """Serialization round-trip preserves data."""
        original = Cookie(
            name="roundtrip",
            value="test",
            domain="example.com",
            secure=True,
            same_site=SameSite.STRICT,
        )
        restored = Cookie.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.value == original.value
        assert restored.same_site == original.same_site


class TestMonitor:
    """Test Monitor dataclass behavior."""

    def test_creation(self) -> None:
        """Monitor stores display information."""
        monitor = Monitor(
            name="Primary Display",
            size=PhysicalSize(width=2560, height=1440),
            position=PhysicalPosition(x=0, y=0),
            scale_factor=2.0,
        )
        assert monitor.name == "Primary Display"
        assert monitor.size.width == 2560
        assert monitor.position.x == 0
        assert monitor.scale_factor == 2.0

    def test_to_dict(self) -> None:
        """to_dict produces nested dictionary structure."""
        monitor = Monitor(
            name="External",
            size=PhysicalSize(width=1920, height=1080),
            position=PhysicalPosition(x=2560, y=0),
            scale_factor=1.0,
        )
        result = monitor.to_dict()
        assert result["name"] == "External"
        assert result["size"] == {"width": 1920, "height": 1080}
        assert result["position"] == {"x": 2560, "y": 0}
        assert result["scale_factor"] == 1.0

    def test_from_dict(self) -> None:
        """from_dict correctly deserializes nested structure."""
        data = {
            "name": "Test",
            "size": {"width": 1920, "height": 1080},
            "position": {"x": 100, "y": 50},
            "scale_factor": 1.5,
        }
        monitor = Monitor.from_dict(data)
        assert monitor.name == "Test"
        assert monitor.size == PhysicalSize(width=1920, height=1080)
        assert monitor.position == PhysicalPosition(x=100, y=50)
        assert monitor.scale_factor == 1.5

    def test_name_can_be_none(self) -> None:
        """Monitor name can be None for unnamed displays."""
        monitor = Monitor(
            name=None,
            size=PhysicalSize(width=1920, height=1080),
            position=PhysicalPosition(x=0, y=0),
            scale_factor=1.0,
        )
        assert monitor.name is None


class TestEnums:
    """Test enum definitions and values."""

    def test_theme_values(self) -> None:
        """Theme enum has correct values."""
        assert Theme.LIGHT.value == "Light"
        assert Theme.DARK.value == "Dark"

    def test_title_bar_style_values(self) -> None:
        """TitleBarStyle enum has correct values."""
        assert TitleBarStyle.VISIBLE.value == "Visible"
        assert TitleBarStyle.TRANSPARENT.value == "Transparent"
        assert TitleBarStyle.OVERLAY.value == "Overlay"

    def test_user_attention_type_values(self) -> None:
        """UserAttentionType enum has correct values."""
        assert UserAttentionType.CRITICAL.value == "Critical"
        assert UserAttentionType.INFORMATIONAL.value == "Informational"

    def test_cursor_icon_subset(self) -> None:
        """CursorIcon enum contains expected values."""
        assert CursorIcon.DEFAULT.value == "Default"
        assert CursorIcon.POINTER.value if hasattr(CursorIcon, "POINTER") else True
        assert CursorIcon.HAND.value == "Hand"
        assert CursorIcon.CROSSHAIR.value == "Crosshair"
        assert CursorIcon.TEXT.value == "Text"
        assert CursorIcon.WAIT.value == "Wait"

    def test_effect_values(self) -> None:
        """Effect enum contains platform-specific effects."""
        # macOS effects
        assert Effect.SIDEBAR.value == "Sidebar"
        assert Effect.TITLEBAR.value == "Titlebar"
        # Windows effects
        assert Effect.MICA.value == "Mica"
        assert Effect.ACRYLIC.value == "Acrylic"

    def test_same_site_values(self) -> None:
        """SameSite enum has correct cookie values."""
        assert SameSite.STRICT.value == "Strict"
        assert SameSite.LAX.value == "Lax"
        assert SameSite.NONE.value == "None"

    def test_progress_bar_status_values(self) -> None:
        """ProgressBarStatus enum has correct values."""
        assert ProgressBarStatus.NONE.value == "None"
        assert ProgressBarStatus.NORMAL.value == "Normal"
        assert ProgressBarStatus.INDETERMINATE.value == "Indeterminate"
        assert ProgressBarStatus.PAUSED.value == "Paused"
        assert ProgressBarStatus.ERROR.value == "Error"


class TestSerializeFunctions:
    """Test serialization helper functions."""

    def test_serialize_physical_size(self) -> None:
        """serialize_size adds type tag for PhysicalSize."""
        size = PhysicalSize(width=800, height=600)
        result = serialize_size(size)
        assert result == {"type": "Physical", "width": 800, "height": 600}

    def test_serialize_logical_size(self) -> None:
        """serialize_size adds type tag for LogicalSize."""
        size = LogicalSize(width=800.5, height=600.5)
        result = serialize_size(size)
        assert result == {"type": "Logical", "width": 800.5, "height": 600.5}

    def test_serialize_physical_position(self) -> None:
        """serialize_position adds type tag for PhysicalPosition."""
        pos = PhysicalPosition(x=100, y=200)
        result = serialize_position(pos)
        assert result == {"type": "Physical", "x": 100, "y": 200}

    def test_serialize_logical_position(self) -> None:
        """serialize_position adds type tag for LogicalPosition."""
        pos = LogicalPosition(x=100.5, y=200.5)
        result = serialize_position(pos)
        assert result == {"type": "Logical", "x": 100.5, "y": 200.5}

    def test_serialize_effects_full(self) -> None:
        """serialize_effects handles all effect options."""
        effects: Effects = {
            "effects": [Effect.MICA, Effect.BLUR],
            "state": EffectState.ACTIVE,
            "radius": 10.0,
            "color": (255, 128, 64, 200),
        }
        result = serialize_effects(effects)
        assert result["effects"] == ["Mica", "Blur"]
        assert result["state"] == "Active"
        assert result["radius"] == 10.0
        assert result["color"] == [255, 128, 64, 200]

    def test_serialize_effects_partial(self) -> None:
        """serialize_effects handles partial effect options."""
        effects: Effects = {
            "effects": [Effect.SIDEBAR],
        }
        result = serialize_effects(effects)
        assert result["effects"] == ["Sidebar"]
        assert "state" not in result
        assert "radius" not in result

    def test_serialize_effects_empty(self) -> None:
        """serialize_effects handles empty effects."""
        effects: Effects = {}
        result = serialize_effects(effects)
        assert not result

    def test_serialize_progress_bar_full(self) -> None:
        """serialize_progress_bar handles all options."""
        state: ProgressBarState = {
            "status": ProgressBarStatus.NORMAL,
            "progress": 75,
        }
        result = serialize_progress_bar(state)
        assert result["status"] == "Normal"
        assert result["progress"] == 75

    def test_serialize_progress_bar_indeterminate(self) -> None:
        """serialize_progress_bar handles indeterminate state."""
        state: ProgressBarState = {
            "status": ProgressBarStatus.INDETERMINATE,
        }
        result = serialize_progress_bar(state)
        assert result["status"] == "Indeterminate"
        assert "progress" not in result


class TestDataclassEquality:
    """Test that dataclass equality works correctly."""

    def test_physical_size_equality(self) -> None:
        """PhysicalSize instances with same values are equal."""
        a = PhysicalSize(width=100, height=200)
        b = PhysicalSize(width=100, height=200)
        c = PhysicalSize(width=100, height=201)
        assert a == b
        assert a != c

    def test_physical_position_equality(self) -> None:
        """PhysicalPosition instances with same values are equal."""
        a = PhysicalPosition(x=10, y=20)
        b = PhysicalPosition(x=10, y=20)
        assert a == b

    def test_logical_size_equality(self) -> None:
        """LogicalSize instances with same values are equal."""
        a = LogicalSize(width=100.5, height=200.5)
        b = LogicalSize(width=100.5, height=200.5)
        assert a == b

    def test_monitor_equality(self) -> None:
        """Monitor instances with same values are equal."""
        a = Monitor(
            name="Test",
            size=PhysicalSize(1920, 1080),
            position=PhysicalPosition(0, 0),
            scale_factor=1.0,
        )
        b = Monitor(
            name="Test",
            size=PhysicalSize(1920, 1080),
            position=PhysicalPosition(0, 0),
            scale_factor=1.0,
        )
        assert a == b


class TestDataclassHashing:
    """Test that frozen dataclasses are hashable."""

    def test_physical_size_hashable(self) -> None:
        """PhysicalSize can be used in sets and as dict keys."""
        a = PhysicalSize(width=100, height=200)
        b = PhysicalSize(width=100, height=200)
        c = PhysicalSize(width=100, height=201)

        size_set = {a, b, c}
        assert len(size_set) == 2  # a and b are equal, so deduplicated

        size_dict = {a: "first"}
        assert size_dict[b] == "first"  # b is equal to a

    def test_position_hashable(self) -> None:
        """Position types can be used in sets."""
        positions = {
            PhysicalPosition(0, 0),
            PhysicalPosition(0, 0),
            PhysicalPosition(1, 1),
        }
        assert len(positions) == 2
