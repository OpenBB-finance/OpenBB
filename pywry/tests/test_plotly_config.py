"""Unit tests for Plotly configuration Pydantic models.

Tests cover:
- StandardButton enum values
- PlotlyIconName enum values
- SvgIcon model validation
- ModeBarButton model validation and JS config generation
- ModeBarConfig container
- PlotlyConfig top-level configuration
- Pre-built button classes
"""

from __future__ import annotations

import pytest

from pywry.plotly_config import (
    DownloadImageButton,
    ModeBarButton,
    ModeBarConfig,
    PlotlyConfig,
    PlotlyIconName,
    ResetAxesButton,
    StandardButton,
    SvgIcon,
    ToggleGridButton,
)


# =============================================================================
# StandardButton Enum Tests
# =============================================================================


class TestStandardButton:
    """Test StandardButton enum values."""

    def test_all_2d_buttons_exist(self) -> None:
        """Test that all 2D cartesian buttons are defined."""
        assert StandardButton.ZOOM_2D.value == "zoom2d"
        assert StandardButton.PAN_2D.value == "pan2d"
        assert StandardButton.SELECT_2D.value == "select2d"
        assert StandardButton.LASSO_2D.value == "lasso2d"
        assert StandardButton.ZOOM_IN_2D.value == "zoomIn2d"
        assert StandardButton.ZOOM_OUT_2D.value == "zoomOut2d"
        assert StandardButton.AUTO_SCALE_2D.value == "autoScale2d"
        assert StandardButton.RESET_SCALE_2D.value == "resetScale2d"

    def test_all_3d_buttons_exist(self) -> None:
        """Test that all 3D buttons are defined."""
        assert StandardButton.ZOOM_3D.value == "zoom3d"
        assert StandardButton.PAN_3D.value == "pan3d"
        assert StandardButton.ORBIT_ROTATION.value == "orbitRotation"
        assert StandardButton.TABLE_ROTATION.value == "tableRotation"
        assert StandardButton.RESET_CAMERA_DEFAULT_3D.value == "resetCameraDefault3d"

    def test_common_buttons_exist(self) -> None:
        """Test commonly used buttons."""
        assert StandardButton.TO_IMAGE.value == "toImage"
        assert StandardButton.TOGGLE_HOVER.value == "toggleHover"
        assert StandardButton.TOGGLE_SPIKELINES.value == "toggleSpikelines"
        assert StandardButton.RESET_VIEWS.value == "resetViews"

    def test_geo_buttons_exist(self) -> None:
        """Test geo/map buttons."""
        assert StandardButton.ZOOM_IN_GEO.value == "zoomInGeo"
        assert StandardButton.ZOOM_OUT_GEO.value == "zoomOutGeo"
        assert StandardButton.RESET_GEO.value == "resetGeo"
        assert StandardButton.HOVER_CLOSEST_GEO.value == "hoverClosestGeo"

    def test_enum_is_string(self) -> None:
        """Test that enum values are strings."""
        assert isinstance(StandardButton.ZOOM_2D.value, str)
        assert isinstance(StandardButton.TO_IMAGE.value, str)

    @pytest.mark.parametrize(
        "button",
        list(StandardButton),
    )
    def test_all_buttons_have_string_values(self, button: StandardButton) -> None:
        """Test that all buttons have non-empty string values."""
        assert isinstance(button.value, str)
        assert len(button.value) > 0


# =============================================================================
# PlotlyIconName Enum Tests
# =============================================================================


class TestPlotlyIconName:
    """Test PlotlyIconName enum values."""

    def test_common_icons_exist(self) -> None:
        """Test commonly used icons."""
        assert PlotlyIconName.HOME.value == "home"
        assert PlotlyIconName.ZOOM_PLUS.value == "zoom_plus"
        assert PlotlyIconName.ZOOM_MINUS.value == "zoom_minus"
        assert PlotlyIconName.PAN.value == "pan"
        assert PlotlyIconName.AUTOSCALE.value == "autoscale"

    def test_drawing_icons_exist(self) -> None:
        """Test drawing-related icons."""
        assert PlotlyIconName.PENCIL.value == "pencil"
        assert PlotlyIconName.ERASE_SHAPE.value == "eraseshape"
        assert PlotlyIconName.DRAW_LINE.value == "drawline"
        assert PlotlyIconName.DRAW_RECT.value == "drawrect"

    def test_selection_icons_exist(self) -> None:
        """Test selection icons."""
        assert PlotlyIconName.LASSO.value == "lasso"
        assert PlotlyIconName.SELECTBOX.value == "selectbox"
        assert PlotlyIconName.ZOOMBOX.value == "zoombox"

    @pytest.mark.parametrize(
        "icon",
        list(PlotlyIconName),
    )
    def test_all_icons_have_string_values(self, icon: PlotlyIconName) -> None:
        """Test that all icons have non-empty string values."""
        assert isinstance(icon.value, str)
        assert len(icon.value) > 0


# =============================================================================
# SvgIcon Model Tests
# =============================================================================


class TestSvgIcon:
    """Test SvgIcon Pydantic model."""

    def test_default_dimensions(self) -> None:
        """Test default width and height."""
        icon = SvgIcon()
        assert icon.width == 500
        assert icon.height == 500

    def test_custom_dimensions(self) -> None:
        """Test custom width and height."""
        icon = SvgIcon(width=100, height=200)
        assert icon.width == 100
        assert icon.height == 200

    def test_svg_path(self) -> None:
        """Test SVG path string."""
        path = "M0 0 L10 10 Z"
        icon = SvgIcon(path=path)
        assert icon.path == path

    def test_svg_markup(self) -> None:
        """Test full SVG markup."""
        svg = "<svg><path d='M0 0'/></svg>"
        icon = SvgIcon(svg=svg)
        assert icon.svg == svg

    def test_icon_name_reference(self) -> None:
        """Test referencing existing icon by name."""
        icon = SvgIcon(name=PlotlyIconName.HOME)
        assert icon.name == PlotlyIconName.HOME

    def test_icon_name_string(self) -> None:
        """Test referencing icon by string name."""
        icon = SvgIcon(name="custom_icon")
        assert icon.name == "custom_icon"

    def test_transform_attribute(self) -> None:
        """Test SVG transform attribute."""
        icon = SvgIcon(transform="rotate(45)")
        assert icon.transform == "rotate(45)"

    def test_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed."""
        icon = SvgIcon(custom_field="value")
        assert icon.model_extra.get("custom_field") == "value"


# =============================================================================
# ModeBarButton Model Tests
# =============================================================================


class TestModeBarButton:
    """Test ModeBarButton Pydantic model."""

    def test_minimal_button(self) -> None:
        """Test button with minimal required fields."""
        button = ModeBarButton(
            name="myButton",
            title="My Button",
            icon=PlotlyIconName.HOME,
        )
        assert button.name == "myButton"
        assert button.title == "My Button"
        assert button.icon == PlotlyIconName.HOME

    def test_button_with_click_handler(self) -> None:
        """Test button with JS click handler."""
        button = ModeBarButton(
            name="myButton",
            title="My Button",
            icon=PlotlyIconName.HOME,
            click="function(gd) { console.log('clicked'); }",
        )
        assert button.click is not None
        assert isinstance(button.click, str)
        # pylint: disable-next=unsupported-membership-test
        assert "console.log" in button.click

    def test_button_with_pywry_event(self) -> None:
        """Test button with PyWry event emission."""
        button = ModeBarButton(
            name="exportBtn",
            title="Export Data",
            icon=PlotlyIconName.DISK,  # Plotly uses 'disk' not 'save'
            event="plotly:modebar-export",
            data={"format": "csv"},
        )
        assert button.event == "plotly:modebar-export"
        assert button.data == {"format": "csv"}

    def test_button_with_toggle(self) -> None:
        """Test toggle button."""
        button = ModeBarButton(
            name="gridToggle",
            title="Toggle Grid",
            icon=PlotlyIconName.DRAW_LINE,
            toggle=True,
            attr="xaxis.showgrid",
            val=True,
        )
        assert button.toggle is True
        assert button.attr == "xaxis.showgrid"
        assert button.val is True

    def test_button_with_svg_icon(self) -> None:
        """Test button with custom SVG icon."""
        icon = SvgIcon(path="M0 0 L10 10 Z", width=100, height=100)
        button = ModeBarButton(
            name="custom",
            title="Custom",
            icon=icon,
        )
        assert isinstance(button.icon, SvgIcon)

    def test_button_with_dict_icon(self) -> None:
        """Test button with dict icon config gets converted to SvgIcon."""
        icon_dict = {"path": "M0 0", "width": 50}
        button = ModeBarButton(
            name="custom",
            title="Custom",
            icon=icon_dict,
        )
        # Dict is converted to SvgIcon
        assert isinstance(button.icon, SvgIcon)
        assert button.icon.path == "M0 0"
        assert button.icon.width == 50

    def test_to_js_config(self) -> None:
        """Test conversion to JS config dict."""
        button = ModeBarButton(
            name="myButton",
            title="My Button",
            icon=PlotlyIconName.HOME,
            toggle=True,
        )
        config = button.to_js_config()
        assert config["name"] == "myButton"
        assert config["title"] == "My Button"
        assert config["toggle"] is True

    def test_to_js_config_excludes_none(self) -> None:
        """Test that None values are excluded from JS config."""
        button = ModeBarButton(
            name="myButton",
            title="My Button",
            icon=PlotlyIconName.HOME,
        )
        config = button.to_js_config()
        assert "click" not in config
        assert "event" not in config
        assert "data" not in config


# =============================================================================
# ModeBarConfig Model Tests
# =============================================================================


class TestModeBarConfig:
    """Test ModeBarConfig Pydantic model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ModeBarConfig()
        assert config.orientation == "h"
        assert config.add_logo is True

    def test_buttons_to_remove(self) -> None:
        """Test removing buttons by enum."""
        config = ModeBarConfig(buttons_to_remove=[StandardButton.TO_IMAGE, StandardButton.LASSO_2D])
        assert config.buttons_to_remove is not None
        assert len(config.buttons_to_remove) == 2
        # pylint: disable-next=unsupported-membership-test
        assert StandardButton.TO_IMAGE in config.buttons_to_remove

    def test_buttons_to_remove_by_string(self) -> None:
        """Test removing buttons by string name."""
        config = ModeBarConfig(buttons_to_remove=["toImage", "lasso2d"])
        assert config.buttons_to_remove is not None
        # pylint: disable=unsupported-membership-test
        assert "toImage" in config.buttons_to_remove
        assert "lasso2d" in config.buttons_to_remove
        # pylint: enable=unsupported-membership-test

    def test_buttons_to_add(self) -> None:
        """Test adding custom buttons."""
        button = ModeBarButton(
            name="custom",
            title="Custom Action",
            icon=PlotlyIconName.QUESTION,
        )
        config = ModeBarConfig(buttons_to_add=[button])
        assert config.buttons_to_add is not None
        assert len(config.buttons_to_add) == 1
        # pylint: disable-next=unsubscriptable-object
        assert config.buttons_to_add[0].name == "custom"

    def test_buttons_to_add_as_dict(self) -> None:
        """Test adding buttons as dicts."""
        config = ModeBarConfig(
            buttons_to_add=[{"name": "custom", "title": "Custom", "icon": "home"}]
        )
        assert config.buttons_to_add is not None
        # pylint: disable-next=unsubscriptable-object
        assert len(config.buttons_to_add) == 1

    def test_custom_colors(self) -> None:
        """Test custom color configuration."""
        config = ModeBarConfig(
            bgcolor="#222222",
            color="#ffffff",
            active_color="#00ff00",
        )
        assert config.bgcolor == "#222222"
        assert config.color == "#ffffff"
        assert config.active_color == "#00ff00"

    def test_vertical_orientation(self) -> None:
        """Test vertical orientation."""
        config = ModeBarConfig(orientation="v")
        assert config.orientation == "v"


# =============================================================================
# PlotlyConfig Model Tests
# =============================================================================


class TestPlotlyConfig:
    """Test PlotlyConfig top-level model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = PlotlyConfig()
        assert config.static_plot is False
        assert config.responsive is True
        assert config.display_mode_bar == "hover"
        assert config.display_logo is False

    def test_static_plot(self) -> None:
        """Test static plot configuration."""
        config = PlotlyConfig(static_plot=True)
        assert config.static_plot is True

    def test_display_mode_bar_options(self) -> None:
        """Test display_mode_bar options."""
        config_hover = PlotlyConfig(display_mode_bar="hover")
        assert config_hover.display_mode_bar == "hover"

        config_always = PlotlyConfig(display_mode_bar=True)
        assert config_always.display_mode_bar is True

        config_never = PlotlyConfig(display_mode_bar=False)
        assert config_never.display_mode_bar is False

    def test_scroll_zoom_options(self) -> None:
        """Test scroll_zoom configuration."""
        config = PlotlyConfig(scroll_zoom=True)
        assert config.scroll_zoom is True

        config_cartesian = PlotlyConfig(scroll_zoom="cartesian")
        assert config_cartesian.scroll_zoom == "cartesian"

    def test_double_click_options(self) -> None:
        """Test double_click configuration."""
        config = PlotlyConfig(double_click="reset")
        assert config.double_click == "reset"

        config_autosize = PlotlyConfig(double_click="autosize")
        assert config_autosize.double_click == "autosize"

    def test_editable_mode(self) -> None:
        """Test editable chart configuration."""
        config = PlotlyConfig(editable=True)
        assert config.editable is True

    def test_buttons_to_remove(self) -> None:
        """Test removing buttons via top-level config."""
        config = PlotlyConfig(
            mode_bar_buttons_to_remove=[StandardButton.TO_IMAGE, StandardButton.LASSO_2D]
        )
        assert len(config.mode_bar_buttons_to_remove) == 2

    def test_buttons_to_add(self) -> None:
        """Test adding buttons via top-level config."""
        button = ModeBarButton(
            name="custom",
            title="Custom",
            icon=PlotlyIconName.QUESTION,
        )
        config = PlotlyConfig(mode_bar_buttons_to_add=[button])
        assert len(config.mode_bar_buttons_to_add) == 1

    def test_locale_settings(self) -> None:
        """Test locale configuration."""
        config = PlotlyConfig(locale="de")
        assert config.locale == "de"

    def test_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed for forward compatibility."""
        config = PlotlyConfig(future_option=True)
        assert config.model_extra.get("future_option") is True


# =============================================================================
# Pre-built Button Tests
# =============================================================================


class TestDownloadImageButton:
    """Test DownloadImageButton pre-built class."""

    def test_default_configuration(self) -> None:
        """Test default button configuration."""
        button = DownloadImageButton()
        assert button.name == "toImage"
        assert "Download" in button.title or "png" in button.title
        assert button.icon == PlotlyIconName.CAMERA_RETRO

    def test_custom_event(self) -> None:
        """Test button with custom event."""
        button = DownloadImageButton(event="plotly:modebar-download")
        assert button.event == "plotly:modebar-download"


class TestResetAxesButton:
    """Test ResetAxesButton pre-built class."""

    def test_default_configuration(self) -> None:
        """Test default button configuration."""
        button = ResetAxesButton()
        assert button.name == "resetViews"
        assert button.icon == PlotlyIconName.HOME


class TestToggleGridButton:
    """Test ToggleGridButton pre-built class."""

    def test_default_configuration(self) -> None:
        """Test default button configuration."""
        button = ToggleGridButton()
        assert button.name == "toggleGrid"
        assert button.toggle is True
        assert button.event == "plotly:toggle-grid"

    def test_custom_event(self) -> None:
        """Test button preserves custom kwargs passed to parent."""
        # Note: event is hardcoded in ToggleGridButton, test uses data instead
        button = ToggleGridButton(data={"custom_key": "value"})
        assert button.event == "plotly:toggle-grid"  # Always this value
        assert button.data == {"custom_key": "value"}


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Test model serialization for JS compatibility."""

    def test_camel_case_aliases(self) -> None:
        """Test that fields use camelCase when serialized."""
        config = PlotlyConfig(
            static_plot=True,
            display_mode_bar=True,
            scroll_zoom=True,
        )
        data = config.model_dump(by_alias=True)
        assert "staticPlot" in data
        assert "displayModeBar" in data
        assert "scrollZoom" in data

    def test_mode_bar_button_serialization(self) -> None:
        """Test ModeBarButton serialization."""
        button = ModeBarButton(
            name="test",
            title="Test Button",
            icon=PlotlyIconName.HOME,
            active_color="#ff0000",
        )
        data = button.model_dump(by_alias=True, exclude_none=True)
        assert data["name"] == "test"
        assert data["title"] == "Test Button"

    def test_nested_serialization(self) -> None:
        """Test nested model serialization."""
        icon = SvgIcon(path="M0 0", width=100, height=100)
        button = ModeBarButton(
            name="custom",
            title="Custom",
            icon=icon,
        )
        data = button.model_dump(by_alias=True)
        assert isinstance(data["icon"], dict)
        assert data["icon"]["width"] == 100
