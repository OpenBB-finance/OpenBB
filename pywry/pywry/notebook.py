"""Notebook environment detection for PyWry.

Detects whether PyWry is running in a Jupyter notebook environment
and provides utilities for inline rendering.
"""
# mypy: disable-error-code="no-untyped-call,attr-defined,arg-type,type-arg"

from __future__ import annotations

import os

from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any


class NotebookEnvironment(Enum):
    """Detected notebook environment type."""

    NONE = "none"  # Not a notebook - use native window
    COLAB = "colab"  # Google Colab
    KAGGLE = "kaggle"  # Kaggle Notebooks
    AZURE = "azure"  # Azure Notebooks
    VSCODE = "vscode"  # VS Code notebook
    NTERACT = "nteract"  # nteract
    COCALC = "cocalc"  # CoCalc
    DATABRICKS = "databricks"  # Databricks
    JUPYTERLAB = "jupyterlab"  # JupyterLab
    JUPYTER_NOTEBOOK = "notebook"  # Classic Jupyter Notebook
    IPYTHON_TERMINAL = "terminal"  # IPython terminal (NOT inline)
    REMOTE_JUPYTER = "remote_jupyter"  # Remote Jupyter (containers, etc.)


# Environment detection rules: (check_function, environment)
_ENV_CHECKS: list[tuple[str, NotebookEnvironment]] = [
    ("_check_colab", NotebookEnvironment.COLAB),
    ("_check_kaggle", NotebookEnvironment.KAGGLE),
    ("_check_azure", NotebookEnvironment.AZURE),
    ("_check_vscode", NotebookEnvironment.VSCODE),
    ("_check_nteract", NotebookEnvironment.NTERACT),
    ("_check_cocalc", NotebookEnvironment.COCALC),
    ("_check_databricks", NotebookEnvironment.DATABRICKS),
    ("_check_remote_jupyter", NotebookEnvironment.REMOTE_JUPYTER),
    ("_check_jupyterlab", NotebookEnvironment.JUPYTERLAB),
]


def _check_colab() -> bool:
    try:
        import google.colab as _colab  # type: ignore[import-not-found]

        del _colab
    except ImportError:
        return False
    return True


def _check_kaggle() -> bool:
    return Path("/kaggle/input").exists()


def _check_azure() -> bool:
    return "AZURE_NOTEBOOKS_HOST" in os.environ


def _check_vscode() -> bool:
    return "VSCODE_PID" in os.environ


def _check_nteract() -> bool:
    return "NTERACT_EXE" in os.environ


def _check_cocalc() -> bool:
    return "COCALC_PROJECT_ID" in os.environ


def _check_databricks() -> bool:
    return "DATABRICKS_RUNTIME_VERSION" in os.environ


def _check_remote_jupyter() -> bool:
    return bool(os.environ.get("JUPYTER_SERVER_ROOT") or os.environ.get("JUPYTERHUB_USER"))


def _check_jupyterlab() -> bool:
    return "JUPYTERLAB_WORKSPACES_DIR" in os.environ


@lru_cache(maxsize=1)
def detect_notebook_environment() -> NotebookEnvironment:
    """Detect the current notebook environment.

    This function is cached - environment detection only happens once.

    Returns
    -------
    NotebookEnvironment
        The detected environment. NONE means use native window,
        IPYTHON_TERMINAL means use native window (not inline).
    """
    return _detect_environment_impl()


def _detect_environment_impl() -> NotebookEnvironment:
    """Implementation of environment detection (avoids too many returns)."""
    try:
        from IPython import get_ipython
    except ImportError:
        return NotebookEnvironment.NONE

    ipython = get_ipython()
    if ipython is None:
        return NotebookEnvironment.NONE

    # Check shell class name
    shell_class = ipython.__class__.__name__

    # Terminal IPython - NOT inline rendering
    if shell_class == "TerminalInteractiveShell":
        return NotebookEnvironment.IPYTHON_TERMINAL

    # Must be ZMQInteractiveShell (or similar) for notebook
    if shell_class != "ZMQInteractiveShell":
        return NotebookEnvironment.NONE

    # Check if kernel is from ipykernel (real notebook kernel)
    kernel_module = type(ipython).__module__
    if not kernel_module.startswith("ipykernel"):
        return NotebookEnvironment.NONE

    # Check specific environments and return first match
    return _check_specific_environment()


def _check_specific_environment() -> NotebookEnvironment:
    """Check for specific notebook environments."""
    checkers = {
        "_check_colab": _check_colab,
        "_check_kaggle": _check_kaggle,
        "_check_azure": _check_azure,
        "_check_vscode": _check_vscode,
        "_check_nteract": _check_nteract,
        "_check_cocalc": _check_cocalc,
        "_check_databricks": _check_databricks,
        "_check_remote_jupyter": _check_remote_jupyter,
        "_check_jupyterlab": _check_jupyterlab,
    }

    for check_name, env in _ENV_CHECKS:
        if checkers[check_name]():
            return env

    # Default to generic Jupyter notebook
    return NotebookEnvironment.JUPYTER_NOTEBOOK


def should_use_inline_rendering() -> bool:
    """Check if inline notebook rendering should be used.

    Returns True for:
    - Notebook environments (Jupyter, Colab, VS Code, etc.)
    - When PYWRY_SERVER__FORCE_NOTEBOOK=true (for headless web deployments)

    Returns False for:
    - No IPython
    - IPython terminal
    - Unknown environments (unless force_notebook is set)

    Returns
    -------
    bool
        True if inline rendering should be used.
    """
    # Check for explicit force_notebook setting (for headless deployments)
    from .config import get_settings

    if get_settings().server.force_notebook:
        return True

    env = detect_notebook_environment()
    return env not in (
        NotebookEnvironment.NONE,
        NotebookEnvironment.IPYTHON_TERMINAL,
    )


def is_anywidget_available() -> bool:
    """Check if anywidget is installed and available.

    Returns
    -------
    bool
        True if anywidget >= 0.9.0 is available.
    """
    try:
        import anywidget
    except ImportError:
        return False
    # Check version - we need 0.9.0+ for proper ESM support
    version = getattr(anywidget, "__version__", "0.0.0")
    parts = version.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    return major > 0 or (major == 0 and minor >= 9)


def is_cloud_environment() -> bool:
    """Check if running in a cloud-hosted notebook environment.

    Cloud environments may use CDN assets instead of embedded.

    Returns
    -------
    bool
        True for Colab, Kaggle, Azure, Databricks.
    """
    env = detect_notebook_environment()
    return env in (
        NotebookEnvironment.COLAB,
        NotebookEnvironment.KAGGLE,
        NotebookEnvironment.AZURE,
        NotebookEnvironment.DATABRICKS,
    )


def clear_environment_cache() -> None:
    """Clear the cached environment detection.

    Useful for testing or when environment changes.
    """
    detect_notebook_environment.cache_clear()


def _wrap_content_with_toolbar(content: str, toolbar_html: str, position: str) -> str:
    """Wrap content HTML with toolbar based on position.

    Parameters
    ----------
    content : str
        The main content HTML.
    toolbar_html : str
        The toolbar HTML (may be empty).
    position : str
        Toolbar position ("top", "bottom", "left", "right", "inside").

    Returns
    -------
    str
        Wrapped HTML with toolbar in correct position.
    """
    if not toolbar_html:
        return content

    wrappers = {
        "bottom": f"<div class='pywry-wrapper-bottom'><div class='pywry-content'>{content}</div>{toolbar_html}</div>",
        "top": f"<div class='pywry-wrapper-top'>{toolbar_html}<div class='pywry-content'>{content}</div></div>",
        "left": f"<div class='pywry-wrapper-left'>{toolbar_html}<div class='pywry-content'>{content}</div></div>",
        "right": f"<div class='pywry-wrapper-right'><div class='pywry-content'>{content}</div>{toolbar_html}</div>",
        "inside": f"<div class='pywry-wrapper-inside'>{toolbar_html}{content}</div>",
    }
    return wrappers.get(position, content)


def create_plotly_widget(  # pylint: disable=too-many-branches
    figure_json: str,
    widget_id: str,
    title: str = "PyWry",
    theme: str = "dark",
    width: str = "100%",
    height: int = 500,
    port: int | None = None,
    buttons: list[dict] | None = None,
    toolbar_position: str = "top",
) -> Any:
    """Create a Plotly widget using the best available backend.

    Automatically selects:
    1. PyWryPlotlyWidget (anywidget) if available - best performance
    2. InlineWidget (FastAPI) as fallback - broader compatibility

    Parameters
    ----------
    figure_json : str
        Plotly figure as JSON string (should include 'config' if needed).
    widget_id : str
        Unique widget identifier.
    title : str
        Widget title.
    theme : str
        'dark' or 'light'.
    width : str
        Widget width (CSS).
    height : int
        Widget height in pixels.
    port : int, optional
        Server port (only for InlineWidget fallback).
    buttons : list[dict], optional
        List of button configs to generate a toolbar.
    toolbar_position : str
        Toolbar position ("top", "bottom", "left", "right", "inside").

    Returns
    -------
    BaseWidget
        Widget instance implementing BaseWidget protocol.
    """
    # Use anywidget when available for better performance
    from .widget import HAS_ANYWIDGET

    use_anywidget = HAS_ANYWIDGET
    if use_anywidget:
        from . import inline
        from .templates import ThemeMode, build_toolbar_html
        from .widget import PyWryPlotlyWidget

        # Generate custom header with toolbar using shared template
        toolbar_html = ""
        if buttons:
            mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
            toolbar_html = build_toolbar_html(buttons, mode, toolbar_position)

        # Generate HTML content for the widget (content only, not full document)
        # This provides just the chart container div, no embedded scripts
        html = inline.generate_plotly_html(
            figure_json, widget_id, title, theme, full_document=False, buttons=None
        )  # Don't pass buttons to generate_plotly_html, we handle it here

        # Inject toolbar based on position using helper
        html = _wrap_content_with_toolbar(html, toolbar_html, toolbar_position)

        return PyWryPlotlyWidget(
            content=html,
            figure_json=figure_json,  # Pass figure data directly to widget
            theme=theme,
            width=width,
            height=f"{height}px",
        )

    # Fallback to InlineWidget (FastAPI server)
    from . import inline

    # Let generate_plotly_html handle toolbar injection for IFrame
    html = inline.generate_plotly_html(
        figure_json, widget_id, title, theme, buttons=buttons, toolbar_position=toolbar_position
    )

    return inline.InlineWidget(
        html=html,
        width=width,
        height=height,
        port=port or 8765,
        widget_id=widget_id,
    )


def _make_grid_export_handler(widget: Any) -> Any:
    """Create a grid_export_csv handler bound to a widget.

    Parameters
    ----------
    widget : InlineWidget
        Widget instance to emit notifications through.

    Returns
    -------
    Callable
        Handler function for grid_export_csv events.
    """

    def handle_export(data: dict[str, Any], _event_type: str, _label: str) -> None:
        csv_content = data.get("csvContent", "")
        suggested_name = data.get("fileName", "export.csv")
        export_type = data.get("exportType", "unknown")

        # Normalize line endings - AG Grid uses \r\n, convert to \n
        csv_content = csv_content.replace("\r\n", "\n").replace("\r", "\n")

        # Use current directory for exports
        save_dir = Path.cwd()

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = suggested_name.rsplit(".", 1)[0]
        filename = f"{base_name}_{timestamp}.csv"
        filepath = save_dir / filename

        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            filepath.write_text(csv_content, encoding="utf-8")
            # Show notification in the grid
            widget.emit(
                "pywry:show_notification",
                {"message": f"Saved: {filepath}", "duration": 3000},
            )
            print(f"[PyWry] CSV exported ({export_type}): {filepath}")
        except Exception as e:
            widget.emit(
                "pywry:show_notification",
                {"message": f"Export failed: {e}", "duration": 4000},
            )
            print(f"[PyWry] Failed to save CSV: {e}")

    return handle_export


def create_dataframe_widget(  # pylint: disable=too-many-branches,too-many-arguments
    row_data: list[dict],
    columns: list[str],
    widget_id: str,
    title: str = "PyWry",
    theme: str = "dark",
    aggrid_theme: str = "alpine",
    width: str = "100%",
    height: int = 500,
    header_html: str = "",
    grid_options: dict | None = None,
    buttons: list[dict] | None = None,
    toolbar_position: str = "top",
    port: int | None = None,
) -> Any:
    """Create a DataFrame/AG Grid widget using the best available backend.

    Automatically selects:
    1. PyWryAgGridWidget (anywidget) if available - best performance
    2. InlineWidget (FastAPI) as fallback - broader compatibility

    Parameters
    ----------
    row_data : list[dict]
        Table data as list of row dictionaries.
    columns : list[str]
        Column names.
    widget_id : str
        Unique widget identifier.
    title : str
        Widget title.
    theme : str
        'dark' or 'light'.
    aggrid_theme : str
        AG Grid theme name.
    width : str
        Widget width (CSS).
    height : int
        Widget height in pixels.
    header_html : str
        Custom HTML for header section.
    grid_options : dict, optional
        Custom AG Grid options.
    buttons : list[dict], optional
        List of button configs to generate a toolbar.
    toolbar_position : str
        Toolbar position ("top", "bottom", "left", "right", "inside").
    port : int, optional
        Server port (only for InlineWidget fallback).

    Returns
    -------
    BaseWidget
        Widget instance implementing BaseWidget protocol.
    """
    from . import inline
    from .templates import ThemeMode, build_toolbar_html

    # Prepare toolbar if needed
    toolbar_html = ""
    if buttons:
        mode = ThemeMode.DARK if theme == "dark" else ThemeMode.LIGHT
        toolbar_html = build_toolbar_html(buttons, mode, toolbar_position)

    # Use anywidget when available for better performance
    from .widget import HAS_ANYWIDGET

    use_anywidget = HAS_ANYWIDGET

    if use_anywidget:
        import json

        from .widget import PyWryAgGridWidget

        # NOTE: header_html is ignored effectively if we rewrite using toolbar_position logic below
        # Or we should append header_html to toolbar?
        # Ideally, flexible layout replaces simple header prepend.

        # Grid config - just the data, defaults come from aggrid-defaults.js
        grid_config = {
            "columnDefs": [{"field": col} for col in columns],
            "rowData": row_data,
            "domLayout": "normal",
        }
        # Merge/Override with provided options
        if grid_options:
            grid_config.update(grid_options)
            if "rowData" not in grid_config:
                grid_config["rowData"] = row_data

        # Construct content HTML for the widget
        grid_html = '<div id="grid" class="pywry-grid" style="height: 100%; width: 100%;"></div>'

        # Layout logic
        content_html = grid_html
        if toolbar_html:
            # NOTE: We do NOT wrap the content in a flex container for AnyWidget
            # because AnyWidget handles the container size.
            # Instead, we just stack them blocks, but give the grid correct height usage.
            # Actually, standard flex usage is safer, but we must ensure the grid div behaves.

            if toolbar_position == "bottom":
                # Fixed height for toolbar, flex-grow for grid content
                content_html = f"<div class='pywry-wrapper-bottom' style='height: 100%; display: flex; flex-direction: column;'><div class='pywry-content' style='flex: 1; min-height: 0;'>{grid_html}</div><div style='flex: 0 0 auto;'>{toolbar_html}</div></div>"
            elif toolbar_position == "top":
                content_html = f"<div class='pywry-wrapper-top' style='height: 100%; display: flex; flex-direction: column;'><div style='flex: 0 0 auto;'>{toolbar_html}</div><div class='pywry-content' style='flex: 1; min-height: 0;'>{grid_html}</div></div>"
            elif toolbar_position == "left":
                content_html = f"<div class='pywry-wrapper-left' style='height: 100%; display: flex; flex-direction: row;'><div style='flex: 0 0 auto;'>{toolbar_html}</div><div class='pywry-content' style='flex: 1; min-width: 0;'>{grid_html}</div></div>"
            elif toolbar_position == "right":
                content_html = f"<div class='pywry-wrapper-right' style='height: 100%; display: flex; flex-direction: row;'><div class='pywry-content' style='flex: 1; min-width: 0;'>{grid_html}</div><div style='flex: 0 0 auto;'>{toolbar_html}</div></div>"
            elif toolbar_position == "inside":
                # Use relative container for grid and absolute toolbar
                content_html = f"<div class='pywry-wrapper-inside' style='position: relative; height: 100%; width: 100%;'>{toolbar_html}{grid_html}</div>"

        # If header_html exists and wasn't toolbar, prepend/append?
        # User only asked to support buttons model position. header_html is legacy param here.
        if header_html and not buttons:
            # Prepend if no buttons (legacy behavior)
            content_html = f"<div style='display: flex; flex-direction: column; height: 100%; width: 100%;'>{header_html}{grid_html}</div>"

        return PyWryAgGridWidget(
            content=content_html,
            theme=theme,
            aggrid_theme=aggrid_theme,
            width=width,
            height=f"{height}px" if isinstance(height, int) else height,
            grid_config=json.dumps(grid_config),
        )

    # Fallback to InlineWidget
    # Pass buttons and toolbar_position to generate_dataframe_html - it handles layout natively
    html = inline.generate_dataframe_html(
        row_data,
        columns,
        widget_id,
        title,
        theme,
        aggrid_theme,
        header_html,
        grid_options=grid_options,
        buttons=buttons,
        toolbar_position=toolbar_position,
    )

    widget = inline.InlineWidget(
        html=html,
        width=width,
        height=height,
        port=port or 8765,
        widget_id=widget_id,
    )

    # Register grid_export_csv handler for IFrame path (mirrors anywidget behavior)
    widget.on("grid_export_csv", _make_grid_export_handler(widget))

    return widget
