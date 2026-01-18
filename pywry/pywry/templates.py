"""HTML template builder for PyWry windows."""

from __future__ import annotations

import datetime
import html
import json
import re
import uuid

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .assets import (
    get_aggrid_css,
    get_aggrid_defaults_js,
    get_aggrid_js,
    get_plotly_defaults_js,
    get_plotly_js,
    get_plotly_templates_js,
    get_pywry_css,
    get_toast_css,
)
from .models import HtmlContent, ThemeMode, WindowConfig
from .scripts import build_init_script
from .toolbar import (
    Toolbar,
    get_toolbar_script,
    wrap_content_with_toolbars,
)


class _NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy arrays, scalars, and datetime types."""

    def default(self, o: Any) -> Any:
        """Convert numpy/datetime types to JSON-serializable Python native types."""
        # Check for numpy array (includes datetime64 arrays)
        if hasattr(o, "tolist"):
            return o.tolist()
        # Check for numpy scalar types (int64, float64, datetime64, etc.)
        if hasattr(o, "item"):
            return o.item()
        # Python datetime types
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()
        # numpy datetime64/timedelta64 scalars
        type_name = type(o).__name__
        if type_name in ("datetime64", "timedelta64"):
            return str(o)
        return super().default(o)


if TYPE_CHECKING:
    from collections.abc import Sequence


# Re-export ThemeMode for consumers importing from templates
__all__ = ["ThemeMode", "build_html", "build_plotly_init_script"]


if TYPE_CHECKING:
    from .asset_loader import AssetLoader
    from .config import AssetSettings, PyWrySettings, SecuritySettings


def build_csp_meta(settings: SecuritySettings | None = None) -> str:
    """Build the Content Security Policy meta tag.

    Parameters
    ----------
    settings : SecuritySettings or None, optional
        Security settings with CSP directives.
        Uses defaults if not provided.

    Returns
    -------
    str
        The CSP meta tag HTML string.
    """
    if settings is None:
        from .config import SecuritySettings

        settings = SecuritySettings()

    csp = settings.build_csp()
    return f'<meta http-equiv="Content-Security-Policy" content="{csp}">'


def build_theme_class(theme: ThemeMode) -> str:
    """Get the HTML class for the current theme.

    Parameters
    ----------
    theme : ThemeMode
        The theme mode.

    Returns
    -------
    str
        The CSS class name.
    """
    if theme == ThemeMode.DARK:
        return "pywry-theme-dark"
    if theme == ThemeMode.LIGHT:
        return "pywry-theme-light"
    return "pywry-theme-dark"


def build_base_styles(settings: PyWrySettings | None = None) -> str:
    """Build base CSS styles for the window from bundled pywry.css.

    If a custom CSS file is specified in ThemeSettings, it will be loaded
    and appended after the base pywry.css styles.

    Parameters
    ----------
    settings : PyWrySettings or None
        Optional settings containing theme configuration with custom CSS file.

    Returns
    -------
    str
        The CSS styles wrapped in style tags.
    """
    # Load base pywry.css
    css = get_pywry_css()
    result = f"<style>{css}</style>" if css else ""

    # Load toast.css for notifications
    toast_css = get_toast_css()
    if toast_css:
        result += f"\n<style>{toast_css}</style>"

    # Load custom CSS file if specified
    if settings and settings.theme and settings.theme.css_file:
        css_path = Path(settings.theme.css_file)
        if css_path.exists():
            try:
                custom_css = css_path.read_text(encoding="utf-8")
                result += f"\n<style>{custom_css}</style>"
            except OSError:
                pass  # Silently ignore read errors

    return result


def build_json_data_script(json_data: dict[str, Any] | None) -> str:
    """Build the script tag for injecting JSON data.

    Parameters
    ----------
    json_data : dict[str, Any] or None
        The JSON data to inject.

    Returns
    -------
    str
        The script tag HTML string.
    """
    if json_data is None:
        return ""

    json_str = json.dumps(json_data, cls=_NumpyEncoder)
    return f"<script>window.json_data = {json_str};</script>"


def build_plotly_init_script(
    figure: dict[str, Any],
    chart_id: str | None = None,
    theme: ThemeMode = ThemeMode.DARK,
) -> str:
    """Build the Plotly initialization script and container.

    Features:
    - Creates div with unique ID
    - Injects Plotly.newPlot call
    - Handles theme templating (dark/light)
    - Registers chart with PyWry (window.registerPyWryChart)
    - Sets up resize handler

    Parameters
    ----------
    figure : dict
        The Plotly figure dictionary (data, layout, config).
    chart_id : str, optional
        The unique chart ID. If None, one will be generated.
    theme : ThemeMode
        The window theme.

    Returns
    -------
    str
        The HTML string containing the container div and initialization script.
    """
    if chart_id is None:
        chart_id = f"chart-{uuid.uuid4().hex[:8]}"

    # Ensure layout exists
    if "layout" not in figure:
        figure["layout"] = {}

    # Apply default Plotly config (hide logo, responsive, etc.)
    default_config = {
        "displaylogo": False,
        "responsive": True,
        "displayModeBar": "hover",
    }
    if "config" not in figure or figure["config"] is None:
        figure["config"] = default_config
    else:
        # Merge defaults with user config (user wins)
        figure["config"] = {**default_config, **figure["config"]}

    # Don't modify original figure in-place - use _NumpyEncoder for numpy array support
    fig_json = json.dumps(figure, cls=_NumpyEncoder)

    plotly_template = "plotly_dark" if theme == ThemeMode.DARK else "plotly_white"

    return f"""
    <div id="{chart_id}" class="pywry-plotly" data-pywry-chart="{chart_id}"></div>
    <script>
        (function() {{
            if (typeof Plotly === 'undefined') {{
                console.error("Plotly.js not loaded");
                return;
            }}

            var figData = {fig_json};
            var layout = figData.layout || {{}};
            var themeTemplate = '{plotly_template}';
            var templates = window.PYWRY_PLOTLY_TEMPLATES || {{}};

            // Resolve template if it's a string name
            if (typeof layout.template === 'string' && templates[layout.template]) {{
                layout.template = templates[layout.template];
            }} else if (!layout.template) {{
                // No user template - use window theme template
                layout.template = templates[themeTemplate] || null;
            }}

            figData.layout = layout;

            Plotly.newPlot('{chart_id}', figData.data || [], figData.layout, figData.config).then(function(gd) {{
                // Register with PyWry
                if (window.registerPyWryChart) {{
                    window.registerPyWryChart('{chart_id}', gd);
                }}

                // Store theme template for later reference
                gd.__pywry_theme_template__ = themeTemplate;
                // Expose last created chart for debugging access
                window.__PYWRY_PLOTLY_DIV__ = gd;

                window.addEventListener('resize', function() {{
                    Plotly.Plots.resize(gd);
                }});
            }});
        }})();
    </script>
    """


def build_plotly_script(config: WindowConfig) -> str:
    """Build the Plotly.js library injection with templates.

    Parameters
    ----------
    config : WindowConfig
        The window configuration.

    Returns
    -------
    str
        The script tags with Plotly.js content and templates.
    """
    if not config.enable_plotly:
        return ""

    plotly_js = get_plotly_js()
    if not plotly_js:
        # Assets not bundled - this should not happen in production
        raise RuntimeError("Plotly.js not found in bundled assets")

    parts = [f"<script>{plotly_js}</script>"]

    # Include Plotly templates (plotly_dark, plotly_white, etc.)
    templates_js = get_plotly_templates_js()
    if templates_js:
        parts.append(f"<script>{templates_js}</script>")

    # Include PyWry Plotly Defaults (event handling, registration logic)
    # This is the single source of truth for all Plotly event bridging
    plotly_defaults = get_plotly_defaults_js()
    if plotly_defaults:
        parts.append(f"<script>{plotly_defaults}</script>")

    return "\n".join(parts)


def build_aggrid_script(config: WindowConfig) -> str:
    """Build the AG Grid library injection.

    Parameters
    ----------
    config : WindowConfig
        The window configuration.

    Returns
    -------
    str
        The script and style tags for AG Grid.
    """
    if not config.enable_aggrid:
        return ""

    aggrid_js = get_aggrid_js()
    aggrid_css = get_aggrid_css(config.aggrid_theme, config.theme)
    aggrid_defaults_js = get_aggrid_defaults_js()

    parts = []

    if aggrid_css:
        parts.append(f"<style>{aggrid_css}</style>")
    else:
        raise RuntimeError(f"AG Grid CSS not found for theme {config.aggrid_theme}")

    if aggrid_js:
        parts.append(f"<script>{aggrid_js}</script>")
    else:
        raise RuntimeError("AG Grid JS not found in bundled assets")

    # Include our AG Grid defaults (context menu, column defaults, etc.)
    if aggrid_defaults_js:
        parts.append(f"<script>{aggrid_defaults_js}</script>")

    return "\n".join(parts)


def build_custom_css(content: HtmlContent, loader: AssetLoader | None = None) -> str:
    """Build custom CSS from files and inline content.

    Parameters
    ----------
    content : HtmlContent
        HTML content with CSS file references.
    loader : AssetLoader or None, optional
        Asset loader for reading files.

    Returns
    -------
    str
        HTML style tags for custom CSS.
    """
    parts = []

    # Inline CSS first
    if content.inline_css:
        parts.append(f'<style id="pywry-inline-css">{content.inline_css}</style>')

    # CSS files
    if content.css_files:
        if loader is None:
            from .asset_loader import get_asset_loader

            loader = get_asset_loader()

        for path in content.css_files:
            css_content = loader.load_css(path)
            if css_content:
                asset_id = loader.get_asset_id(path)
                parts.append(f'<style id="{asset_id}">{css_content}</style>')

    return "\n".join(parts)


def build_custom_scripts(content: HtmlContent, loader: AssetLoader | None = None) -> str:
    """Build custom JavaScript from files.

    Parameters
    ----------
    content : HtmlContent
        HTML content with script file references.
    loader : AssetLoader or None, optional
        Asset loader for reading files.

    Returns
    -------
    str
        HTML script tags for custom scripts.
    """
    if not content.script_files:
        return ""

    if loader is None:
        from .asset_loader import get_asset_loader

        loader = get_asset_loader()

    parts = []
    for path in content.script_files:
        script_content = loader.load_script(path)
        if script_content:
            parts.append(f"<script>{script_content}</script>")

    return "\n".join(parts)


def build_global_css(
    settings: AssetSettings | None = None, loader: AssetLoader | None = None
) -> str:
    """Build global CSS from AssetSettings.css_files.

    Parameters
    ----------
    settings : AssetSettings or None, optional
        Asset settings with CSS file references.
    loader : AssetLoader or None, optional
        Asset loader for reading files.

    Returns
    -------
    str
        HTML style tags for global CSS.
    """
    if settings is None or not settings.css_files:
        return ""

    if loader is None:
        from .asset_loader import configure_asset_loader, get_asset_loader

        # Configure loader with AssetSettings.path if available
        if settings.path:
            loader = configure_asset_loader(base_dir=Path(settings.path))
        else:
            loader = get_asset_loader()

    parts = []
    for path in settings.css_files:
        css_content = loader.load_css(path)
        if css_content:
            asset_id = loader.get_asset_id(path)
            parts.append(f'<style id="{asset_id}">{css_content}</style>')

    return "\n".join(parts)


def build_global_scripts(
    settings: AssetSettings | None = None, loader: AssetLoader | None = None
) -> str:
    """Build global JavaScript from AssetSettings.script_files.

    Parameters
    ----------
    settings : AssetSettings or None, optional
        Asset settings with script file references.
    loader : AssetLoader or None, optional
        Asset loader for reading files.

    Returns
    -------
    str
        HTML script tags for global scripts.
    """
    if settings is None or not settings.script_files:
        return ""

    if loader is None:
        from .asset_loader import configure_asset_loader, get_asset_loader

        # Configure loader with AssetSettings.path if available
        if settings.path:
            loader = configure_asset_loader(base_dir=Path(settings.path))
        else:
            loader = get_asset_loader()

    parts = []
    for path in settings.script_files:
        script_content = loader.load_script(path)
        if script_content:
            parts.append(f"<script>{script_content}</script>")

    return "\n".join(parts)


def fix_aggrid_theme_classes(content: str, theme: ThemeMode) -> str:
    """Fix AG Grid theme classes in HTML to match the window theme.

    This ensures that AG Grid theme classes (ag-theme-*) always match
    the window's dark/light mode. Users cannot accidentally have a
    dark window with a light grid or vice versa.

    Parameters
    ----------
    content : str
        The HTML content.
    theme : ThemeMode
        The window theme mode.

    Returns
    -------
    str
        HTML with corrected AG Grid theme classes.
    """
    is_dark = theme == ThemeMode.DARK

    # Pattern to match AG Grid theme classes
    # Matches: ag-theme-quartz, ag-theme-quartz-dark, ag-theme-alpine, etc.
    pattern = r"ag-theme-(quartz|alpine|balham|material)(-dark)?"

    def replacer(match: re.Match[str]) -> str:
        base_theme = match.group(1)  # quartz, alpine, balham, or material
        if is_dark:
            return f"ag-theme-{base_theme}-dark"
        return f"ag-theme-{base_theme}"

    return re.sub(pattern, replacer, content)


def fix_plotly_template(content: str, theme: ThemeMode) -> str:
    """Fix Plotly template references in HTML to match the window theme.

    This ensures that Plotly templates always match the window's dark/light mode.

    Parameters
    ----------
    content : str
        The HTML content.
    theme : ThemeMode
        The window theme mode.

    Returns
    -------
    str
        HTML with corrected Plotly template references.
    """
    is_dark = theme == ThemeMode.DARK
    correct_template = "plotly_dark" if is_dark else "plotly_white"

    # Fix template string
    pattern = r"template\s*:\s*['\"](?:plotly_dark|plotly_white|plotly)['\"]"
    replacement = f"template: '{correct_template}'"
    return re.sub(pattern, replacement, content)


def build_html(  # pylint: disable=too-many-statements
    content: HtmlContent,
    config: WindowConfig,
    window_label: str,
    settings: PyWrySettings | None = None,
    loader: AssetLoader | None = None,
    enable_hot_reload: bool = False,
    toolbars: Sequence[Toolbar | dict[str, Any]] | None = None,
) -> str:
    """Build the complete HTML document for a PyWry window.

    Parameters
    ----------
    content : HtmlContent
        The HTML content to display.
    config : WindowConfig
        The window configuration.
    window_label : str
        The label for this window.
    settings : PyWrySettings or None, optional
        PyWry settings for CSP, theme, etc.
    loader : AssetLoader or None, optional
        Asset loader for custom CSS/JS files.
    enable_hot_reload : bool, optional
        Whether to include hot reload JavaScript.
    toolbars : list[Toolbar | dict] or None, optional
        List of toolbar configurations. Each can be a Toolbar model or dict with:
        - position: "top", "bottom", "left", "right", "inside"
        - items: list of toolbar item configurations (Button, Select, etc.)

    Returns
    -------
    str
        The complete HTML document as a string.
    """
    # Get settings components
    csp_settings = settings.csp if settings else None
    asset_settings = settings.asset if settings else None

    theme_class = build_theme_class(config.theme)
    csp_meta = build_csp_meta(csp_settings)
    base_styles = build_base_styles(settings)
    json_script = build_json_data_script(content.json_data)
    plotly_script = build_plotly_script(config)
    aggrid_script = build_aggrid_script(config)
    init_script = build_init_script(window_label, enable_hot_reload)
    toolbar_script = get_toolbar_script() if toolbars else ""

    # Custom CSS and scripts from content
    custom_css = build_custom_css(content, loader)
    custom_scripts = build_custom_scripts(content, loader)

    # Global CSS and scripts from AssetSettings
    global_css = build_global_css(asset_settings, loader)
    global_scripts = build_global_scripts(asset_settings, loader)

    # Custom init script from content - placed at end of body so DOM is ready
    custom_init = ""
    if content.init_script:
        custom_init = f"<script>{content.init_script}</script>"

    # Check if content.html is a complete HTML document or a fragment
    user_html = content.html.strip()

    # Fix AG Grid and Plotly themes in user HTML to match window theme
    user_html = fix_aggrid_theme_classes(user_html, config.theme)
    user_html = fix_plotly_template(user_html, config.theme)

    is_complete_doc = user_html.lower().startswith("<!doctype") or user_html.lower().startswith(
        "<html"
    )

    # Build and inject toolbars using centralized function
    if toolbars:
        # Use the canonical wrap_content_with_toolbars from toolbar.py
        # This handles all 7 positions: header, footer, top, bottom, left, right, inside
        user_html = wrap_content_with_toolbars(user_html, toolbars)

    if is_complete_doc:
        # Inject our scripts into the existing document
        # First, add theme class to <html> tag
        # Find <html ...> tag and add class
        def add_theme_class_to_html_tag(html_str: str, theme_cls: str) -> str:
            """Add theme class to <html> tag, preserving existing classes."""
            pattern = r"(<html)(\s+[^>]*)?>"

            def replacer(match: re.Match[str]) -> str:
                opening = match.group(1)
                attrs = match.group(2) or ""

                # Check if class attribute exists
                class_pattern = r'class\s*=\s*["\']([^"\']*)["\']'
                class_match = re.search(class_pattern, attrs)
                if class_match:
                    existing = class_match.group(1)
                    if theme_cls not in existing.split():
                        new_class = f"{existing} {theme_cls}"
                        attrs = re.sub(class_pattern, f'class="{new_class}"', attrs)
                else:
                    attrs = f' class="{theme_cls}"' + attrs
                return f"{opening}{attrs}>"

            return re.sub(pattern, replacer, html_str, count=1, flags=re.IGNORECASE)

        user_html = add_theme_class_to_html_tag(user_html, theme_class)

        # Find the </head> tag and inject before it
        head_close_pos = user_html.lower().find("</head>")
        if head_close_pos != -1:
            injection = f"""
                {csp_meta}
                {base_styles}
                {global_css}
                {custom_css}
                {plotly_script}
                {aggrid_script}
                {json_script}
                <script>{init_script}</script>
                {toolbar_script}
                {global_scripts}
                {custom_scripts}
                {custom_init}
            """
            return user_html[:head_close_pos] + injection + user_html[head_close_pos:]

        # No </head> found, inject at the beginning after <html>
        html_pos = user_html.lower().find("<html")
        if html_pos != -1:
            # Find the end of the <html> tag
            html_end = user_html.find(">", html_pos)
            if html_end != -1:
                before = user_html[: html_end + 1]
                after = user_html[html_end + 1 :]
                return (
                    before
                    + f"""
                    <head>
                        {csp_meta}
                        {base_styles}
                        {global_css}
                        {custom_css}
                        {plotly_script}
                        {aggrid_script}
                        {json_script}
                        <script>{init_script}</script>
                        {toolbar_script}
                        {global_scripts}
                        {custom_scripts}
                        {custom_init}
                    </head>
                """
                    + after
                )
        return user_html

    # Build a complete document wrapper for HTML fragments
    return f"""<!DOCTYPE html>
<html lang="en" class="pywry-native {theme_class}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {csp_meta}
    <title>{html.escape(config.title)}</title>
    {base_styles}
    {global_css}
    {custom_css}
    {plotly_script}
    {aggrid_script}
    {json_script}
    <script>{init_script}</script>
    {toolbar_script}
    {global_scripts}
    {custom_scripts}
</head>
<body>
    <div class="pywry-container">
        {user_html}
    </div>
    {custom_init}
</body>
</html>"""


def build_content_update_script(html_content: str) -> str:
    """Build a script to update window content without full reload.

    Parameters
    ----------
    html_content : str
        The new HTML content.

    Returns
    -------
    str
        JavaScript code to update the document content.
    """
    # Use ensure_ascii=False to preserve emoji and unicode characters
    escaped_html = json.dumps(html_content, ensure_ascii=False)
    return f"""
    (function() {{
        var container = document.querySelector('.pywry-container');
        if (container) {{
            container.innerHTML = {escaped_html};
        }} else {{
            document.body.innerHTML = '<div class="pywry-container">' + {escaped_html} + '</div>';
        }}
    }})();
    """
