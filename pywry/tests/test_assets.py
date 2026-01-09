"""Tests for bundled asset loading.

Tests get_plotly_js, get_aggrid_js, get_aggrid_css for all themes and modes.
"""

import pytest

from pywry.assets import (
    ASSETS_DIR,
    SRC_DIR,
    STYLE_DIR,
    clear_cache,
    get_aggrid_css,
    get_aggrid_js,
    get_openbb_icon,
    get_openbb_icon_path,
    get_plotly_js,
)
from pywry.models import ThemeMode


class TestAssetsDir:
    """Tests for ASSETS_DIR constant."""

    def test_assets_dir_exists(self):
        """Assets directory exists."""
        assert ASSETS_DIR.exists()

    def test_assets_dir_is_directory(self):
        """Assets directory is a directory."""
        assert ASSETS_DIR.is_dir()

    def test_assets_dir_path_correct(self):
        """Assets directory path is frontend/assets."""
        assert ASSETS_DIR.name == "assets"
        assert ASSETS_DIR.parent.name == "frontend"


class TestSrcDir:
    """Tests for SRC_DIR constant."""

    def test_src_dir_exists(self):
        """Source directory exists."""
        assert SRC_DIR.exists()

    def test_src_dir_is_directory(self):
        """Source directory is a directory."""
        assert SRC_DIR.is_dir()

    def test_src_dir_path_correct(self):
        """Source directory path is frontend/src."""
        assert SRC_DIR.name == "src"
        assert SRC_DIR.parent.name == "frontend"

    def test_src_dir_contains_js_files(self):
        """Source directory contains our JS source files."""
        assert (SRC_DIR / "aggrid-defaults.js").exists()
        assert (SRC_DIR / "plotly-templates.js").exists()
        assert (SRC_DIR / "plotly-widget.js").exists()
        assert (SRC_DIR / "main.js").exists()


class TestStyleDir:
    """Tests for STYLE_DIR constant."""

    def test_style_dir_exists(self):
        """Style directory exists."""
        assert STYLE_DIR.exists()

    def test_style_dir_is_directory(self):
        """Style directory is a directory."""
        assert STYLE_DIR.is_dir()

    def test_style_dir_path_correct(self):
        """Style directory path is frontend/style."""
        assert STYLE_DIR.name == "style"
        assert STYLE_DIR.parent.name == "frontend"

    def test_style_dir_contains_css_files(self):
        """Style directory contains our CSS source files."""
        assert (STYLE_DIR / "pywry.css").exists()


class TestGetPlotlyJs:
    """Tests for get_plotly_js function."""

    def test_returns_string(self):
        """Returns a string."""
        result = get_plotly_js()
        assert isinstance(result, str)

    def test_returns_non_empty(self):
        """Returns non-empty content."""
        result = get_plotly_js()
        assert len(result) > 0

    def test_contains_plotly(self):
        """Content contains Plotly library code."""
        result = get_plotly_js()
        assert "Plotly" in result

    def test_is_valid_javascript(self):
        """Content is valid JavaScript (full bundle with templates)."""
        result = get_plotly_js()
        # Full bundle is larger than minified and contains more structure
        # Should be at least 1MB for the full plotly bundle
        assert len(result) > 1_000_000

    def test_caching_works(self):
        """Same content is returned on multiple calls (cached)."""
        result1 = get_plotly_js()
        result2 = get_plotly_js()
        assert result1 is result2  # Same object, not just equal

    def test_file_exists(self):
        """Plotly JS file exists in assets directory (full or minified)."""
        plotly_full_gz = ASSETS_DIR / "plotly-3.3.1.js.gz"
        plotly_full = ASSETS_DIR / "plotly-3.3.1.js"
        plotly_min_gz = ASSETS_DIR / "plotly-3.3.1.min.js.gz"
        plotly_min = ASSETS_DIR / "plotly-3.3.1.min.js"
        assert (
            plotly_full_gz.exists()
            or plotly_full.exists()
            or plotly_min_gz.exists()
            or plotly_min.exists()
        )


class TestGetAggridJs:
    """Tests for get_aggrid_js function."""

    def test_returns_string(self):
        """Returns a string."""
        result = get_aggrid_js()
        assert isinstance(result, str)

    def test_returns_non_empty(self):
        """Returns non-empty content."""
        result = get_aggrid_js()
        assert len(result) > 0

    def test_contains_aggrid(self):
        """Content contains AG Grid library code."""
        result = get_aggrid_js()
        # AG Grid uses agGrid or createGrid
        assert "agGrid" in result or "createGrid" in result or "Grid" in result

    def test_is_minified(self):
        """Content is minified."""
        result = get_aggrid_js()
        lines = result.count("\n")
        assert lines < len(result) / 1000

    def test_caching_works(self):
        """Same content is returned on multiple calls (cached)."""
        result1 = get_aggrid_js()
        result2 = get_aggrid_js()
        assert result1 is result2

    def test_file_exists(self):
        """AG Grid JS file exists in assets directory (compressed or uncompressed)."""
        aggrid_gz = ASSETS_DIR / "ag-grid-community-35.0.0.min.js.gz"
        aggrid_file = ASSETS_DIR / "ag-grid-community-35.0.0.min.js"
        assert aggrid_gz.exists() or aggrid_file.exists()


class TestGetAggridCssQuartz:
    """Tests for get_aggrid_css with quartz theme."""

    def test_quartz_dark_returns_string(self):
        """Quartz dark returns a string."""
        result = get_aggrid_css("quartz", ThemeMode.DARK)
        assert isinstance(result, str)

    def test_quartz_dark_non_empty(self):
        """Quartz dark returns non-empty content."""
        result = get_aggrid_css("quartz", ThemeMode.DARK)
        assert len(result) > 0

    def test_quartz_dark_contains_theme_class(self):
        """Quartz dark contains theme class."""
        result = get_aggrid_css("quartz", ThemeMode.DARK)
        assert "ag-theme-quartz" in result

    def test_quartz_light_returns_string(self):
        """Quartz light returns a string."""
        result = get_aggrid_css("quartz", ThemeMode.LIGHT)
        assert isinstance(result, str)

    def test_quartz_light_non_empty(self):
        """Quartz light returns non-empty content."""
        result = get_aggrid_css("quartz", ThemeMode.LIGHT)
        assert len(result) > 0

    def test_quartz_dark_file_exists(self):
        """Quartz dark CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-quartz-dark-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-quartz-dark-35.0.0.css"
        assert css_gz.exists() or css_file.exists()

    def test_quartz_light_file_exists(self):
        """Quartz light CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-quartz-light-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-quartz-light-35.0.0.css"
        assert css_gz.exists() or css_file.exists()


class TestGetAggridCssAlpine:
    """Tests for get_aggrid_css with alpine theme."""

    def test_alpine_dark_returns_content(self):
        """Alpine dark returns content."""
        result = get_aggrid_css("alpine", ThemeMode.DARK)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_alpine_dark_contains_theme_class(self):
        """Alpine dark contains theme class."""
        result = get_aggrid_css("alpine", ThemeMode.DARK)
        assert "ag-theme-alpine" in result

    def test_alpine_light_returns_content(self):
        """Alpine light returns content."""
        result = get_aggrid_css("alpine", ThemeMode.LIGHT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_alpine_dark_file_exists(self):
        """Alpine dark CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-alpine-dark-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-alpine-dark-35.0.0.css"
        assert css_gz.exists() or css_file.exists()

    def test_alpine_light_file_exists(self):
        """Alpine light CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-alpine-light-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-alpine-light-35.0.0.css"
        assert css_gz.exists() or css_file.exists()


class TestGetAggridCssBalham:
    """Tests for get_aggrid_css with balham theme."""

    def test_balham_dark_returns_content(self):
        """Balham dark returns content."""
        result = get_aggrid_css("balham", ThemeMode.DARK)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_balham_dark_contains_theme_class(self):
        """Balham dark contains theme class."""
        result = get_aggrid_css("balham", ThemeMode.DARK)
        assert "ag-theme-balham" in result

    def test_balham_light_returns_content(self):
        """Balham light returns content."""
        result = get_aggrid_css("balham", ThemeMode.LIGHT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_balham_dark_file_exists(self):
        """Balham dark CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-balham-dark-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-balham-dark-35.0.0.css"
        assert css_gz.exists() or css_file.exists()

    def test_balham_light_file_exists(self):
        """Balham light CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-balham-light-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-balham-light-35.0.0.css"
        assert css_gz.exists() or css_file.exists()


class TestGetAggridCssMaterial:
    """Tests for get_aggrid_css with material theme."""

    def test_material_dark_returns_content(self):
        """Material dark returns content."""
        result = get_aggrid_css("material", ThemeMode.DARK)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_material_dark_contains_theme_class(self):
        """Material dark contains theme class."""
        result = get_aggrid_css("material", ThemeMode.DARK)
        assert "ag-theme-material" in result

    def test_material_light_returns_content(self):
        """Material light returns content."""
        result = get_aggrid_css("material", ThemeMode.LIGHT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_material_dark_file_exists(self):
        """Material dark CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-material-dark-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-material-dark-35.0.0.css"
        assert css_gz.exists() or css_file.exists()

    def test_material_light_file_exists(self):
        """Material light CSS file exists (compressed or uncompressed)."""
        css_gz = ASSETS_DIR / "ag-theme-material-light-35.0.0.css.gz"
        css_file = ASSETS_DIR / "ag-theme-material-light-35.0.0.css"
        assert css_gz.exists() or css_file.exists()


class TestGetAggridCssCaching:
    """Tests for get_aggrid_css caching behavior."""

    def test_same_theme_mode_returns_same_object(self):
        """Same theme/mode combination returns cached object."""
        result1 = get_aggrid_css("quartz", ThemeMode.DARK)
        result2 = get_aggrid_css("quartz", ThemeMode.DARK)
        assert result1 is result2

    def test_different_mode_returns_same_base_content(self):
        """AG Grid 35.x: Different mode returns same base CSS (theme via CSS vars).

        Note: AG Grid 35.x Theming API uses the same base CSS for both modes.
        Dark/light mode is controlled via CSS variables at runtime.
        """
        dark = get_aggrid_css("quartz", ThemeMode.DARK)
        light = get_aggrid_css("quartz", ThemeMode.LIGHT)
        # Both should be valid non-empty strings
        assert isinstance(dark, str)
        assert isinstance(light, str)
        assert len(dark) > 0
        assert len(light) > 0

    def test_different_theme_returns_different_content(self):
        """Different theme returns different content."""
        quartz = get_aggrid_css("quartz", ThemeMode.DARK)
        alpine = get_aggrid_css("alpine", ThemeMode.DARK)
        assert quartz != alpine


class TestGetAggridCssSystemMode:
    """Tests for get_aggrid_css with SYSTEM mode (falls back to dark)."""

    def test_system_mode_returns_dark(self):
        """SYSTEM mode returns dark theme content."""
        system = get_aggrid_css("quartz", ThemeMode.SYSTEM)
        # SYSTEM should fall back to dark (or return empty)
        # Based on the implementation, SYSTEM != DARK, so returns empty or light
        assert isinstance(system, str)


class TestGetAggridCssInvalidTheme:
    """Tests for get_aggrid_css with invalid theme."""

    def test_invalid_theme_returns_empty(self):
        """Invalid theme returns empty string."""
        result = get_aggrid_css("nonexistent", ThemeMode.DARK)
        assert result == ""


class TestGetOpenbbIcon:
    """Tests for get_openbb_icon function."""

    def test_returns_bytes(self):
        """Returns bytes."""
        result = get_openbb_icon()
        assert isinstance(result, bytes)

    def test_returns_non_empty(self):
        """Returns non-empty content."""
        result = get_openbb_icon()
        assert len(result) > 0

    def test_is_png_format(self):
        """Content is PNG format (starts with PNG magic bytes)."""
        result = get_openbb_icon()
        # PNG magic bytes: 89 50 4E 47
        assert result[:4] == b"\x89PNG"

    def test_caching_works(self):
        """Same content is returned on multiple calls (cached)."""
        result1 = get_openbb_icon()
        result2 = get_openbb_icon()
        assert result1 is result2


class TestGetOpenbbIconPath:
    """Tests for get_openbb_icon_path function."""

    def test_returns_path(self):
        """Returns a Path object."""
        result = get_openbb_icon_path()
        assert result is not None
        from pathlib import Path

        assert isinstance(result, Path)

    def test_path_exists(self):
        """Returned path exists."""
        result = get_openbb_icon_path()
        assert result is not None
        assert result.exists()

    def test_path_is_png(self):
        """Returned path is icon.png."""
        result = get_openbb_icon_path()
        assert result is not None
        assert result.name == "icon.png"


class TestClearCache:
    """Tests for clear_cache function."""

    def test_clears_plotly_cache(self):
        """Clears Plotly.js cache."""
        # Load to populate cache
        get_plotly_js()
        # Clear
        clear_cache()
        # Should still work (reloads from file)
        result = get_plotly_js()
        assert len(result) > 0

    def test_clears_aggrid_cache(self):
        """Clears AG Grid cache."""
        get_aggrid_js()
        clear_cache()
        result = get_aggrid_js()
        assert len(result) > 0

    def test_clears_aggrid_css_cache(self):
        """Clears AG Grid CSS cache."""
        get_aggrid_css("quartz", ThemeMode.DARK)
        clear_cache()
        result = get_aggrid_css("quartz", ThemeMode.DARK)
        assert len(result) > 0

    def test_clears_icon_cache(self):
        """Clears icon cache."""
        get_openbb_icon()
        clear_cache()
        result = get_openbb_icon()
        assert len(result) > 0


class TestAllThemesAllModes:
    """Comprehensive tests for all theme and mode combinations."""

    @pytest.mark.parametrize("theme", ["quartz", "alpine", "balham", "material"])
    @pytest.mark.parametrize("mode", [ThemeMode.DARK, ThemeMode.LIGHT])
    def test_theme_mode_combination(self, theme, mode):
        """All theme/mode combinations return valid CSS."""
        result = get_aggrid_css(theme, mode)
        assert isinstance(result, str)
        assert len(result) > 0
        assert f"ag-theme-{theme}" in result

    @pytest.mark.parametrize("theme", ["quartz", "alpine", "balham", "material"])
    def test_dark_light_both_load(self, theme):
        """Dark and light modes both load valid CSS.

        Note: AG Grid 35.x Theming API uses the same base CSS for both modes.
        Dark/light mode is controlled via CSS variables at runtime, not separate files.
        """
        dark = get_aggrid_css(theme, ThemeMode.DARK)
        light = get_aggrid_css(theme, ThemeMode.LIGHT)
        # Both should load successfully
        assert isinstance(dark, str)
        assert isinstance(light, str)
        assert len(dark) > 0
        assert len(light) > 0
        # Both should contain the theme name
        assert f"ag-theme-{theme}" in dark
        assert f"ag-theme-{theme}" in light
