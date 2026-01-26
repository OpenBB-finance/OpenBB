"""Tests for HTML template generation.

Tests build_html and related template functions.
"""

# pylint: disable=too-many-lines

import pytest

from pywry.config import AssetSettings, PyWrySettings, SecuritySettings, ThemeSettings
from pywry.models import HtmlContent, ThemeMode, WindowConfig
from pywry.templates import (
    build_aggrid_script,
    build_base_styles,
    build_csp_meta,
    build_global_css,
    build_global_scripts,
    build_html,
    build_json_data_script,
    build_plotly_script,
    build_theme_class,
    fix_aggrid_theme_classes,
    fix_plotly_template,
)
from pywry.toolbar import Toolbar


class TestFixAggridThemeClasses:
    """Tests for fix_aggrid_theme_classes - ensures AG Grid themes always match window theme."""

    def test_fixes_light_class_when_dark_mode(self):
        """Light AG Grid class is fixed to dark when window is dark."""
        html = '<div class="ag-theme-alpine"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.DARK)
        assert "ag-theme-alpine-dark" in result
        assert 'class="ag-theme-alpine"' not in result

    def test_keeps_dark_class_when_dark_mode(self):
        """Dark AG Grid class stays dark when window is dark."""
        html = '<div class="ag-theme-alpine-dark"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.DARK)
        assert "ag-theme-alpine-dark" in result

    def test_fixes_dark_class_when_light_mode(self):
        """Dark AG Grid class is fixed to light when window is light."""
        html = '<div class="ag-theme-quartz-dark"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.LIGHT)
        assert (
            'ag-theme-quartz"' in result
            or "ag-theme-quartz " in result
            or result.endswith("ag-theme-quartz")
        )
        assert "ag-theme-quartz-dark" not in result

    def test_keeps_light_class_when_light_mode(self):
        """Light AG Grid class stays light when window is light."""
        html = '<div class="ag-theme-balham"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.LIGHT)
        assert "ag-theme-balham" in result
        assert "ag-theme-balham-dark" not in result

    @pytest.mark.parametrize("theme_name", ["quartz", "alpine", "balham", "material"])
    def test_fixes_all_themes_to_dark(self, theme_name):
        """All AG Grid themes are fixed to dark when window is dark."""
        html = f'<div class="ag-theme-{theme_name}"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.DARK)
        assert f"ag-theme-{theme_name}-dark" in result

    @pytest.mark.parametrize("theme_name", ["quartz", "alpine", "balham", "material"])
    def test_fixes_all_themes_to_light(self, theme_name):
        """All AG Grid dark themes are fixed to light when window is light."""
        html = f'<div class="ag-theme-{theme_name}-dark"></div>'
        result = fix_aggrid_theme_classes(html, ThemeMode.LIGHT)
        assert f"ag-theme-{theme_name}" in result
        assert f"ag-theme-{theme_name}-dark" not in result


class TestFixPlotlyTemplate:
    """Tests for fix_plotly_template - ensures Plotly templates always match window theme."""

    def test_fixes_light_template_when_dark_mode(self):
        """Light Plotly template is fixed to dark when window is dark."""
        html = "template: 'plotly_white'"
        result = fix_plotly_template(html, ThemeMode.DARK)
        assert "plotly_dark" in result
        assert "plotly_white" not in result

    def test_keeps_dark_template_when_dark_mode(self):
        """Dark Plotly template stays dark when window is dark."""
        html = "template: 'plotly_dark'"
        result = fix_plotly_template(html, ThemeMode.DARK)
        assert "plotly_dark" in result

    def test_fixes_dark_template_when_light_mode(self):
        """Dark Plotly template is fixed to light when window is light."""
        html = 'template: "plotly_dark"'
        result = fix_plotly_template(html, ThemeMode.LIGHT)
        assert "plotly_white" in result
        assert "plotly_dark" not in result

    def test_keeps_light_template_when_light_mode(self):
        """Light Plotly template stays light when window is light."""
        html = "template: 'plotly_white'"
        result = fix_plotly_template(html, ThemeMode.LIGHT)
        assert "plotly_white" in result

    def test_fixes_plain_plotly_template_to_dark(self):
        """Plain 'plotly' template is fixed to dark when window is dark."""
        html = "template: 'plotly'"
        result = fix_plotly_template(html, ThemeMode.DARK)
        assert "plotly_dark" in result

    def test_fixes_plain_plotly_template_to_light(self):
        """Plain 'plotly' template is fixed to light when window is light."""
        html = "template: 'plotly'"
        result = fix_plotly_template(html, ThemeMode.LIGHT)
        assert "plotly_white" in result

    def test_handles_double_quotes(self):
        """Handles double-quoted template values."""
        html = 'template: "plotly_white"'
        result = fix_plotly_template(html, ThemeMode.DARK)
        assert "plotly_dark" in result

    def test_handles_single_quotes(self):
        """Handles single-quoted template values."""
        html = "template: 'plotly_dark'"
        result = fix_plotly_template(html, ThemeMode.LIGHT)
        assert "plotly_white" in result


class TestThemeCoordinationInBuildHtml:
    """Tests that build_html enforces theme coordination - NO mismatched themes allowed.

    Note: These tests don't enable AG Grid CSS loading because the theme fix
    happens on user HTML content BEFORE any assets are injected. We just need
    to verify the fix_aggrid_theme_classes and fix_plotly_template functions
    are called correctly by build_html.
    """

    def test_dark_window_fixes_light_aggrid_class(self):
        """Dark window automatically fixes light AG Grid class to dark."""
        # Don't enable_aggrid - we're testing the HTML fix, not CSS loading
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(html='<div class="ag-theme-alpine"></div>')
        html = build_html(content, config, window_label="main")
        # User HTML should be corrected to dark theme
        assert 'class="ag-theme-alpine-dark"' in html
        # Ensure NO light AG Grid class remains in user content
        assert 'class="ag-theme-alpine"' not in html

    def test_light_window_fixes_dark_aggrid_class(self):
        """Light window automatically fixes dark AG Grid class to light."""
        # Don't enable_aggrid - we're testing the HTML fix, not CSS loading
        config = WindowConfig(theme=ThemeMode.LIGHT)
        content = HtmlContent(html='<div class="ag-theme-quartz-dark"></div>')
        html = build_html(content, config, window_label="main")
        # User HTML should be corrected to light theme (no -dark suffix)
        assert 'class="ag-theme-quartz"' in html
        assert 'class="ag-theme-quartz-dark"' not in html

    def test_dark_window_fixes_light_plotly_template(self):
        """Dark window automatically fixes light Plotly template to dark."""
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(
            html="<script>Plotly.newPlot('div', data, {template: 'plotly_white'})</script>"
        )
        html = build_html(content, config, window_label="main")
        # Check user content in pywry-container only (THEME_MANAGER_JS contains both for runtime switching)
        container_start = html.find('class="pywry-container"')
        container_section = html[container_start : container_start + 500]
        assert "template: 'plotly_dark'" in container_section
        assert "template: 'plotly_white'" not in container_section

    def test_light_window_fixes_dark_plotly_template(self):
        """Light window automatically fixes dark Plotly template to light."""
        config = WindowConfig(theme=ThemeMode.LIGHT)
        content = HtmlContent(
            html="<script>Plotly.newPlot('div', data, {template: 'plotly_dark'})</script>"
        )
        html = build_html(content, config, window_label="main")
        # Check user content in pywry-container only (THEME_MANAGER_JS contains both for runtime switching)
        container_start = html.find('class="pywry-container"')
        container_section = html[container_start : container_start + 500]
        assert "template: 'plotly_white'" in container_section
        assert "template: 'plotly_dark'" not in container_section

    @pytest.mark.parametrize("aggrid_theme", ["quartz", "alpine", "balham", "material"])
    def test_dark_window_enforces_dark_aggrid_for_all_themes(self, aggrid_theme):
        """Dark window enforces dark mode for ALL AG Grid themes."""
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(html=f'<div class="ag-theme-{aggrid_theme}"></div>')
        html = build_html(content, config, window_label="main")
        assert f'class="ag-theme-{aggrid_theme}-dark"' in html

    @pytest.mark.parametrize("aggrid_theme", ["quartz", "alpine", "balham", "material"])
    def test_light_window_enforces_light_aggrid_for_all_themes(self, aggrid_theme):
        """Light window enforces light mode for ALL AG Grid themes."""
        config = WindowConfig(theme=ThemeMode.LIGHT)
        content = HtmlContent(html=f'<div class="ag-theme-{aggrid_theme}-dark"></div>')
        html = build_html(content, config, window_label="main")
        # Check that user content class was fixed (CSS may contain class selectors)
        assert f'class="ag-theme-{aggrid_theme}"' in html

    def test_dark_window_fixes_class_to_dark(self):
        """Dark window fixes AG Grid class to dark variant."""
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(html='<div class="ag-theme-quartz"></div>')
        html = build_html(content, config, window_label="main")
        assert "ag-theme-quartz-dark" in html

    def test_light_window_fixes_class_to_light(self):
        """Light window fixes AG Grid class to light variant."""
        config = WindowConfig(theme=ThemeMode.LIGHT)
        content = HtmlContent(html='<div class="ag-theme-quartz-dark"></div>')
        html = build_html(content, config, window_label="main")
        # Check that user content class was fixed (CSS may contain class selectors)
        assert 'class="ag-theme-quartz"' in html

    @pytest.mark.parametrize("aggrid_theme", ["quartz", "alpine", "balham", "material"])
    def test_dark_window_full_theme_coordination(self, aggrid_theme):
        """Dark window enforces dark class for all AG Grid themes."""
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(html=f'<div class="ag-theme-{aggrid_theme}"></div>')
        html = build_html(content, config, window_label="main")
        assert f"ag-theme-{aggrid_theme}-dark" in html
        assert f'class="ag-theme-{aggrid_theme}"' not in html


class TestBuildHtml:
    """Tests for build_html function."""

    def test_creates_doctype(self):
        """Creates HTML5 doctype."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "<!DOCTYPE html>" in html

    def test_creates_html_tag(self):
        """Creates html tag."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "<html" in html
        assert "</html>" in html

    def test_creates_head_tag(self):
        """Creates head tag."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "<head>" in html
        assert "</head>" in html

    def test_creates_body_tag(self):
        """Creates body tag."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "<body>" in html
        assert "</body>" in html

    def test_includes_title(self):
        """Includes title from config."""
        config = WindowConfig(title="Test Title")
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "<title>Test Title</title>" in html

    def test_includes_content(self):
        """Includes HTML content."""
        config = WindowConfig()
        content = HtmlContent(html="<p>Hello World</p>")
        html = build_html(content, config, window_label="main")
        assert "<p>Hello World</p>" in html

    def test_includes_init_script(self):
        """Includes init script when provided."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>", init_script="console.log('test');")
        html = build_html(content, config, window_label="main")
        assert "console.log('test');" in html

    def test_includes_inline_css(self):
        """Includes inline CSS when provided."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>", inline_css="body { margin: 0; }")
        html = build_html(content, config, window_label="main")
        assert "body { margin: 0; }" in html

    def test_includes_json_data(self):
        """Includes JSON data when provided."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>", json_data={"key": "value"})
        html = build_html(content, config, window_label="main")
        assert "key" in html
        assert "value" in html


class TestBuildHtmlWithTheme:
    """Tests for build_html with theme settings."""

    def test_dark_theme_class(self):
        """Dark theme adds appropriate class or attribute."""
        config = WindowConfig(theme=ThemeMode.DARK)
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        # Should have dark theme indicator somewhere
        assert "dark" in html.lower() or ThemeMode.DARK.value in html

    def test_light_theme_class(self):
        """Light theme adds appropriate class or attribute."""
        config = WindowConfig(theme=ThemeMode.LIGHT)
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        # Should have light theme indicator somewhere
        assert "light" in html.lower() or ThemeMode.LIGHT.value in html


class TestBuildHtmlWithPlotly:
    """Tests for build_html with Plotly enabled."""

    def test_includes_plotly_when_enabled(self):
        """Includes Plotly script when enabled."""
        config = WindowConfig(enable_plotly=True)
        content = HtmlContent(html="<div id='chart'></div>")
        html = build_html(content, config, window_label="main")
        assert "Plotly" in html

    def test_excludes_plotly_library_when_disabled(self):
        """Excludes Plotly library script when disabled."""
        config = WindowConfig(enable_plotly=False)
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        # Check the Plotly library specifically is not included
        # The bridge script mentions "Plotly" but actual library loads window.Plotly.version
        plotly_lib_present = "Plotly.version" in html or "plotly-3.3.1.min.js" in html
        assert not plotly_lib_present


class TestBuildHtmlWithAGGrid:
    """Tests for build_html with AG Grid enabled."""

    def test_includes_aggrid_when_enabled(self):
        """Includes AG Grid when enabled."""
        config = WindowConfig(enable_aggrid=True)
        content = HtmlContent(html="<div id='grid'></div>")
        html = build_html(content, config, window_label="main")
        assert "ag-" in html.lower() or "agGrid" in html


class TestBuildCspMeta:
    """Tests for build_csp_meta function."""

    def test_creates_meta_tag(self):
        """Creates CSP meta tag."""
        meta = build_csp_meta(SecuritySettings())
        assert '<meta http-equiv="Content-Security-Policy"' in meta

    def test_includes_default_src(self):
        """Includes default-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "default-src" in meta

    def test_includes_script_src(self):
        """Includes script-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "script-src" in meta

    def test_includes_style_src(self):
        """Includes style-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "style-src" in meta


class TestBuildPlotlyScript:
    """Tests for build_plotly_script function."""

    def test_returns_script_when_enabled(self):
        """Returns script tag when Plotly enabled."""
        config = WindowConfig(enable_plotly=True)
        script = build_plotly_script(config)
        assert script.startswith("<script>")
        assert script.endswith("</script>")

    def test_returns_empty_when_disabled(self):
        """Returns empty string when Plotly disabled."""
        config = WindowConfig(enable_plotly=False)
        script = build_plotly_script(config)
        assert script == ""

    def test_contains_plotly_code(self):
        """Contains Plotly library code."""
        config = WindowConfig(enable_plotly=True)
        script = build_plotly_script(config)
        assert "Plotly" in script


class TestBuildJsonDataScript:
    """Tests for build_json_data_script function."""

    def test_creates_script_tag(self):
        """Creates script tag when data provided."""
        script = build_json_data_script({"test": 1})
        assert "<script>" in script
        assert "</script>" in script

    def test_assigns_to_json_data_variable(self):
        """Assigns data to window.json_data variable."""
        script = build_json_data_script({"test": 1})
        assert "json_data" in script

    def test_serializes_dict(self):
        """Serializes dictionary to JSON."""
        script = build_json_data_script({"name": "test", "value": 42})
        assert "name" in script
        assert "test" in script
        assert "42" in script

    def test_returns_empty_for_none(self):
        """Returns empty string for None."""
        script = build_json_data_script(None)
        assert script == ""

    def test_handles_nested_data(self):
        """Handles nested data structures."""
        data = {"outer": {"inner": [1, 2, 3], "value": "test"}}
        script = build_json_data_script(data)
        assert "outer" in script
        assert "inner" in script


class TestBuildHtmlWithSettings:
    """Tests for build_html with PyWrySettings."""

    def test_uses_settings_csp(self):
        """Uses CSP from settings."""
        settings = PyWrySettings()
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        assert "Content-Security-Policy" in html

    def test_permissive_csp_includes_unsafe_eval(self):
        """Permissive CSP includes unsafe-eval."""
        settings = PyWrySettings(csp=SecuritySettings.permissive())
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        assert "'unsafe-eval'" in html


class TestBuildHtmlWithWindowLabel:
    """Tests for build_html with window label."""

    def test_includes_window_label(self):
        """Includes window label for event routing."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main-window")
        # Window label should be available somewhere (data attribute or JS var)
        assert "main-window" in html


class TestBuildHtmlStructure:
    """Tests for overall HTML structure."""

    def test_head_before_body(self):
        """Head comes before body."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        head_pos = html.find("<head>")
        body_pos = html.find("<body>")
        assert head_pos < body_pos

    def test_meta_charset(self):
        """Includes UTF-8 charset."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert 'charset="UTF-8"' in html or "charset=UTF-8" in html

    def test_viewport_meta(self):
        """Includes viewport meta tag."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main")
        assert "viewport" in html


class TestBuildThemeClass:
    """Tests for build_theme_class function."""

    def test_dark_returns_dark(self):
        """Dark theme returns 'pywry-theme-dark' class."""
        result = build_theme_class(ThemeMode.DARK)
        assert result == "pywry-theme-dark"

    def test_light_returns_light(self):
        """Light theme returns 'pywry-theme-light' class."""
        result = build_theme_class(ThemeMode.LIGHT)
        assert result == "pywry-theme-light"

    def test_system_returns_dark(self):
        """System theme defaults to 'pywry-theme-dark' class."""
        result = build_theme_class(ThemeMode.SYSTEM)
        assert result == "pywry-theme-dark"


class TestBuildBaseStyles:
    """Tests for build_base_styles function."""

    def test_returns_style_tag(self):
        """Returns style tag."""
        result = build_base_styles()
        assert "<style>" in result
        assert "</style>" in result

    def test_includes_css_variables(self):
        """Includes CSS variables from pywry.css."""
        result = build_base_styles()
        assert "--pywry-bg" in result
        assert "--pywry-text" in result

    def test_includes_font_family(self):
        """Includes font family from pywry.css."""
        result = build_base_styles()
        assert "font-family" in result


class TestBuildAggridScript:
    """Tests for build_aggrid_script function."""

    def test_returns_empty_when_disabled(self):
        """Returns empty string when AG Grid disabled."""
        config = WindowConfig(enable_aggrid=False)
        result = build_aggrid_script(config)
        assert result == ""

    def test_returns_content_when_enabled(self):
        """Returns content when AG Grid enabled."""
        config = WindowConfig(enable_aggrid=True)
        result = build_aggrid_script(config)
        assert len(result) > 0

    def test_includes_style_tag(self):
        """Includes style tag for CSS."""
        config = WindowConfig(enable_aggrid=True)
        result = build_aggrid_script(config)
        assert "<style>" in result

    def test_includes_script_tag(self):
        """Includes script tag for JS."""
        config = WindowConfig(enable_aggrid=True)
        result = build_aggrid_script(config)
        assert "<script>" in result

    def test_uses_quartz_theme_by_default(self):
        """Uses quartz theme by default."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme="quartz")
        result = build_aggrid_script(config)
        assert "ag-theme-quartz" in result

    def test_uses_alpine_theme(self):
        """Uses alpine theme when specified."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme="alpine")
        result = build_aggrid_script(config)
        assert "ag-theme-alpine" in result

    def test_uses_balham_theme(self):
        """Uses balham theme when specified."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme="balham")
        result = build_aggrid_script(config)
        assert "ag-theme-balham" in result

    def test_uses_material_theme(self):
        """Uses material theme when specified."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme="material")
        result = build_aggrid_script(config)
        assert "ag-theme-material" in result

    def test_dark_mode_uses_dark_css(self):
        """Dark mode uses dark theme CSS."""
        config = WindowConfig(enable_aggrid=True, theme=ThemeMode.DARK)
        result = build_aggrid_script(config)
        # The CSS content should be loaded from dark variant
        assert len(result) > 0

    def test_light_mode_uses_light_css(self):
        """Light mode uses light theme CSS."""
        config = WindowConfig(enable_aggrid=True, theme=ThemeMode.LIGHT)
        result = build_aggrid_script(config)
        assert len(result) > 0


class TestBuildAggridScriptAllThemes:
    """Tests for build_aggrid_script with all theme combinations."""

    @pytest.mark.parametrize("theme", ["quartz", "alpine", "balham", "material"])
    def test_theme_produces_output(self, theme):
        """Each theme produces output."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme=theme)
        result = build_aggrid_script(config)
        assert len(result) > 0
        assert f"ag-theme-{theme}" in result

    @pytest.mark.parametrize("theme", ["quartz", "alpine", "balham", "material"])
    def test_theme_with_dark_mode(self, theme):
        """Each theme works with dark mode."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme=theme, theme=ThemeMode.DARK)
        result = build_aggrid_script(config)
        assert len(result) > 0

    @pytest.mark.parametrize("theme", ["quartz", "alpine", "balham", "material"])
    def test_theme_with_light_mode(self, theme):
        """Each theme works with light mode."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme=theme, theme=ThemeMode.LIGHT)
        result = build_aggrid_script(config)
        assert len(result) > 0


class TestBuildGlobalCss:
    """Tests for build_global_css function."""

    def test_returns_empty_when_no_settings(self):
        """Returns empty string when settings is None."""
        result = build_global_css(None)
        assert result == ""

    def test_returns_empty_when_no_css_files(self):
        """Returns empty string when css_files is empty."""
        settings = AssetSettings()
        result = build_global_css(settings)
        assert result == ""

    def test_loads_css_file(self, tmp_path):
        """Loads CSS file from path."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        settings = AssetSettings(path=str(tmp_path), css_files=["test.css"])
        result = build_global_css(settings)
        assert "body { color: red; }" in result

    def test_wraps_in_style_tag(self, tmp_path):
        """Wraps CSS in style tag."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { margin: 0; }")
        settings = AssetSettings(path=str(tmp_path), css_files=["test.css"])
        result = build_global_css(settings)
        assert "<style" in result
        assert "</style>" in result

    def test_loads_multiple_css_files(self, tmp_path):
        """Loads multiple CSS files."""
        (tmp_path / "a.css").write_text("a { color: red; }")
        (tmp_path / "b.css").write_text("b { color: blue; }")
        settings = AssetSettings(path=str(tmp_path), css_files=["a.css", "b.css"])
        result = build_global_css(settings)
        assert "a { color: red; }" in result
        assert "b { color: blue; }" in result


class TestBuildGlobalScripts:
    """Tests for build_global_scripts function."""

    def test_returns_empty_when_no_settings(self):
        """Returns empty string when settings is None."""
        result = build_global_scripts(None)
        assert result == ""

    def test_returns_empty_when_no_script_files(self):
        """Returns empty string when script_files is empty."""
        settings = AssetSettings()
        result = build_global_scripts(settings)
        assert result == ""

    def test_loads_script_file(self, tmp_path):
        """Loads script file from path."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        settings = AssetSettings(path=str(tmp_path), script_files=["test.js"])
        result = build_global_scripts(settings)
        assert "console.log('hello');" in result

    def test_wraps_in_script_tag(self, tmp_path):
        """Wraps JS in script tag."""
        js_file = tmp_path / "test.js"
        js_file.write_text("let x = 1;")
        settings = AssetSettings(path=str(tmp_path), script_files=["test.js"])
        result = build_global_scripts(settings)
        assert "<script>" in result
        assert "</script>" in result

    def test_loads_multiple_script_files(self, tmp_path):
        """Loads multiple script files."""
        (tmp_path / "a.js").write_text("let a = 1;")
        (tmp_path / "b.js").write_text("let b = 2;")
        settings = AssetSettings(path=str(tmp_path), script_files=["a.js", "b.js"])
        result = build_global_scripts(settings)
        assert "let a = 1;" in result
        assert "let b = 2;" in result


class TestBuildHtmlWithGlobalAssets:
    """Tests for build_html with global CSS/JS from AssetSettings."""

    def test_includes_global_css(self, tmp_path):
        """Includes global CSS from AssetSettings."""
        css_file = tmp_path / "global.css"
        css_file.write_text(".global { color: green; }")
        settings = PyWrySettings(asset=AssetSettings(path=str(tmp_path), css_files=["global.css"]))
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        assert ".global { color: green; }" in html

    def test_includes_global_scripts(self, tmp_path):
        """Includes global scripts from AssetSettings."""
        js_file = tmp_path / "global.js"
        js_file.write_text("window.globalVar = 42;")
        settings = PyWrySettings(
            asset=AssetSettings(path=str(tmp_path), script_files=["global.js"])
        )
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        assert "window.globalVar = 42;" in html

    def test_global_css_before_custom_css(self, tmp_path):
        """Global CSS appears before custom CSS."""
        (tmp_path / "global.css").write_text("/* global */")
        (tmp_path / "custom.css").write_text("/* custom */")
        settings = PyWrySettings(asset=AssetSettings(path=str(tmp_path), css_files=["global.css"]))
        config = WindowConfig()
        content = HtmlContent(
            html="<div></div>",
            css_files=[str(tmp_path / "custom.css")],
        )
        html = build_html(content, config, window_label="main", settings=settings)
        global_pos = html.find("/* global */")
        custom_pos = html.find("/* custom */")
        assert global_pos < custom_pos


class TestBuildHtmlWithThemeSettings:
    """Tests for build_html with ThemeSettings custom CSS file."""

    def test_base_styles_included_without_custom_css(self):
        """Base pywry.css styles are included when no custom CSS file."""
        settings = PyWrySettings(theme=ThemeSettings())
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        # Base styling from pywry.css is included
        assert "--pywry-font-family" in html

    def test_custom_css_file_included(self, tmp_path):
        """Custom CSS file is loaded and included when specified."""
        # Create a temporary CSS file
        css_file = tmp_path / "custom.css"
        css_file.write_text(":root { --custom-var: red; }")

        settings = PyWrySettings(theme=ThemeSettings(css_file=str(css_file)))
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        html = build_html(content, config, window_label="main", settings=settings)
        # Both base and custom CSS should be included
        assert "--pywry-font-family" in html
        assert "--custom-var: red" in html


class TestBuildHtmlWithPlotlyTheme:
    """Tests for build_html with Plotly and themes."""

    def test_plotly_with_dark_theme(self):
        """Plotly works with dark theme."""
        config = WindowConfig(enable_plotly=True, theme=ThemeMode.DARK)
        content = HtmlContent(html="<div id='chart'></div>")
        html = build_html(content, config, window_label="main")
        assert "Plotly" in html

    def test_plotly_with_light_theme(self):
        """Plotly works with light theme."""
        config = WindowConfig(enable_plotly=True, theme=ThemeMode.LIGHT)
        content = HtmlContent(html="<div id='chart'></div>")
        html = build_html(content, config, window_label="main")
        assert "Plotly" in html


class TestBuildHtmlWithAggridTheme:
    """Tests for build_html with AG Grid and themes."""

    def test_aggrid_with_dark_theme(self):
        """AG Grid works with dark theme."""
        config = WindowConfig(enable_aggrid=True, theme=ThemeMode.DARK)
        content = HtmlContent(html="<div id='grid'></div>")
        html = build_html(content, config, window_label="main")
        assert "ag-" in html.lower() or "agGrid" in html

    def test_aggrid_with_light_theme(self):
        """AG Grid works with light theme."""
        config = WindowConfig(enable_aggrid=True, theme=ThemeMode.LIGHT)
        content = HtmlContent(html="<div id='grid'></div>")
        html = build_html(content, config, window_label="main")
        assert "ag-" in html.lower() or "agGrid" in html

    @pytest.mark.parametrize("aggrid_theme", ["quartz", "alpine", "balham", "material"])
    def test_aggrid_theme_variations(self, aggrid_theme):
        """AG Grid works with all theme variations."""
        config = WindowConfig(enable_aggrid=True, aggrid_theme=aggrid_theme)
        content = HtmlContent(html="<div id='grid'></div>")
        html = build_html(content, config, window_label="main")
        assert f"ag-theme-{aggrid_theme}" in html


class TestBuildToolbarHtml:
    """Tests for Toolbar.build_html() method."""

    def test_returns_empty_when_no_buttons(self):
        """Returns empty string when no items provided."""
        toolbar = Toolbar(items=[])
        result = toolbar.build_html()
        assert result == ""

    def test_returns_html_with_buttons(self):
        """Returns HTML with buttons."""
        toolbar = Toolbar(items=[{"label": "Click Me", "event": "toolbar:click-me"}])
        result = toolbar.build_html()
        assert "Click Me" in result
        assert "toolbar:click-me" in result
        assert "pywry-toolbar" in result

    def test_includes_position_class(self):
        """Includes position class in toolbar div."""
        toolbar = Toolbar(
            position="bottom",
            items=[{"type": "button", "label": "Btn", "event": "toolbar:click"}],
        )
        result = toolbar.build_html()
        assert "pywry-toolbar-bottom" in result


class TestBuildHtmlWithToolbar:
    """Tests for build_html with toolbar configurations."""

    def test_toolbar_position_top(self):
        """Verifies structure for top-positioned toolbar."""
        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")
        toolbars = [
            {
                "position": "top",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        html = build_html(content, config, window_label="main", toolbars=toolbars)
        assert "pywry-wrapper-top" in html
        assert "pywry-toolbar-top" in html
        assert "pywry-content" in html

    def test_toolbar_position_bottom(self):
        """Verifies structure for bottom-positioned toolbar."""
        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")
        toolbars = [
            {
                "position": "bottom",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        html = build_html(content, config, window_label="main", toolbars=toolbars)
        assert "pywry-wrapper-bottom" in html
        assert "pywry-toolbar-bottom" in html
        assert "pywry-content" in html

    def test_toolbar_position_left(self):
        """Verifies structure for left-positioned toolbar."""
        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")
        toolbars = [
            {
                "position": "left",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        html = build_html(content, config, window_label="main", toolbars=toolbars)
        assert "pywry-wrapper-left" in html
        assert "pywry-toolbar-left" in html

    def test_toolbar_position_right(self):
        """Verifies structure for right-positioned toolbar."""
        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")
        toolbars = [
            {
                "position": "right",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        html = build_html(content, config, window_label="main", toolbars=toolbars)
        assert "pywry-wrapper-right" in html
        assert "pywry-toolbar-right" in html

    def test_toolbar_position_inside(self):
        """Verifies structure for inside-positioned toolbar."""
        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")
        toolbars = [
            {
                "position": "inside",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        html = build_html(content, config, window_label="main", toolbars=toolbars)
        assert "pywry-wrapper-inside" in html
        assert "pywry-toolbar-inside" in html


class TestBuildHtmlWithSecretInput:
    """Tests for build_html with SecretInput in native window rendering.

    These tests verify that SecretInput security is maintained when
    rendering through the native window path (build_html in templates.py).
    """

    def test_secret_value_never_in_native_html(self):
        """Secret value must NEVER appear in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        secret_value = "super-secret-api-key-12345"
        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:api-key", value=secret_value)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Secret must NEVER be in HTML
        assert secret_value not in html
        # Mask should be shown instead
        assert "••••••••••••" in html
        assert 'data-has-value="true"' in html

    def test_secret_mask_shown_in_native_html(self):
        """Secret should show mask (••••) in native window when value exists."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:token", value="my-token")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        assert 'value="••••••••••••"' in html
        assert 'type="password"' in html
        assert "pywry-input-secret" in html

    def test_secret_empty_when_no_value_native(self):
        """Secret should be empty in native window when no value set."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:new-key", placeholder="Enter key")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Should have empty value, not mask
        assert 'value=""' in html
        assert 'data-has-value="true"' not in html

    def test_secret_value_exists_flag_native(self):
        """value_exists flag should work in native window rendering."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        # External storage scenario - no internal value but value_exists=True
        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="vault:secret", value_exists=True)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Mask should be shown even without internal value
        assert 'value="••••••••••••"' in html
        assert 'data-has-value="true"' in html

    def test_secret_edit_mode_in_native_html(self):
        """Edit mode scripts should be present in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Edit mode textarea creation should be in HTML
        assert "createElement('textarea')" in html
        assert "pywry-secret-textarea" in html
        # Input should be readonly
        assert " readonly" in html
        # Edit button should be present
        assert "pywry-secret-edit" in html

    def test_secret_reveal_copy_buttons_in_native_html(self):
        """Reveal and copy buttons should be in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", show_toggle=True, show_copy=True)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        assert "pywry-secret-toggle" in html
        assert "pywry-secret-copy" in html
        # Reveal/copy use event-based flow
        assert ":reveal" in html
        assert ":copy" in html

    def test_secret_base64_encoding_in_native_html(self):
        """Base64 encoding should be used in native window scripts."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Base64 encoding functions should be in the scripts
        assert "btoa" in html  # JavaScript base64 encode
        assert "atob" in html  # JavaScript base64 decode
        assert "encoded:true" in html

    def test_secret_pem_certificate_never_in_native_html(self):
        """PEM certificate must never appear in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        pem_cert = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0Gcert
-----END CERTIFICATE-----"""

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="certs:ssl", value=pem_cert)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # PEM certificate must NEVER be in HTML
        assert "-----BEGIN CERTIFICATE-----" not in html
        assert "-----END CERTIFICATE-----" not in html
        assert "MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0Gcert" not in html
        # Only mask should appear
        assert "••••••••••••" in html

    def test_secret_json_service_account_never_in_native_html(self):
        """JSON service account key must never appear in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        json_key = '{"type":"service_account","private_key":"secret"}'

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="gcp:key", value=json_key)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # JSON key must NEVER be in HTML (check key parts)
        assert '"type":"service_account"' not in html
        assert '"private_key":"secret"' not in html
        assert "service_account" not in html
        # Only mask should appear
        assert "••••••••••••" in html


class TestSecretInputBeforeUnloadBehavior:
    """Tests for beforeUnload behavior to verify secrets are cleared on page unload.

    These tests validate that:
    1. clearSecrets function exists in generated HTML
    2. beforeunload event listener is registered
    3. pagehide event listener is registered (mobile/Safari fallback)
    4. clearSecrets restores mask for inputs with values
    5. clearSecrets clears revealed secrets tracking
    6. Both inline and native window paths include unload handling
    """

    def test_clear_secrets_function_in_native_html(self):
        """clearSecrets function should be in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # clearSecrets function should be present
        assert "clearSecrets" in html

    def test_beforeunload_listener_in_native_html(self):
        """beforeunload event listener should be registered in native window HTML."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # beforeunload listener should be registered
        assert "beforeunload" in html

    def test_pagehide_listener_in_native_html(self):
        """pagehide event listener should be registered (mobile/Safari fallback)."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # pagehide listener should be registered
        assert "pagehide" in html

    def test_clear_secrets_restores_mask_logic(self):
        """clearSecrets should restore mask for inputs with data-has-value='true'."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Should have mask constant
        assert "SECRET_MASK" in html or "••••••••••••" in html
        # Should check data-has-value attribute
        assert "hasValue" in html or "has-value" in html

    def test_clear_secrets_clears_revealed_tracking(self):
        """clearSecrets should clear _revealedSecrets tracking object."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Should have revealed secrets tracking
        assert "_revealedSecrets" in html

    def test_hide_button_clears_revealed_tracking(self):
        """Hide button should clear _revealedSecrets entry when secret is hidden."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret", show_toggle=True)],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Hide should delete from revealed secrets
        assert "delete window.pywry._revealedSecrets" in html

    def test_input_type_reset_to_password_on_unload(self):
        """clearSecrets should set input type back to 'password'."""
        from pywry.toolbar import SecretInput

        config = WindowConfig()
        content = HtmlContent(html="<div>Content</div>")

        toolbars = [
            Toolbar(
                position="top",
                items=[SecretInput(event="auth:key", value="secret")],
            )
        ]

        html = build_html(content, config, window_label="main", toolbars=toolbars)

        # Should reset type to password (in clearSecrets or toggle script)
        assert "type='password'" in html or 'type="password"' in html
