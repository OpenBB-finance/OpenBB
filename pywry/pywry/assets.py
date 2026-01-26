"""Asset loading utilities for bundled JavaScript and CSS files."""

from __future__ import annotations

import gzip

from functools import lru_cache
from pathlib import Path

from .log import debug
from .models import ThemeMode


# Asset directory path (bundled/external files: libraries, icons, CSS)
ASSETS_DIR = Path(__file__).parent / "frontend" / "assets"

# Source directory path (our JavaScript source files)
SRC_DIR = Path(__file__).parent / "frontend" / "src"

# Style directory path (our CSS source files)
STYLE_DIR = Path(__file__).parent / "frontend" / "style"


@lru_cache(maxsize=1)
def get_plotly_js() -> str:
    """Get the bundled Plotly.js library content.

    Returns
    -------
    str
        The Plotly.js source code (full bundle with templates), or empty if not bundled.
    """
    # Try compressed file first (full bundle with templates)
    gz_file = ASSETS_DIR / "plotly-3.3.1.js.gz"
    if gz_file.exists():
        debug("Loading Plotly.js from compressed bundled assets")
        return gzip.decompress(gz_file.read_bytes()).decode("utf-8")

    # Fallback to uncompressed file
    js_file = ASSETS_DIR / "plotly-3.3.1.js"
    if js_file.exists():
        debug("Loading Plotly.js from bundled assets")
        return js_file.read_text(encoding="utf-8")

    # Try minified version (may not have templates)
    gz_min = ASSETS_DIR / "plotly-3.3.1.min.js.gz"
    if gz_min.exists():
        debug("Loading Plotly.js minified from compressed bundled assets")
        return gzip.decompress(gz_min.read_bytes()).decode("utf-8")

    js_min = ASSETS_DIR / "plotly-3.3.1.min.js"
    if js_min.exists():
        debug("Loading Plotly.js minified from bundled assets")
        return js_min.read_text(encoding="utf-8")

    # No bundled assets
    debug("Plotly.js not bundled")
    return ""


@lru_cache(maxsize=1)
def get_plotly_templates_js() -> str:
    """Get the bundled Plotly templates (plotly_dark, plotly_white).

    Returns
    -------
    str
        JavaScript that defines window.PYWRY_PLOTLY_TEMPLATES, or empty if not bundled.
    """
    js_file = SRC_DIR / "plotly-templates.js"
    if js_file.exists():
        debug("Loading Plotly templates from src")
        return js_file.read_text(encoding="utf-8")

    debug("Plotly templates not found")
    return ""


@lru_cache(maxsize=1)
def get_aggrid_js() -> str:
    """Get the bundled AG Grid library content.

    Returns
    -------
    str
        The minified AG Grid source code, or empty string if not bundled.
    """
    # Try compressed file first
    gz_file = ASSETS_DIR / "ag-grid-community-35.0.0.min.js.gz"
    if gz_file.exists():
        debug("Loading AG Grid JS from compressed bundled assets")
        return gzip.decompress(gz_file.read_bytes()).decode("utf-8")

    # Fallback to uncompressed file
    js_file = ASSETS_DIR / "ag-grid-community-35.0.0.min.js"
    if js_file.exists():
        debug("Loading AG Grid JS from bundled assets")
        return js_file.read_text(encoding="utf-8")

    debug("Using AG Grid CDN fallback")
    return ""


@lru_cache(maxsize=1)
def get_pywry_css() -> str:
    """Get the PyWry CSS content.

    Returns
    -------
    str
        The PyWry CSS content, or empty if not found.
    """
    css_file = STYLE_DIR / "pywry.css"
    if css_file.exists():
        return css_file.read_text(encoding="utf-8")
    return ""


@lru_cache(maxsize=1)
def get_scrollbar_js() -> str:
    """Get the custom scrollbar JavaScript content.

    This provides macOS-style overlay scrollbars that work in both
    native windows and widget/iframe contexts.

    Returns
    -------
    str
        The scrollbar JavaScript content, or empty if not found.
    """
    js_file = SRC_DIR / "scrollbar.js"
    if js_file.exists():
        return js_file.read_text(encoding="utf-8")
    return ""


def clear_css_cache() -> None:
    """Clear the cached CSS and JS content.

    Call this after modifying pywry.css or scrollbar.js during development
    to force a reload on the next request.
    """
    get_pywry_css.cache_clear()
    get_scrollbar_js.cache_clear()
    get_toast_css.cache_clear()
    get_aggrid_css.cache_clear()


@lru_cache(maxsize=8)
def get_aggrid_css(theme: str, mode: ThemeMode) -> str:
    """Get the AG Grid CSS for a specific theme and mode.

    Parameters
    ----------
    theme : str
        The AG Grid theme name (quartz, alpine, balham, material).
    mode : ThemeMode
        The theme mode (light or dark).

    Returns
    -------
    str
        The combined CSS content, or empty string if not found.
    """
    # Theme CSS file names include version and mode suffix
    mode_suffix = "-dark" if mode == ThemeMode.DARK else "-light"
    theme_name = f"ag-theme-{theme}{mode_suffix}-35.0.0"

    # Try compressed file first
    gz_file = ASSETS_DIR / f"{theme_name}.css.gz"
    if gz_file.exists():
        debug(f"Loading AG Grid CSS from compressed bundled assets: {theme_name}")
        return gzip.decompress(gz_file.read_bytes()).decode("utf-8")

    # Fallback to uncompressed file
    css_file = ASSETS_DIR / f"{theme_name}.css"
    if css_file.exists():
        debug(f"Loading AG Grid CSS from bundled assets: {theme_name}")
        # Only load theme CSS - do NOT load base ag-grid.css as it conflicts with Theming API
        return css_file.read_text(encoding="utf-8")

    debug(f"AG Grid CSS not bundled: {theme_name}")
    return ""


def _get_pywry_css_bundled() -> str:
    """Get the bundled PyWry base CSS (internal helper).

    Returns
    -------
    str
        The PyWry base CSS content.
    """
    css_file = STYLE_DIR / "pywry.css"
    if css_file.exists():
        debug("Loading PyWry CSS from bundled assets")
        return css_file.read_text(encoding="utf-8")

    debug("PyWry CSS not bundled")
    return ""


@lru_cache(maxsize=1)
def get_openbb_icon() -> bytes:
    """Get the bundled OpenBB icon.

    Returns
    -------
    bytes
        The icon file content as bytes, or empty bytes if not found.
    """
    icon_file = ASSETS_DIR / "icon.png"
    if icon_file.exists():
        return icon_file.read_bytes()
    return b""


@lru_cache(maxsize=1)
def get_plotly_defaults_js() -> str:
    """Get the PyWry Plotly defaults JavaScript.

    This is the SINGLE SOURCE OF TRUTH for all Plotly chart configuration
    and event handling. All rendering paths (notebook, inline, window)
    must include this.

    Returns
    -------
    str
        The Plotly defaults JavaScript content.
    """
    js_file = SRC_DIR / "plotly-defaults.js"
    if js_file.exists():
        debug("Loading Plotly defaults JS from src")
        return js_file.read_text(encoding="utf-8")
    debug("Plotly defaults JS not found")
    return ""


@lru_cache(maxsize=1)
def get_aggrid_defaults_js() -> str:
    """Get the PyWry AG Grid defaults JavaScript.

    This is the SINGLE SOURCE OF TRUTH for all AG Grid configuration.
    All rendering paths (notebook, inline, window) must include this.

    Returns
    -------
    str
        The AG Grid defaults JavaScript content.
    """
    js_file = SRC_DIR / "aggrid-defaults.js"
    if js_file.exists():
        debug("Loading AG Grid defaults JS from src")
        return js_file.read_text(encoding="utf-8")
    debug("AG Grid defaults JS not found")
    return ""


def get_openbb_icon_path() -> Path | None:
    """Get the path to the bundled OpenBB icon.

    Returns
    -------
    Path or None
        The path to the icon file, or None if not found.
    """
    icon_file = ASSETS_DIR / "icon.png"
    if icon_file.exists():
        return icon_file
    return None


def clear_cache() -> None:
    """Clear all cached asset data."""
    get_plotly_js.cache_clear()
    get_aggrid_js.cache_clear()
    get_aggrid_css.cache_clear()
    get_aggrid_defaults_js.cache_clear()
    get_pywry_css.cache_clear()
    get_openbb_icon.cache_clear()
    get_toast_notifications_js.cache_clear()
    get_toast_css.cache_clear()


@lru_cache(maxsize=1)
def get_toast_notifications_js() -> str:
    """Get the PyWry Toast notification JavaScript.

    This provides the PYWRY_TOAST object for showing typed toast
    notifications (info, success, warning, error, confirm).

    Returns
    -------
    str
        The toast notifications JavaScript content.
    """
    js_file = SRC_DIR / "toast-notifications.js"
    if js_file.exists():
        debug("Loading toast notifications JS from src")
        return js_file.read_text(encoding="utf-8")
    debug("Toast notifications JS not found")
    return ""


@lru_cache(maxsize=1)
def get_toast_css() -> str:
    """Get the PyWry Toast CSS styles.

    Returns
    -------
    str
        The toast CSS content.
    """
    css_file = STYLE_DIR / "toast.css"
    if css_file.exists():
        debug("Loading toast CSS from style")
        return css_file.read_text(encoding="utf-8")
    debug("Toast CSS not found")
    return ""
