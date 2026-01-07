"""Tests for configuration classes.

Tests PyWrySettings, SecuritySettings, and other config classes.
"""

import pytest

from pywry.config import (
    AssetSettings,
    HotReloadSettings,
    PyWrySettings,
    SecuritySettings,
    ThemeSettings,
    WindowSettings,
)


class TestSecuritySettings:
    """Tests for SecuritySettings class."""

    def test_default_src_includes_self(self):
        """default-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.default_src

    def test_default_src_includes_unsafe_inline(self):
        """default-src includes 'unsafe-inline'."""
        settings = SecuritySettings()
        assert "'unsafe-inline'" in settings.default_src

    def test_default_src_includes_unsafe_eval(self):
        """default-src includes 'unsafe-eval'."""
        settings = SecuritySettings()
        assert "'unsafe-eval'" in settings.default_src

    def test_default_src_includes_data(self):
        """default-src includes data:."""
        settings = SecuritySettings()
        assert "data:" in settings.default_src

    def test_default_src_includes_blob(self):
        """default-src includes blob:."""
        settings = SecuritySettings()
        assert "blob:" in settings.default_src

    def test_script_src_includes_self(self):
        """script-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.script_src

    def test_script_src_includes_unsafe_inline(self):
        """script-src includes 'unsafe-inline'."""
        settings = SecuritySettings()
        assert "'unsafe-inline'" in settings.script_src

    def test_script_src_includes_unsafe_eval(self):
        """script-src includes 'unsafe-eval'."""
        settings = SecuritySettings()
        assert "'unsafe-eval'" in settings.script_src

    def test_style_src_includes_self(self):
        """style-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.style_src

    def test_style_src_includes_unsafe_inline(self):
        """style-src includes 'unsafe-inline'."""
        settings = SecuritySettings()
        assert "'unsafe-inline'" in settings.style_src

    def test_img_src_includes_self(self):
        """img-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.img_src

    def test_img_src_includes_data(self):
        """img-src includes data:."""
        settings = SecuritySettings()
        assert "data:" in settings.img_src

    def test_img_src_includes_blob(self):
        """img-src includes blob:."""
        settings = SecuritySettings()
        assert "blob:" in settings.img_src

    def test_font_src_includes_self(self):
        """font-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.font_src

    def test_font_src_includes_data(self):
        """font-src includes data:."""
        settings = SecuritySettings()
        assert "data:" in settings.font_src

    def test_connect_src_includes_self(self):
        """connect-src includes 'self'."""
        settings = SecuritySettings()
        assert "'self'" in settings.connect_src

    def test_connect_src_includes_http(self):
        """connect-src includes http wildcard."""
        settings = SecuritySettings()
        assert "http://*:*" in settings.connect_src

    def test_connect_src_includes_https(self):
        """connect-src includes https wildcard."""
        settings = SecuritySettings()
        assert "https://*:*" in settings.connect_src

    def test_connect_src_includes_ws(self):
        """connect-src includes ws wildcard."""
        settings = SecuritySettings()
        assert "ws://*:*" in settings.connect_src

    def test_connect_src_includes_wss(self):
        """connect-src includes wss wildcard."""
        settings = SecuritySettings()
        assert "wss://*:*" in settings.connect_src


class TestSecuritySettingsPermissive:
    """Tests for SecuritySettings.permissive() factory."""

    def test_permissive_allows_unsafe_eval(self):
        """permissive() allows unsafe-eval."""
        settings = SecuritySettings.permissive()
        assert "'unsafe-eval'" in settings.script_src
        assert "'unsafe-eval'" in settings.default_src

    def test_permissive_allows_unsafe_inline(self):
        """permissive() allows unsafe-inline."""
        settings = SecuritySettings.permissive()
        assert "'unsafe-inline'" in settings.script_src
        assert "'unsafe-inline'" in settings.style_src

    def test_permissive_allows_data(self):
        """permissive() allows data:."""
        settings = SecuritySettings.permissive()
        assert "data:" in settings.default_src

    def test_permissive_allows_blob(self):
        """permissive() allows blob:."""
        settings = SecuritySettings.permissive()
        assert "blob:" in settings.default_src


class TestSecuritySettingsStrict:
    """Tests for SecuritySettings.strict() factory."""

    def test_strict_has_self(self):
        """strict() has 'self' in default-src."""
        settings = SecuritySettings.strict()
        assert "'self'" in settings.default_src

    def test_strict_removes_unsafe_eval_from_default(self):
        """strict() removes unsafe-eval from default-src."""
        settings = SecuritySettings.strict()
        assert "'unsafe-eval'" not in settings.default_src


class TestSecuritySettingsLocalhost:
    """Tests for SecuritySettings.localhost() factory."""

    def test_localhost_allows_localhost(self):
        """localhost() allows localhost connections."""
        settings = SecuritySettings.localhost()
        # Should have localhost in connect-src
        connect = settings.connect_src
        assert "localhost" in connect or "127.0.0.1" in connect


class TestWindowSettings:
    """Tests for WindowSettings class."""

    def test_default_width(self):
        """Default width is 1280."""
        settings = WindowSettings()
        assert settings.width == 1280

    def test_default_height(self):
        """Default height is 720."""
        settings = WindowSettings()
        assert settings.height == 720

    def test_default_title(self):
        """Default title is PyWry."""
        settings = WindowSettings()
        assert settings.title == "PyWry"

    def test_default_resizable(self):
        """Default resizable is True."""
        settings = WindowSettings()
        assert settings.resizable is True

    def test_default_center(self):
        """Default center is True."""
        settings = WindowSettings()
        assert settings.center is True

    def test_custom_width(self):
        """Custom width is set."""
        settings = WindowSettings(width=800)
        assert settings.width == 800

    def test_custom_height(self):
        """Custom height is set."""
        settings = WindowSettings(height=600)
        assert settings.height == 600


class TestThemeSettings:
    """Tests for ThemeSettings class."""

    def test_default_css_file_is_none(self):
        """Default css_file is None."""
        settings = ThemeSettings()
        assert settings.css_file is None

    def test_custom_css_file(self):
        """Custom CSS file path can be set."""
        settings = ThemeSettings(css_file="/path/to/custom.css")
        assert settings.css_file == "/path/to/custom.css"


class TestHotReloadSettings:
    """Tests for HotReloadSettings class."""

    def test_default_enabled(self):
        """Default enabled is False."""
        settings = HotReloadSettings()
        assert settings.enabled is False

    def test_custom_enabled(self):
        """Custom enabled is set."""
        settings = HotReloadSettings(enabled=True)
        assert settings.enabled is True

    def test_default_debounce(self):
        """Default debounce_ms is reasonable."""
        settings = HotReloadSettings()
        assert settings.debounce_ms >= 0


class TestPyWrySettings:
    """Tests for PyWrySettings class."""

    def test_creates_default_settings(self):
        """Creates default settings."""
        settings = PyWrySettings()
        assert settings is not None

    def test_has_window_settings(self):
        """Has window settings."""
        settings = PyWrySettings()
        assert hasattr(settings, "window")
        assert isinstance(settings.window, WindowSettings)

    def test_has_theme_settings(self):
        """Has theme settings."""
        settings = PyWrySettings()
        assert hasattr(settings, "theme")
        assert isinstance(settings.theme, ThemeSettings)

    def test_has_csp_settings(self):
        """Has CSP settings."""
        settings = PyWrySettings()
        assert hasattr(settings, "csp")
        assert isinstance(settings.csp, SecuritySettings)

    def test_has_hot_reload_settings(self):
        """Has hot reload settings."""
        settings = PyWrySettings()
        assert hasattr(settings, "hot_reload")
        assert isinstance(settings.hot_reload, HotReloadSettings)

    def test_custom_window_settings(self):
        """Custom window settings work."""
        settings = PyWrySettings(window=WindowSettings(width=1024, height=768))
        assert settings.window.width == 1024
        assert settings.window.height == 768

    def test_custom_theme_css_file(self):
        """Custom theme settings with css_file work."""
        settings = PyWrySettings(theme=ThemeSettings(css_file="/path/to/custom.css"))
        assert settings.theme.css_file == "/path/to/custom.css"

    def test_custom_csp_settings(self):
        """Custom CSP settings work."""
        csp = SecuritySettings.strict()
        settings = PyWrySettings(csp=csp)
        assert "'unsafe-eval'" not in settings.csp.default_src

    def test_dict_window_settings(self):
        """Dict window settings work."""
        settings = PyWrySettings(window={"width": 800, "height": 600})
        assert settings.window.width == 800
        assert settings.window.height == 600

    def test_dict_theme_css_file(self):
        """Dict theme settings with css_file work."""
        settings = PyWrySettings(theme={"css_file": "/path/to/custom.css"})
        assert settings.theme.css_file == "/path/to/custom.css"


class TestPyWrySettingsValidation:
    """Tests for PyWrySettings validation."""

    def test_invalid_window_width_raises(self):
        """Invalid window width raises error."""
        with pytest.raises((TypeError, ValueError)):
            PyWrySettings(window={"width": "invalid"})


class TestAssetSettings:
    """Tests for AssetSettings class."""

    def test_default_plotly_version(self):
        """Default Plotly version is set."""
        settings = AssetSettings()
        assert settings.plotly_version == "3.3.1"

    def test_default_aggrid_version(self):
        """Default AG Grid version is set."""
        settings = AssetSettings()
        assert settings.aggrid_version == "35.0.0"

    def test_default_path_empty(self):
        """Default path is empty string."""
        settings = AssetSettings()
        assert settings.path == ""

    def test_default_css_files_empty(self):
        """Default css_files is empty list."""
        settings = AssetSettings()
        assert settings.css_files == []

    def test_default_script_files_empty(self):
        """Default script_files is empty list."""
        settings = AssetSettings()
        assert settings.script_files == []

    def test_custom_plotly_version(self):
        """Custom Plotly version can be set."""
        settings = AssetSettings(plotly_version="3.4.0")
        assert settings.plotly_version == "3.4.0"

    def test_custom_aggrid_version(self):
        """Custom AG Grid version can be set."""
        settings = AssetSettings(aggrid_version="36.0.0")
        assert settings.aggrid_version == "36.0.0"

    def test_custom_path(self):
        """Custom path can be set."""
        settings = AssetSettings(path="/custom/assets")
        assert settings.path == "/custom/assets"

    def test_custom_css_files_list(self):
        """Custom css_files list can be set."""
        settings = AssetSettings(css_files=["style.css", "theme.css"])
        assert settings.css_files == ["style.css", "theme.css"]

    def test_custom_script_files_list(self):
        """Custom script_files list can be set."""
        settings = AssetSettings(script_files=["app.js", "utils.js"])
        assert settings.script_files == ["app.js", "utils.js"]


class TestAssetSettingsCommaParsingCss:
    """Tests for AssetSettings.css_files comma-separated parsing."""

    def test_parses_comma_separated_css(self):
        """Parses comma-separated string to list."""
        settings = AssetSettings(css_files="style.css,theme.css")
        assert settings.css_files == ["style.css", "theme.css"]

    def test_trims_whitespace_css(self):
        """Trims whitespace around values."""
        settings = AssetSettings(css_files=" style.css , theme.css ")
        assert settings.css_files == ["style.css", "theme.css"]

    def test_handles_empty_string_css(self):
        """Empty string results in empty list."""
        settings = AssetSettings(css_files="")
        assert settings.css_files == []

    def test_ignores_empty_values_css(self):
        """Ignores empty values from multiple commas."""
        settings = AssetSettings(css_files="style.css,,theme.css")
        assert settings.css_files == ["style.css", "theme.css"]


class TestAssetSettingsCommaParsingScript:
    """Tests for AssetSettings.script_files comma-separated parsing."""

    def test_parses_comma_separated_script(self):
        """Parses comma-separated string to list."""
        settings = AssetSettings(script_files="app.js,utils.js")
        assert settings.script_files == ["app.js", "utils.js"]

    def test_trims_whitespace_script(self):
        """Trims whitespace around values."""
        settings = AssetSettings(script_files=" app.js , utils.js ")
        assert settings.script_files == ["app.js", "utils.js"]

    def test_handles_empty_string_script(self):
        """Empty string results in empty list."""
        settings = AssetSettings(script_files="")
        assert settings.script_files == []

    def test_ignores_empty_values_script(self):
        """Ignores empty values from multiple commas."""
        settings = AssetSettings(script_files="app.js,,utils.js")
        assert settings.script_files == ["app.js", "utils.js"]


class TestAssetSettingsNone:
    """Tests for AssetSettings with None values."""

    def test_none_css_files_becomes_empty_list(self):
        """None css_files becomes empty list."""
        settings = AssetSettings(css_files=None)
        assert settings.css_files == []

    def test_none_script_files_becomes_empty_list(self):
        """None script_files becomes empty list."""
        settings = AssetSettings(script_files=None)
        assert settings.script_files == []


class TestPyWrySettingsWithAsset:
    """Tests for PyWrySettings with AssetSettings."""

    def test_has_asset_settings(self):
        """Has asset settings."""
        settings = PyWrySettings()
        assert hasattr(settings, "asset")
        assert isinstance(settings.asset, AssetSettings)

    def test_custom_asset_settings(self):
        """Custom asset settings work."""
        settings = PyWrySettings(asset=AssetSettings(plotly_version="4.0.0"))
        assert settings.asset.plotly_version == "4.0.0"

    def test_dict_asset_settings(self):
        """Dict asset settings work."""
        settings = PyWrySettings(asset={"plotly_version": "4.0.0", "css_files": ["test.css"]})
        assert settings.asset.plotly_version == "4.0.0"
        assert settings.asset.css_files == ["test.css"]

    def test_asset_in_toml_export(self):
        """Asset settings are included in TOML export."""
        settings = PyWrySettings()
        toml = settings.to_toml()
        assert "[asset]" in toml
        assert "plotly_version" in toml
        assert "aggrid_version" in toml

    def test_asset_in_env_export(self):
        """Asset settings are included in env export."""
        settings = PyWrySettings()
        env = settings.to_env()
        assert "PYWRY_ASSET__PLOTLY_VERSION" in env
        assert "PYWRY_ASSET__AGGRID_VERSION" in env

    def test_asset_in_show_output(self):
        """Asset settings are included in show output."""
        settings = PyWrySettings()
        output = settings.show()
        assert "Assets" in output
        assert "plotly_version" in output
