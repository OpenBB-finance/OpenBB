"""Tests for Content Security Policy.

Tests CSP configuration and meta tag generation.
"""

from pywry.config import PyWrySettings, SecuritySettings
from pywry.models import HtmlContent, WindowConfig
from pywry.templates import build_csp_meta, build_html


class TestDefaultCspValues:
    """Tests for default CSP directive values."""

    def test_default_src_includes_self(self):
        """default-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.default_src

    def test_default_src_includes_unsafe_inline(self):
        """default-src includes 'unsafe-inline'."""
        csp = SecuritySettings()
        assert "'unsafe-inline'" in csp.default_src

    def test_default_src_includes_unsafe_eval(self):
        """default-src includes 'unsafe-eval' for Plotly."""
        csp = SecuritySettings()
        assert "'unsafe-eval'" in csp.default_src

    def test_default_src_includes_data(self):
        """default-src includes data: scheme."""
        csp = SecuritySettings()
        assert "data:" in csp.default_src

    def test_default_src_includes_blob(self):
        """default-src includes blob: scheme."""
        csp = SecuritySettings()
        assert "blob:" in csp.default_src

    def test_connect_src_includes_self(self):
        """connect-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.connect_src

    def test_connect_src_includes_http_wildcard(self):
        """connect-src includes http wildcard."""
        csp = SecuritySettings()
        assert "http://*:*" in csp.connect_src

    def test_connect_src_includes_https_wildcard(self):
        """connect-src includes https wildcard."""
        csp = SecuritySettings()
        assert "https://*:*" in csp.connect_src

    def test_connect_src_includes_ws_wildcard(self):
        """connect-src includes ws wildcard."""
        csp = SecuritySettings()
        assert "ws://*:*" in csp.connect_src

    def test_connect_src_includes_wss_wildcard(self):
        """connect-src includes wss wildcard."""
        csp = SecuritySettings()
        assert "wss://*:*" in csp.connect_src

    def test_script_src_includes_self(self):
        """script-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.script_src

    def test_script_src_includes_unsafe_inline(self):
        """script-src includes 'unsafe-inline'."""
        csp = SecuritySettings()
        assert "'unsafe-inline'" in csp.script_src

    def test_script_src_includes_unsafe_eval(self):
        """script-src includes 'unsafe-eval'."""
        csp = SecuritySettings()
        assert "'unsafe-eval'" in csp.script_src

    def test_style_src_includes_self(self):
        """style-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.style_src

    def test_style_src_includes_unsafe_inline(self):
        """style-src includes 'unsafe-inline'."""
        csp = SecuritySettings()
        assert "'unsafe-inline'" in csp.style_src

    def test_img_src_includes_self(self):
        """img-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.img_src

    def test_img_src_includes_data(self):
        """img-src includes data: scheme."""
        csp = SecuritySettings()
        assert "data:" in csp.img_src

    def test_img_src_includes_blob(self):
        """img-src includes blob: scheme."""
        csp = SecuritySettings()
        assert "blob:" in csp.img_src

    def test_font_src_includes_self(self):
        """font-src includes 'self'."""
        csp = SecuritySettings()
        assert "'self'" in csp.font_src

    def test_font_src_includes_data(self):
        """font-src includes data: scheme."""
        csp = SecuritySettings()
        assert "data:" in csp.font_src


class TestPermissiveFactory:
    """Tests for SecuritySettings.permissive() factory."""

    def test_allows_unsafe_eval(self):
        """permissive() allows unsafe-eval."""
        csp = SecuritySettings.permissive()
        assert "'unsafe-eval'" in csp.script_src
        assert "'unsafe-eval'" in csp.default_src

    def test_allows_unsafe_inline(self):
        """permissive() allows unsafe-inline."""
        csp = SecuritySettings.permissive()
        assert "'unsafe-inline'" in csp.script_src
        assert "'unsafe-inline'" in csp.style_src

    def test_allows_data_scheme(self):
        """permissive() allows data: scheme."""
        csp = SecuritySettings.permissive()
        assert "data:" in csp.default_src

    def test_allows_blob_scheme(self):
        """permissive() allows blob: scheme."""
        csp = SecuritySettings.permissive()
        assert "blob:" in csp.default_src

    def test_allows_wildcard_connections(self):
        """permissive() allows wildcard connections."""
        csp = SecuritySettings.permissive()
        assert "http://*:*" in csp.connect_src
        assert "https://*:*" in csp.connect_src


class TestStrictFactory:
    """Tests for SecuritySettings.strict() factory."""

    def test_has_self_in_default_src(self):
        """strict() has 'self' in default-src."""
        csp = SecuritySettings.strict()
        assert "'self'" in csp.default_src

    def test_removes_unsafe_eval_from_default(self):
        """strict() removes 'unsafe-eval' from default-src."""
        csp = SecuritySettings.strict()
        assert "'unsafe-eval'" not in csp.default_src


class TestLocalhostFactory:
    """Tests for SecuritySettings.localhost() factory."""

    def test_allows_localhost_connections(self):
        """localhost() allows localhost connections."""
        csp = SecuritySettings.localhost()
        connect = csp.connect_src
        assert "localhost" in connect or "127.0.0.1" in connect


class TestCspMetaTag:
    """Tests for CSP meta tag generation."""

    def test_creates_meta_tag(self):
        """Creates Content-Security-Policy meta tag."""
        meta = build_csp_meta(SecuritySettings())
        assert '<meta http-equiv="Content-Security-Policy"' in meta

    def test_includes_default_src_directive(self):
        """Includes default-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "default-src" in meta

    def test_includes_script_src_directive(self):
        """Includes script-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "script-src" in meta

    def test_includes_style_src_directive(self):
        """Includes style-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "style-src" in meta

    def test_includes_img_src_directive(self):
        """Includes img-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "img-src" in meta

    def test_includes_font_src_directive(self):
        """Includes font-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "font-src" in meta

    def test_includes_connect_src_directive(self):
        """Includes connect-src directive."""
        meta = build_csp_meta(SecuritySettings())
        assert "connect-src" in meta


class TestCspInHtml:
    """Tests for CSP integration in HTML output."""

    def test_build_html_includes_csp(self):
        """build_html includes CSP meta tag."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        settings = PyWrySettings()
        html = build_html(content, config, window_label="main", settings=settings)
        assert "Content-Security-Policy" in html

    def test_permissive_csp_in_html(self):
        """Permissive CSP is included in HTML."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        settings = PyWrySettings(csp=SecuritySettings.permissive())
        html = build_html(content, config, window_label="main", settings=settings)
        assert "'unsafe-eval'" in html

    def test_strict_csp_in_html(self):
        """Strict CSP is included in HTML."""
        config = WindowConfig()
        content = HtmlContent(html="<div></div>")
        settings = PyWrySettings(csp=SecuritySettings.strict())
        html = build_html(content, config, window_label="main", settings=settings)
        assert "default-src" in html
        # Strict CSP should NOT have unsafe-eval in default-src
        # (may still have it in script-src for Plotly compat)


class TestCspDirectiveValues:
    """Tests for individual CSP directive values."""

    def test_default_src_is_string(self):
        """default_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.default_src, str)

    def test_script_src_is_string(self):
        """script_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.script_src, str)

    def test_style_src_is_string(self):
        """style_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.style_src, str)

    def test_img_src_is_string(self):
        """img_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.img_src, str)

    def test_font_src_is_string(self):
        """font_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.font_src, str)

    def test_connect_src_is_string(self):
        """connect_src is a string."""
        csp = SecuritySettings()
        assert isinstance(csp.connect_src, str)
