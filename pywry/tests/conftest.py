"""Pytest configuration and fixtures."""

import sys

from pathlib import Path

import pytest


# Add pywry to path for imports
pywry_path = Path(__file__).parent.parent / "pywry"
if str(pywry_path) not in sys.path:
    sys.path.insert(0, str(pywry_path.parent))


@pytest.fixture
def temp_css_file(tmp_path):
    """Create a temporary CSS file."""
    css_file = tmp_path / "test.css"
    css_file.write_text("body { color: red; }")
    return css_file


@pytest.fixture
def temp_js_file(tmp_path):
    """Create a temporary JavaScript file."""
    js_file = tmp_path / "test.js"
    js_file.write_text("console.log('test');")
    return js_file


@pytest.fixture
def sample_html_content():
    """Create a sample HtmlContent object."""
    from pywry.models import HtmlContent

    return HtmlContent(
        html="<div id='app'>Hello World</div>",
        json_data={"message": "hello"},
        init_script="console.log('init');",
    )


@pytest.fixture
def sample_window_config():
    """Create a sample WindowConfig object."""
    from pywry.models import ThemeMode, WindowConfig

    return WindowConfig(
        title="Test Window",
        width=1024,
        height=768,
        theme=ThemeMode.DARK,
    )


@pytest.fixture
def default_settings():
    """Create default PyWrySettings."""
    from pywry.config import PyWrySettings

    return PyWrySettings()


@pytest.fixture
def permissive_csp():
    """Create permissive CSP settings."""
    from pywry.config import SecuritySettings

    return SecuritySettings.permissive()


@pytest.fixture
def strict_csp():
    """Create strict CSP settings."""
    from pywry.config import SecuritySettings

    return SecuritySettings.strict()


@pytest.fixture
def asset_loader(tmp_path):
    """Create an AssetLoader with temp directory as base."""
    from pywry.asset_loader import AssetLoader

    return AssetLoader(base_dir=tmp_path)


@pytest.fixture
def callback_registry():
    """Get a clean callback registry."""
    from pywry.callbacks import get_registry

    registry = get_registry()
    registry.clear()
    return registry
