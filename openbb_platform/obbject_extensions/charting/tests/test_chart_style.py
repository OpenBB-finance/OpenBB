"""Tests for ``openbb_charting.core.chart_style.ChartStyle``."""

import warnings
from pathlib import Path

import plotly.io as pio
import pytest

from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.core.config.openbb_styles import (
    PLT_COLORWAY,
    PLT_DECREASING_COLORWAY,
    PLT_INCREASING_COLORWAY,
)


@pytest.fixture
def style() -> ChartStyle:
    """Return the live ``ChartStyle`` singleton."""
    return ChartStyle()


@pytest.fixture
def restore_style(style):
    """Snapshot mutable singleton state and restore it after a test."""
    saved = {
        "plt_style": style.plt_style,
        "plotly_template": style.plotly_template,
        "mapbox_style": style.mapbox_style,
        "up_color": style.up_color,
        "down_color": style.down_color,
        "line_color": style.line_color,
        "up_colorway": style.up_colorway,
        "down_colorway": style.down_colorway,
        "default": pio.templates.default,
    }
    yield
    for attr in (
        "plt_style",
        "plotly_template",
        "mapbox_style",
        "up_color",
        "down_color",
        "line_color",
        "up_colorway",
        "down_colorway",
    ):
        setattr(style, attr, saved[attr])
    pio.templates.default = saved["default"]


class TestSingleton:
    """The class enforces a single shared instance."""

    def test_new_returns_same_instance(self):
        """Repeated construction returns the same object."""
        assert ChartStyle() is ChartStyle()

    def test_already_initialized_init_is_noop(self):
        """Re-initializing an initialized singleton leaves it intact."""
        style = ChartStyle()
        previous = style.plt_style
        ChartStyle("white")
        assert style.plt_style == previous
        assert style.initialized is True


class TestLoadStyles:
    """Loading available styles and individual style files."""

    def test_available_styles_loaded(self, style):
        """The default folder styles are discoverable."""
        assert "dark" in style.plt_styles_available
        assert "light" in style.plt_styles_available
        assert "tables" in style.plt_styles_available

    def test_load_available_styles_from_folder_missing(self, style):
        """A non-existent folder is ignored without raising."""
        before = dict(style.plt_styles_available)
        style.load_available_styles_from_folder(Path("/no/such/folder/xyz"))
        assert style.plt_styles_available == before

    def test_load_available_styles_from_folder_non_path(self, style):
        """A non-Path argument short-circuits and is ignored."""
        before = dict(style.plt_styles_available)
        style.load_available_styles_from_folder("not-a-path-object")  # type: ignore
        assert style.plt_styles_available == before

    def test_load_json_style(self, style):
        """Reading a known style file returns its dict contents."""
        loaded = style.load_json_style(style.plt_styles_available["dark"])
        assert isinstance(loaded, dict)
        assert "layout" in loaded

    def test_load_style_unknown_warns_and_falls_back(self, style, restore_style):
        """An unknown style name warns and falls back to ``dark``."""
        with pytest.warns(UserWarning, match="not found"):
            style.load_style("does-not-exist")
        assert style.plt_style == "dark"

    def test_load_style_default_uses_plt_style(self, style, restore_style):
        """Passing no style loads the currently set ``plt_style``."""
        style.plt_style = "dark"
        style.load_style("")
        assert style.plt_style == "dark"

    def test_load_plt_style_populates_colors(self, style, restore_style):
        """Loading a style populates the color attributes from the file."""
        style.load_plt_style("dark")
        assert style.up_color
        assert style.down_color
        assert style.line_color
        assert style.up_colorway
        assert style.down_colorway


class TestLoadPltStyleDefaults:
    """Color defaults fill in when a style file omits its ``line`` block."""

    def test_defaults_used_when_line_block_absent(self, style, restore_style, tmp_path):
        """A style file lacking a ``line`` block falls back to module defaults."""
        bare = tmp_path / "bare.pltstyle.json"
        bare.write_text('{"layout": {"colorway": ["#123456"]}}')
        style.plt_styles_available["bare"] = bare
        try:
            style.load_plt_style("bare")
            assert style.up_color == "#00ACFF"
            assert style.down_color == "#FF0000"
            assert style.line_color == "#ffed00"
            assert style.up_colorway == PLT_INCREASING_COLORWAY
            assert style.down_colorway == PLT_DECREASING_COLORWAY
        finally:
            style.plt_styles_available.pop("bare", None)


class TestApplyStyle:
    """Exercise the branches of ``apply_style``."""

    def test_apply_style_dark_sets_default(self, style, restore_style):
        """Applying the dark style sets the combined plotly+openbb default."""
        style.apply_style("dark")
        assert pio.templates.default == "plotly_dark+openbb"

    def test_apply_style_light_maps_to_white(self, style, restore_style):
        """Applying ``light`` maps to the plotly white template default."""
        style.apply_style("light")
        assert pio.templates.default == "plotly_white+openbb"

    def test_apply_style_reloads_when_style_differs(self, style, restore_style):
        """A style differing from ``plt_style`` triggers a reload."""
        style.plt_style = "dark"
        style.apply_style("light")
        assert style.plt_style == "light"

    def test_apply_style_custom_sets_openbb_default(self, style, restore_style):
        """A non dark/white style selects the bare ``openbb`` template."""
        style.plt_style = "dark"
        style.load_plt_style("dark")
        style.plt_style = "custom"
        style.apply_style("custom")
        assert pio.templates.default == "openbb"
        assert style.mapbox_style == "dark"

    def test_apply_style_value_error_non_legend2_is_swallowed(
        self, style, restore_style
    ):
        """A non-legend2 ValueError from the template is swallowed, not fatal."""
        style.plt_style = "dark"
        style.plotly_template = {"layout": {"not_a_real_property_xyz": 1}}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            style.apply_style("dark")
        assert pio.templates.default == "plotly_dark+openbb"

    def test_apply_style_noop_when_template_empty(self, style, restore_style):
        """An empty template skips template registration entirely."""
        style.plt_style = "dark"
        style.plotly_template = {}
        before = pio.templates.default
        style.apply_style("dark")
        assert pio.templates.default == before


class TestGetColors:
    """Exercise ``get_colors`` ordering."""

    def test_get_colors_returns_copy(self, style):
        """Colors are returned and mutation does not affect the template."""
        colors = style.get_colors()
        assert isinstance(colors, list)
        colors.append("x")
        assert "x" not in style.get_colors()

    def test_get_colors_reverse(self, style):
        """Reversing yields the colors in opposite order."""
        forward = style.get_colors()
        backward = style.get_colors(reverse=True)
        assert backward == forward[::-1]

    def test_get_colors_falls_back_to_default_colorway(self, style, restore_style):
        """A template lacking a colorway falls back to ``PLT_COLORWAY``."""
        style.plotly_template = {"layout": {}}
        assert style.get_colors() == PLT_COLORWAY
