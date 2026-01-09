"""Main PyWry application class."""

from __future__ import annotations

import json
import uuid

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from .asset_loader import AssetLoader
from .assets import (
    get_aggrid_css,
    get_aggrid_js,
    get_openbb_icon,
    get_plotly_js,
)
from .callbacks import CallbackFunc, get_registry
from .config import PyWrySettings
from .hot_reload import HotReloadManager
from .log import debug, info, warn
from .models import (
    HtmlContent,
    ThemeMode,
    WindowConfig,
    WindowMode,
)
from .notebook import should_use_inline_rendering
from .runtime import refresh_window as runtime_refresh_window
from .templates import build_html
from .window_manager import (
    MultiWindowMode,
    NewWindowMode,
    SingleWindowMode,
    WindowModeBase,
    get_lifecycle,
)


if TYPE_CHECKING:
    from .widget_protocol import BaseWidget
    from .window_manager import WindowLifecycle


class PyWry:
    """Main PyWry application for displaying content in native windows.

    Supports three window modes:
    - NEW_WINDOW: Creates a new window for each show() call
    - SINGLE_WINDOW: Reuses one window, replaces content
    - MULTI_WINDOW: Multiple independent windows

    Examples
    --------
    >>> pywry = PyWry(mode=WindowMode.SINGLE_WINDOW)
    >>> pywry.show("<h1>Hello World</h1>")
    """

    def __init__(
        self,
        mode: WindowMode = WindowMode.NEW_WINDOW,
        theme: ThemeMode = ThemeMode.DARK,
        title: str = "PyWry",
        width: int = 800,
        height: int = 600,
        settings: PyWrySettings | None = None,
        hot_reload: bool = False,
    ) -> None:
        """Initialize PyWry.

        Parameters
        ----------
        mode : WindowMode, optional
            Window mode to use.
        theme : ThemeMode, optional
            Default theme mode.
        title : str, optional
            Default window title.
        width : int, optional
            Default window width.
        height : int, optional
            Default window height.
        settings : PyWrySettings or None, optional
            Configuration settings. If None, loads from env/files.
        hot_reload : bool, optional
            Enable hot reload for CSS/JS files.
        """
        self._mode_enum = mode
        self._theme = theme
        self._default_config = WindowConfig(
            title=title,
            width=width,
            height=height,
        )

        # Load settings (from env vars, config files, or defaults)
        self._settings = settings or PyWrySettings()

        # Initialize the appropriate window mode
        self._mode: WindowModeBase = self._create_mode(mode)

        # Asset loader for CSS/JS files
        self._asset_loader = AssetLoader()

        # Hot reload manager (only if enabled)
        self._hot_reload_manager: HotReloadManager | None = None
        if hot_reload or self._settings.hot_reload.enabled:
            self._hot_reload_manager = HotReloadManager(
                settings=self._settings.hot_reload,
                asset_loader=self._asset_loader,
            )
            self._hot_reload_manager.start()
            info("Hot reload enabled")

        # Cache for bundled assets
        self._plotly_js: str | None = None
        self._aggrid_js: str | None = None
        self._aggrid_css: dict[tuple[str, ThemeMode], str] = {}

        info(f"PyWry initialized with {mode.value} mode")

    def _create_mode(self, mode: WindowMode) -> WindowModeBase:
        """Create the appropriate window mode handler.

        Parameters
        ----------
        mode : WindowMode
            Window mode enum.

        Returns
        -------
        WindowModeBase
            Window mode handler instance.
        """
        if mode == WindowMode.NEW_WINDOW:
            return NewWindowMode()
        if mode == WindowMode.SINGLE_WINDOW:
            return SingleWindowMode()
        # MULTI_WINDOW
        return MultiWindowMode()

    @property
    def settings(self) -> PyWrySettings:
        """Get the current settings."""
        return self._settings

    @property
    def theme(self) -> ThemeMode:
        """Get the current theme mode."""
        return self._theme

    @theme.setter
    def theme(self, value: ThemeMode) -> None:
        """Set the theme mode."""
        self._theme = value
        debug(f"Theme changed to {value.value}")

    # pylint: disable=too-many-arguments
    def show(
        self,
        content: str | HtmlContent,
        title: str | None = None,
        width: int | None = None,
        height: int | None = None,
        callbacks: dict[str, CallbackFunc] | None = None,
        include_plotly: bool = False,
        include_aggrid: bool = False,
        aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
        label: str | None = None,
        watch: bool | None = None,
        buttons: list[dict[str, str]] | None = None,
        toolbar_position: str | None = None,
    ) -> str | BaseWidget:
        """Show content in a window.

        In a notebook environment (Jupyter, IPython, Colab, etc.), this will
        automatically render content inline via IFrame instead of opening
        a native window.

        Parameters
        ----------
        content : str or HtmlContent
            HTML content or HtmlContent object.
        title : str or None, optional
            Window title (overrides default).
        width : int or None, optional
            Window width (overrides default).
        height : int or None, optional
            Window height (overrides default).
        callbacks : dict[str, CallbackFunc] or None, optional
            Event callbacks (event_type -> handler).
        include_plotly : bool, optional
            Include Plotly.js library.
        include_aggrid : bool, optional
            Include AG Grid library.
        aggrid_theme : {'quartz', 'alpine', 'balham', 'material'}, optional
            AG Grid theme name (default: 'alpine').
        label : str or None, optional
            Window label (for MULTI_WINDOW mode updates).
        watch : bool or None, optional
            Enable hot reload for CSS/JS files (overrides HtmlContent.watch).
        buttons : list[dict[str, str]] or None, optional
            List of button configs to generate a toolbar.

        Returns
        -------
        str or InlineWidget
            The window label (native window) or InlineWidget (notebook).
        """
        # Resolve toolbar position from args or settings
        toolbar_pos = toolbar_position or self._settings.window.toolbar_position

        # Check if we're in a notebook environment
        if should_use_inline_rendering():
            from . import inline as pywry_inline

            # Convert HtmlContent to string if needed
            html_str = content.html if isinstance(content, HtmlContent) else content

            # Build callbacks dict from CallbackFunc to plain Callable
            inline_callbacks: dict[str, Any] | None = None
            if callbacks:
                inline_callbacks = {
                    event: (cb.func if hasattr(cb, "func") else cb)
                    for event, cb in callbacks.items()
                }

            return pywry_inline.show(
                content=html_str,
                title=title or self._default_config.title,
                width="100%",
                height=height or self._default_config.height,
                theme="dark" if self._theme == ThemeMode.DARK else "light",
                callbacks=inline_callbacks,
                include_plotly=include_plotly,
                include_aggrid=include_aggrid,
                aggrid_theme=aggrid_theme,
                buttons=buttons,
                toolbar_position=toolbar_pos,
            )

        # Build config
        config = WindowConfig(
            title=title or self._default_config.title,
            width=width or self._default_config.width,
            height=height or self._default_config.height,
            theme=self._theme,
            enable_plotly=include_plotly,
            enable_aggrid=include_aggrid,
            aggrid_theme=aggrid_theme,
        )

        # Build HtmlContent from string if needed
        html_content = content if isinstance(content, HtmlContent) else HtmlContent(html=content)

        # Get window label - for SINGLE_WINDOW mode, use the mode's fixed label
        # For other modes, let the mode's show() generate unique label if not provided
        if hasattr(self._mode, "label"):
            target_label = self._mode.label
        else:
            target_label = label if label else f"pywry-{uuid.uuid4().hex[:8]}"

        # Determine if hot reload should be enabled for this window
        should_watch = watch if watch is not None else html_content.watch
        enable_hot_reload = should_watch and self._hot_reload_manager is not None

        # Build HTML using templates with settings
        html = build_html(
            content=html_content,
            config=config,
            window_label=target_label,
            settings=self._settings,
            loader=self._asset_loader,
            enable_hot_reload=enable_hot_reload,
            buttons=buttons,
            toolbar_position=toolbar_pos,
        )

        # Store content for refresh support
        lifecycle = get_lifecycle()
        lifecycle.store_content_for_refresh(target_label, html_content, config)

        # Enable hot reload watching if requested
        if enable_hot_reload:
            if html_content.css_files:
                for css_file in html_content.css_files:
                    css_path = Path(css_file) if isinstance(css_file, str) else css_file
                    lifecycle.add_watched_file(target_label, css_path, "css")

            if html_content.script_files:
                for script_file in html_content.script_files:
                    script_path = Path(script_file) if isinstance(script_file, str) else script_file
                    lifecycle.add_watched_file(target_label, script_path, "js")

            watch_content = html_content

            if not html_content.watch:
                watch_content = HtmlContent(
                    html=html_content.html,
                    json_data=html_content.json_data,
                    init_script=html_content.init_script,
                    css_files=html_content.css_files,
                    script_files=html_content.script_files,
                    inline_css=html_content.inline_css,
                    watch=True,
                )

            if self._hot_reload_manager:
                self._hot_reload_manager.enable_for_window(target_label, watch_content)

            debug(f"Hot reload enabled for window {target_label}")

        # Show in window (pass label for multi-window mode)
        return self._mode.show(config, html, callbacks, target_label)

    def show_plotly(  # noqa: PLR0912  # pylint: disable=too-many-branches
        self,
        figure: Any,
        title: str | None = None,
        width: int | None = None,
        height: int | None = None,
        callbacks: dict[str, CallbackFunc] | None = None,
        label: str | None = None,
        inline_css: str | None = None,
        on_click: Any = None,
        on_hover: Any = None,
        on_select: Any = None,
        buttons: list[dict[str, str]] | None = None,
        toolbar_position: str | None = None,
    ) -> str | BaseWidget:
        """Show a Plotly figure.

        In a notebook environment, this will automatically render the figure
        inline via IFrame with full interactivity.

        Parameters
        ----------
        figure : Any
            Plotly figure object (must have to_html method) or dictionary spec.
        title : str or None, optional
            Window title.
        width : int or None, optional
            Window/IFrame width (overrides default).
        height : int or None, optional
            Window/IFrame height (overrides default).
        callbacks : dict[str, CallbackFunc] or None, optional
            Event callbacks.
        label : str or None, optional
            Window label (for MULTI_WINDOW mode).
        inline_css : str or None, optional
            Custom CSS to inject (e.g., override window background).
        on_click : Callable or None, optional
            Click callback for notebook mode.
        on_hover : Callable or None, optional
            Hover callback for notebook mode.
        on_select : Callable or None, optional
            Selection callback for notebook mode.
        buttons : list[dict[str, str]] or None, optional
            List of button configs to generate a toolbar.
        toolbar_position : str or None
            Toolbar position ("top", "bottom", "left", "right", "inside").

        Returns
        -------
        str or InlineWidget
            The window label (native window) or InlineWidget (notebook).
        """
        # Resolve toolbar position from args or settings
        toolbar_pos = toolbar_position or self._settings.window.toolbar_position

        # Check if we're in a notebook environment
        if should_use_inline_rendering():
            from . import inline as pywry_inline

            # Map specific callbacks to generic dict for inline
            inline_callbacks = callbacks or {}
            if on_click and "plotly_click" not in inline_callbacks:
                inline_callbacks["plotly_click"] = on_click
            if on_hover and "plotly_hover" not in inline_callbacks:
                inline_callbacks["plotly_hover"] = on_hover
            if on_select and "plotly_selected" not in inline_callbacks:
                inline_callbacks["plotly_selected"] = on_select

            return pywry_inline.show_plotly(
                figure=figure,
                title=title or "Plotly Chart",
                width="100%",
                height=height or self._default_config.height,
                theme="dark" if self._theme == ThemeMode.DARK else "light",
                callbacks=inline_callbacks,
                buttons=buttons,
                toolbar_position=toolbar_pos,
            )

        plotly_template = "plotly_dark" if self._theme == ThemeMode.DARK else "plotly_white"

        if isinstance(figure, dict):
            fig_dict = dict(figure)  # Make a copy
            if "layout" not in fig_dict:
                fig_dict["layout"] = {}
            fig_json = json.dumps(fig_dict)
            html_content = f"""
            <div id="plotly-chart" class="plotly-graph-div" style="height: 100%; width: 100%;"></div>
            <script>
                if (typeof Plotly === 'undefined') {{
                    console.error("Plotly.js not loaded");
                }} else {{
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
                    Plotly.newPlot('plotly-chart', figData.data || [], figData.layout, figData.config);
                    // Store on the element for test verification
                    var chartEl = document.getElementById('plotly-chart');
                    chartEl.__pywry_theme_template__ = themeTemplate;
                    window.__PYWRY_PLOTLY_DIV__ = chartEl;
                    window.addEventListener('resize', function() {{
                        Plotly.Plots.resize('plotly-chart');
                    }});
                }}
            </script>
            """
        else:
            # Handle Plotly Figure objects - convert to JSON spec and use same logic
            try:
                if hasattr(figure, "to_plotly_json"):
                    fig_dict = figure.to_plotly_json()
                elif hasattr(figure, "to_dict"):
                    fig_dict = figure.to_dict()
                else:
                    # Fallback: try direct serialization
                    fig_dict = {"data": [], "layout": {}}
                    warn("Figure does not have to_plotly_json or to_dict method")

                if "layout" not in fig_dict:
                    fig_dict["layout"] = {}

                fig_json = json.dumps(fig_dict)

                html_content = f"""
            <div id="plotly-chart" class="plotly-graph-div" data-pywry-chart style="height: 100%; width: 100%;"></div>
            <script>
                if (typeof Plotly === 'undefined') {{
                    console.error("Plotly.js not loaded");
                }} else {{
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
                    Plotly.newPlot('plotly-chart', figData.data || [], figData.layout, figData.config);
                    var chartEl = document.getElementById('plotly-chart');
                    window.__PYWRY_PLOTLY_DIV__ = chartEl;
                    window.addEventListener('resize', function() {{
                        Plotly.Plots.resize('plotly-chart');
                    }});
                }}
            </script>
            """
            except Exception as e:
                warn(f"Failed to convert figure: {e}")
                html_content = f"<pre>Error: {e}</pre>"

        # Wrap in HtmlContent if inline_css provided
        content: str | HtmlContent
        if inline_css:
            content = HtmlContent(html=html_content, inline_css=inline_css)
        else:
            content = html_content

        return self.show(
            content=content,
            title=title or "Plotly Chart",
            width=width,
            height=height,
            callbacks=callbacks,
            include_plotly=True,
            label=label,
            buttons=buttons,
            toolbar_position=toolbar_pos,
        )

    def show_dataframe(
        self,
        data: Any,
        title: str | None = None,
        width: int | None = None,
        height: int | None = None,
        callbacks: dict[str, CallbackFunc] | None = None,
        label: str | None = None,
        column_defs: list[dict[str, Any]] | None = None,
        aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
        grid_options: dict[str, Any] | None = None,
        buttons: list[dict[str, str]] | None = None,
        inline_css: str | None = None,
        on_cell_click: Any = None,
        on_row_selected: Any = None,
        toolbar_position: str | None = None,
    ) -> str | BaseWidget:
        """Show a DataFrame in an AG Grid table.

        In a notebook environment, this will automatically render the table
        inline via IFrame with full interactivity.

        Parameters
        ----------
        data : Any
            DataFrame or list of dicts to display.
        title : str or None, optional
            Window title.
        width : int or None, optional
            Window/IFrame width (overrides default).
        height : int or None, optional
            Window/IFrame height (overrides default).
        callbacks : dict[str, CallbackFunc] or None, optional
            Event callbacks.
        label : str or None, optional
            Window label (for MULTI_WINDOW mode).
        column_defs : list[dict[str, Any]] or None, optional
            AG Grid column definitions.
        aggrid_theme : {'quartz', 'alpine', 'balham', 'material'}, optional
            AG Grid theme.
        grid_options : dict[str, Any] or None, optional
            Custom AG Grid options to merge with defaults.
        buttons : list[dict[str, str]] or None, optional
             List of button configs to generate a toolbar.
        inline_css : str or None, optional
            Custom CSS to inject (e.g., override window background).
        on_cell_click : Callable or None, optional
            Cell click callback for notebook mode.
        on_row_selected : Callable or None, optional
            Row selection callback for notebook mode.

        Returns
        -------
        str or InlineWidget
            The window label (native window) or InlineWidget (notebook).
        """
        # Resolve toolbar position from args or settings
        toolbar_pos = toolbar_position or self._settings.window.toolbar_position

        # Check if we're in a notebook environment
        if should_use_inline_rendering():
            from . import inline as pywry_inline

            # Map specific callbacks to generic dict for inline
            inline_callbacks = callbacks or {}
            if on_cell_click and "cell_click" not in inline_callbacks:
                inline_callbacks["cell_click"] = on_cell_click
            if on_row_selected and "row_selected" not in inline_callbacks:
                inline_callbacks["row_selected"] = on_row_selected

            return pywry_inline.show_dataframe(
                df=data,
                title=title or "Data Table",
                width="100%",
                height=height or self._default_config.height,
                theme="dark" if self._theme == ThemeMode.DARK else "light",
                aggrid_theme=aggrid_theme,
                buttons=buttons,
                callbacks=inline_callbacks,
                toolbar_position=toolbar_pos,
            )

        # Convert to list of dicts if DataFrame or column-oriented dict
        try:
            if hasattr(data, "to_dict"):
                row_data = data.to_dict("records")
            elif isinstance(data, dict):
                # Check if it's column-oriented (dict of lists) or already list of dicts
                first_value = next(iter(data.values()), None)
                if isinstance(first_value, (list, tuple)):
                    keys = list(data.keys())
                    num_rows = len(first_value)
                    row_data = [{key: data[key][i] for key in keys} for i in range(num_rows)]
                else:
                    row_data = [data]
            else:
                row_data = list(data)
        except (ValueError, TypeError) as e:
            warn(f"Failed to convert data: {e}")
            row_data = []

        # Auto-generate column defs if not provided
        if column_defs is None and row_data:
            column_defs = [{"field": key} for key in row_data[0]]

        # Build the AG Grid HTML
        # Theme class automatically includes -dark suffix for dark mode
        if self._theme == ThemeMode.DARK:
            theme_class = f"ag-theme-{aggrid_theme}-dark"
        else:
            theme_class = f"ag-theme-{aggrid_theme}"

        # Serialize user grid options for merging in JS
        user_options_json = json.dumps(grid_options or {})

        grid_html = f"""
        <div id="myGrid" class="pywry-grid {theme_class}" style="width:100%;height:100%;"></div>
        <script>
            (function() {{
                function initGrid() {{
                    if (typeof agGrid === 'undefined') {{
                        setTimeout(initGrid, 50);
                        return;
                    }}

                    // Grid config - centralized defaults handle everything else
                    var gridConfig = {{
                        columnDefs: {json.dumps(column_defs or [])},
                        rowData: {json.dumps(row_data)}
                    }};

                    // Merge user options on top of base config
                    var userOptions = {user_options_json};
                    if (userOptions) {{
                        Object.assign(gridConfig, userOptions);
                        // Preserve columnDefs and rowData if user didn't override
                        if (!userOptions.columnDefs) gridConfig.columnDefs = {json.dumps(column_defs or [])};
                        if (!userOptions.rowData) gridConfig.rowData = {json.dumps(row_data)};
                    }}

                    const gridDiv = document.querySelector('#myGrid');
                    if (gridDiv) {{
                        const gridId = 'app-grid-' + Math.random().toString(36).substr(2, 9);

                        // Use centralized AG Grid defaults from aggrid-defaults.js
                        var gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS
                            ? window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId)
                            : gridConfig;

                        window.__PYWRY_GRID_API__ = agGrid.createGrid(gridDiv, gridOptions);

                        // Register event listeners + context menu using centralized function
                        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
                            window.PYWRY_AGGRID_REGISTER_LISTENERS(window.__PYWRY_GRID_API__, gridDiv, gridId);
                        }}
                    }}
                }}
                initGrid();
            }})();
        </script>
        """

        # Wrap in HtmlContent if inline_css provided
        content = HtmlContent(html=grid_html, inline_css=inline_css) if inline_css else grid_html

        return self.show(
            content=content,
            title=title or "Data Table",
            width=width,
            height=height,
            callbacks=callbacks,
            include_aggrid=True,
            aggrid_theme=aggrid_theme,
            label=label,
            buttons=buttons,
            toolbar_position=toolbar_pos,
        )

    def on(self, event_type: str, handler: CallbackFunc, label: str | None = None) -> bool:
        """Register an event handler.

        Parameters
        ----------
        event_type : str
            Event type (namespace:event-name or * for wildcard).
        handler : CallbackFunc
            Callback function.
        label : str or None, optional
            Window label (required for NEW_WINDOW mode).

        Returns
        -------
        bool
            True if registered successfully.
        """
        registry = get_registry()
        labels = self._mode.get_labels()

        if label:
            labels = [label]
        elif not labels:
            # No windows yet - register on "main" which will be created later
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(lbl, event_type, handler):
                success = False

        return success

    def send_event(
        self,
        event_type: str,
        data: Any,
        label: str | None = None,
    ) -> bool:
        """Send an event to window(s).

        Parameters
        ----------
        event_type : str
            Event type (namespace:event-name).
        data : Any
            Event data.
        label : str or None, optional
            Specific window label (None = all windows).

        Returns
        -------
        bool
            True if event was sent to at least one window.
        """
        if label:
            return self._mode.send_event(label, event_type, data)

        # Send to all windows
        labels = self._mode.get_labels()
        if not labels:
            return False

        success = False
        for lbl in labels:
            if self._mode.send_event(lbl, event_type, data):
                success = True

        return success

    def update_content(self, html: str, label: str | None = None) -> bool:
        """Update window content.

        Parameters
        ----------
        html : str
            New HTML content.
        label : str or None, optional
            Window label (required for NEW_WINDOW/MULTI_WINDOW).

        Returns
        -------
        bool
            True if updated successfully.
        """
        theme_str = "dark" if self._theme.value in ("dark", "system") else "light"

        if label:
            return self._mode.update_content(label, html, theme_str)

        # For SINGLE_WINDOW mode, update the main window
        labels = self._mode.get_labels()
        if labels:
            return self._mode.update_content(labels[0], html, theme_str)

        return False

    def eval_js(self, script: str, label: str | None = None) -> bool:
        """Evaluate JavaScript in a window without replacing content.

        This is useful for DOM queries and dynamic updates that
        should not replace the window content.

        Parameters
        ----------
        script : str
            JavaScript code to execute.
        label : str or None, optional
            Window label (None = main window in SINGLE_WINDOW mode).

        Returns
        -------
        bool
            True if command was sent.
        """
        from . import runtime

        if label is None:
            labels = self._mode.get_labels()
            if not labels:
                return False
            label = labels[0]

        return runtime.eval_js(label, script)

    def close(self, label: str | None = None) -> bool:
        """Close window(s).

        Parameters
        ----------
        label : str or None, optional
            Window label to close (None = close all).

        Returns
        -------
        bool
            True if any window was closed.
        """
        if label:
            return self._mode.close(label)

        return self._mode.close_all() > 0

    def get_labels(self) -> list[str]:
        """Get all active window labels.

        Returns
        -------
        list of str
            List of window labels.
        """
        return self._mode.get_labels()

    def is_open(self, label: str | None = None) -> bool:
        """Check if window(s) are open.

        Parameters
        ----------
        label : str or None, optional
            Specific window to check (None = any window).

        Returns
        -------
        bool
            True if window(s) are open.
        """
        if label:
            return self._mode.is_open(label)
        return len(self._mode.get_labels()) > 0

    def refresh(self, label: str | None = None) -> bool:
        """Refresh window content.

        Triggers a full page refresh while preserving scroll position.

        Parameters
        ----------
        label : str or None, optional
            Specific window to refresh (None = all windows).

        Returns
        -------
        bool
            True if at least one window was refreshed.
        """
        if label:
            return runtime_refresh_window(label)

        # Refresh all windows
        labels = self._mode.get_labels()
        if not labels:
            return False

        success = False
        for lbl in labels:
            if runtime_refresh_window(lbl):
                success = True

        return success

    def refresh_css(self, label: str | None = None) -> bool:
        """Hot-reload CSS files for window(s).

        Re-injects CSS files without page refresh.

        Parameters
        ----------
        label : str or None, optional
            Specific window to refresh CSS (None = all windows).

        Returns
        -------
        bool
            True if at least one window's CSS was refreshed.
        """
        if not self._hot_reload_manager:
            warn("Hot reload not enabled. Initialize PyWry with hot_reload=True")
            return False

        if label:
            return self._hot_reload_manager.reload_css(label)

        # Refresh CSS for all windows
        labels = self._mode.get_labels()
        if not labels:
            return False

        success = False
        for lbl in labels:
            if self._hot_reload_manager.reload_css(lbl):
                success = True

        return success

    def enable_hot_reload(self) -> None:
        """Enable hot reload if not already enabled."""
        if self._hot_reload_manager is None:
            self._hot_reload_manager = HotReloadManager(
                settings=self._settings.hot_reload,
                asset_loader=self._asset_loader,
            )
            self._hot_reload_manager.start()
            info("Hot reload enabled")

    def disable_hot_reload(self) -> None:
        """Disable hot reload and stop file watching."""
        if self._hot_reload_manager:
            self._hot_reload_manager.stop()
            self._hot_reload_manager = None
            info("Hot reload disabled")

    def _get_plotly_js(self) -> str:
        """Get Plotly.js library (lazy loaded)."""
        if self._plotly_js is None:
            self._plotly_js = get_plotly_js()
        return self._plotly_js

    def _get_aggrid_js(self) -> str:
        """Get AG Grid JS library (lazy loaded)."""
        if self._aggrid_js is None:
            self._aggrid_js = get_aggrid_js()
        return self._aggrid_js

    def _get_aggrid_css(self) -> str:
        """Get AG Grid CSS for current theme (lazy loaded)."""
        theme_key = ("alpine", self._theme)
        if theme_key not in self._aggrid_css:
            self._aggrid_css[theme_key] = get_aggrid_css("alpine", self._theme)
        return self._aggrid_css[theme_key]

    def get_icon(self) -> bytes:
        """Get the OpenBB icon.

        Returns
        -------
        bytes
            Icon bytes.
        """
        return get_openbb_icon()

    def get_lifecycle(self) -> WindowLifecycle:
        """Get the window lifecycle manager.

        Returns
        -------
        WindowLifecycle
            WindowLifecycle instance.
        """
        return get_lifecycle()

    def destroy(self) -> None:
        """Destroy all resources and close all windows."""
        info("Destroying PyWry")

        # Stop hot reload if active
        if self._hot_reload_manager:
            self._hot_reload_manager.stop()
            self._hot_reload_manager = None

        self._mode.close_all()
        get_lifecycle().destroy_all()
        self._plotly_js = None
        self._aggrid_js = None
        self._aggrid_css.clear()
        self._asset_loader.clear_cache()
