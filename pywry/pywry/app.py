"""Main PyWry application class."""
# pylint: disable=too-many-lines

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
from .state_mixins import GridStateMixin, PlotlyStateMixin, ToolbarStateMixin
from .templates import build_html, build_plotly_init_script
from .window_manager import (
    BrowserMode,
    MultiWindowMode,
    NewWindowMode,
    SingleWindowMode,
    WindowModeBase,
    get_lifecycle,
)


if TYPE_CHECKING:
    from .toolbar import Toolbar
    from .widget_protocol import BaseWidget
    from .window_manager import WindowLifecycle


class PyWry(GridStateMixin, PlotlyStateMixin, ToolbarStateMixin):  # pylint: disable=too-many-public-methods
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
        super().__init__()
        self._mode_enum = mode
        self._theme = theme
        self._default_config = WindowConfig(
            title=title,
            width=width,
            height=height,
        )

        # Load settings (from env vars, config files, or defaults)
        self._settings = settings or PyWrySettings()

        # Set window close behavior before subprocess starts
        from . import runtime

        runtime.set_on_window_close(self._settings.window.on_window_close)
        # Set window mode so subprocess knows how to handle X button
        mode_map = {
            WindowMode.SINGLE_WINDOW: "single",
            WindowMode.MULTI_WINDOW: "multi",
            WindowMode.NEW_WINDOW: "new",
        }
        runtime.set_window_mode(mode_map.get(mode, "new"))

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
        if mode == WindowMode.BROWSER:
            return BrowserMode()
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

    def _setup_hot_reload_watching(
        self,
        target_label: str,
        html_content: HtmlContent,
    ) -> None:
        """Set up hot reload file watching for a window.

        Parameters
        ----------
        target_label : str
            The window label.
        html_content : HtmlContent
            The HTML content with files to watch.
        """
        lifecycle = get_lifecycle()

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

    # pylint: disable=too-many-arguments
    def show(
        self,
        content: str | HtmlContent,
        title: str | None = None,
        width: int | str | None = None,
        height: int | None = None,
        callbacks: dict[str, CallbackFunc] | None = None,
        include_plotly: bool = False,
        include_aggrid: bool = False,
        aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = "alpine",
        label: str | None = None,
        watch: bool | None = None,
        toolbars: list[dict[str, Any] | Toolbar] | None = None,
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
        width : int or str or None, optional
            Window width - int for pixels, str for CSS value (e.g., "60%", "500px").
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
        toolbars : list[dict], optional
            List of toolbar configs. Each toolbar has 'position' and 'items' keys.

        Returns
        -------
        str or PyWryWidget or InlineWidget
            The window label (native window) or widget (notebook).
        """
        # Check if we're in BROWSER mode - use inline server but open in system browser
        is_browser_mode = isinstance(self._mode, BrowserMode)

        # Check if we're in a notebook environment OR explicit BROWSER mode
        if should_use_inline_rendering() or is_browser_mode:
            # Convert HtmlContent to string if needed
            html_str = content.html if isinstance(content, HtmlContent) else content

            # Build callbacks dict from CallbackFunc to plain Callable
            plain_callbacks: dict[str, Any] | None = None
            if callbacks:
                plain_callbacks = {
                    event: (cb.func if hasattr(cb, "func") else cb)
                    for event, cb in callbacks.items()
                }

            # For BROWSER mode, use InlineWidget (IFrame + WebSocket)
            if is_browser_mode:
                from . import inline as pywry_inline

                return pywry_inline.show(
                    content=html_str,
                    title=title or self._default_config.title,
                    width="100%",
                    height=height or self._default_config.height,
                    theme="dark" if self._theme == ThemeMode.DARK else "light",
                    callbacks=plain_callbacks,
                    include_plotly=include_plotly,
                    include_aggrid=include_aggrid,
                    aggrid_theme=aggrid_theme,
                    toolbars=toolbars,
                    open_browser=True,
                )

            # For notebook inline: use PyWryWidget (AnyWidget) for plain HTML
            # Use InlineWidget only for Plotly/AG Grid (they need specialized handling)
            if include_plotly or include_aggrid:
                from . import inline as pywry_inline

                return pywry_inline.show(
                    content=html_str,
                    title=title or self._default_config.title,
                    width="100%",
                    height=height or self._default_config.height,
                    theme="dark" if self._theme == ThemeMode.DARK else "light",
                    callbacks=plain_callbacks,
                    include_plotly=include_plotly,
                    include_aggrid=include_aggrid,
                    aggrid_theme=aggrid_theme,
                    toolbars=toolbars,
                    open_browser=False,
                )

            # Plain HTML with toolbars: use PyWryWidget (AnyWidget)
            from .widget import PyWryWidget

            # Handle width - can be int (pixels), string (css value), or None
            widget_width = width
            if widget_width is None:
                widget_width = "100%"
            elif isinstance(widget_width, int):
                widget_width = f"{widget_width}px"
            # else: already a string like "60%" or "500px"

            widget = PyWryWidget.from_html(
                content=html_str,
                callbacks=plain_callbacks,
                theme="dark" if self._theme == ThemeMode.DARK else "light",
                width=widget_width,
                height=f"{height or self._default_config.height}px",
                toolbars=toolbars,
            )
            widget.display()  # Auto-display in notebook
            return widget

        # Build config - width must be int for native window
        native_width = width if isinstance(width, int) else self._default_config.width
        config = WindowConfig(
            title=title or self._default_config.title,
            width=native_width,
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
        target_label = (
            self._mode.label
            if hasattr(self._mode, "label")
            else (label or f"pywry-{uuid.uuid4().hex[:8]}")
        )

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
            toolbars=toolbars,
        )

        # Store content for refresh support
        lifecycle = get_lifecycle()
        lifecycle.store_content_for_refresh(target_label, html_content, config)

        # Enable hot reload watching if requested
        if enable_hot_reload:
            self._setup_hot_reload_watching(target_label, html_content)

        # Show in window (pass label for multi-window mode)
        label_result = self._mode.show(config, html, callbacks, target_label)

        return label_result

    def show_plotly(  # noqa: C901, PLR0912  # pylint: disable=too-many-branches
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
        toolbars: list[dict[str, Any] | Toolbar] | None = None,
        config: Any = None,
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
        toolbars : list[dict], optional
            List of toolbar configs. Each toolbar has 'position' and 'items' keys.
        config : PlotlyConfig or dict, optional
            Plotly.js configuration (modebar, responsive, etc.).

        Returns
        -------
        str or InlineWidget
            The window label (native window) or InlineWidget (notebook).
        """
        # Check if we're in BROWSER mode - use inline server but open in system browser
        is_browser_mode = isinstance(self._mode, BrowserMode)

        # Check if we're in a notebook environment OR explicit BROWSER mode
        if should_use_inline_rendering() or is_browser_mode:
            from . import inline as pywry_inline

            # Map specific callbacks to generic dict for inline
            inline_callbacks = callbacks or {}
            if on_click and "plotly_click" not in inline_callbacks:
                inline_callbacks["plotly_click"] = on_click
            if on_hover and "plotly_hover" not in inline_callbacks:
                inline_callbacks["plotly_hover"] = on_hover
            if on_select and "plotly_selected" not in inline_callbacks:
                inline_callbacks["plotly_selected"] = on_select

            widget = pywry_inline.show_plotly(
                figure=figure,
                title=title or "Plotly Chart",
                width="100%",
                height=height or self._default_config.height,
                theme="dark" if self._theme == ThemeMode.DARK else "light",
                callbacks=inline_callbacks,
                toolbars=toolbars,
                config=config,
                open_browser=is_browser_mode,  # Open in browser for BROWSER mode
            )

            return widget

        # Generate unique chart ID
        chart_id = f"chart_{uuid.uuid4().hex}"

        # Convert figure to JSON
        try:
            if isinstance(figure, dict):
                fig_dict = dict(figure)
            elif hasattr(figure, "to_plotly_json"):
                fig_dict = figure.to_plotly_json()
            elif hasattr(figure, "to_dict"):
                fig_dict = figure.to_dict()
            else:
                fig_dict = {"data": [], "layout": {}}
                warn("Figure does not have to_plotly_json or to_dict method")

            if "layout" not in fig_dict:
                fig_dict["layout"] = {}

            # Apply PlotlyConfig if provided
            if config is not None:
                if hasattr(config, "model_dump"):
                    # Pydantic model - convert to dict with camelCase aliases
                    config_dict = config.model_dump(by_alias=True, exclude_none=True)
                elif isinstance(config, dict):
                    config_dict = config
                else:
                    config_dict = {}
                fig_dict["config"] = config_dict

            # Generate HTML containing div + init script
            html_content = build_plotly_init_script(
                figure=fig_dict,
                chart_id=chart_id,
                theme=self._theme,
            )

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
            toolbars=toolbars,
        )

    def show_dataframe(  # pylint: disable=too-many-branches
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
        toolbars: list[dict[str, Any] | Toolbar] | None = None,
        inline_css: str | None = None,
        on_cell_click: Any = None,
        on_row_selected: Any = None,
        server_side: bool = False,
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
        toolbars : list[dict], optional
            List of toolbar configs. Each toolbar has 'position' and 'items' keys.
        inline_css : str or None, optional
            Custom CSS to inject (e.g., override window background).
        on_cell_click : Callable or None, optional
            Cell click callback for notebook mode.
        on_row_selected : Callable or None, optional
            Row selection callback for notebook mode.
        server_side : bool, optional
            Enable server-side mode where data stays in Python memory.
            Useful for very large datasets (>100K rows) where you want
            to filter/sort the full data. Data is fetched via IPC on
            demand. Default is False.

        Returns
        -------
        str or InlineWidget
            The window label (native window) or InlineWidget (notebook).
        """
        # Check if we're in BROWSER mode - use inline server but open in system browser
        is_browser_mode = isinstance(self._mode, BrowserMode)

        # Check if we're in a notebook environment OR explicit BROWSER mode
        if should_use_inline_rendering() or is_browser_mode:
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
                toolbars=toolbars,
                callbacks=inline_callbacks,
                open_browser=is_browser_mode,  # Open in browser for BROWSER mode
            )

        # Use unified grid config builder for column defs with type detection
        from .grid import build_column_defs, normalize_data

        # Normalize input data (handles DataFrame, dict, list)
        grid_data = normalize_data(data)
        row_data = grid_data.row_data

        # Build column defs with type detection and formatters
        if column_defs is None:
            column_defs = build_column_defs(
                grid_data.columns,
                column_types=grid_data.column_types,
            )
        else:
            # Convert ColDef objects to dicts for JSON serialization
            column_defs = [c.to_dict() if hasattr(c, "to_dict") else c for c in column_defs]

        # Build the AG Grid HTML
        # Theme class automatically includes -dark suffix for dark mode
        if self._theme == ThemeMode.DARK:
            theme_class = f"ag-theme-{aggrid_theme}-dark"
        else:
            theme_class = f"ag-theme-{aggrid_theme}"

        # Serialize user grid options for merging in JS
        user_options_json = json.dumps(grid_options or {})

        # Generate unique grid ID for this instance
        grid_id = f"app-grid-{uuid.uuid4().hex[:8]}"
        row_count = len(row_data)

        if server_side:
            # Server-side mode: data stays in Python, JS gets it via IPC
            # Useful for very large datasets where you want full filtering
            info(f"Server-side mode for {row_count:,} rows (grid: {grid_id})")

            server_config = {
                "totalRows": row_count,
                "blockSize": 500,
            }

            grid_html = f"""
        <div id="myGrid" class="pywry-grid {theme_class}" style="width:100%;height:100%;"></div>
        <script>
            (function() {{
                function initGrid() {{
                    if (typeof agGrid === 'undefined') {{
                        setTimeout(initGrid, 50);
                        return;
                    }}

                    var gridConfig = {{
                        columnDefs: {json.dumps(column_defs or [])},
                        serverSide: {json.dumps(server_config)},
                        domLayout: 'normal'
                    }};

                    var userOptions = {user_options_json};
                    if (userOptions) {{
                        Object.assign(gridConfig, userOptions);
                    }}

                    const gridDiv = document.querySelector('#myGrid');
                    if (gridDiv) {{
                        const gridId = '{grid_id}';

                        var gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS
                            ? window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId)
                            : gridConfig;

                        window.__PYWRY_GRID_API__ = agGrid.createGrid(gridDiv, gridOptions);

                        if (window.PYWRY_AGGRID_REGISTER_LISTENERS) {{
                            window.PYWRY_AGGRID_REGISTER_LISTENERS(window.__PYWRY_GRID_API__, gridDiv, gridId);
                        }}
                    }}
                }}
                initGrid();
            }})();
        </script>
        """
            # Set up IPC handler for data requests
            self._setup_server_side_handler(grid_id, row_data, label)
        else:
            # Client-side mode: send all data to frontend
            # AG Grid's DOM virtualization handles large datasets efficiently
            # JS-side truncates if > 100K rows to protect browser memory
            grid_html = f"""
        <div id="myGrid" class="pywry-grid {theme_class}" style="width:100%;height:100%;"></div>
        <script>
            (function() {{
                function initGrid() {{
                    if (typeof agGrid === 'undefined') {{
                        setTimeout(initGrid, 50);
                        return;
                    }}

                    var gridConfig = {{
                        columnDefs: {json.dumps(column_defs or [])},
                        rowData: {json.dumps(row_data)},
                        domLayout: 'normal'
                    }};

                    var userOptions = {user_options_json};
                    if (userOptions) {{
                        Object.assign(gridConfig, userOptions);
                        if (!userOptions.columnDefs) gridConfig.columnDefs = {json.dumps(column_defs or [])};
                        if (!userOptions.rowData) gridConfig.rowData = {json.dumps(row_data)};
                    }}

                    const gridDiv = document.querySelector('#myGrid');
                    if (gridDiv) {{
                        const gridId = '{grid_id}';

                        var gridOptions = window.PYWRY_AGGRID_BUILD_OPTIONS
                            ? window.PYWRY_AGGRID_BUILD_OPTIONS(gridConfig, gridId)
                            : gridConfig;

                        window.__PYWRY_GRID_API__ = agGrid.createGrid(gridDiv, gridOptions);

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
            toolbars=toolbars,
        )

    def emit(self, event_type: str, data: dict[str, Any], label: str | None = None) -> None:
        """Emit an event to the JavaScript side.

        Parameters
        ----------
        event_type : str
            Event name.
        data : dict
            Event data.
        label : str, optional
            Window label. If None, targets all active windows.
        """
        labels = [label] if label else self._mode.get_labels()

        for lbl in labels:
            self.send_event(event_type, data, label=lbl)

    def on(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
        widget_id: str | None = None,
    ) -> bool:
        """Register an event handler.

        Parameters
        ----------
        event_type : str
            Event type (namespace:event-name or * for wildcard).
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.
        widget_id : str, optional
            Widget ID to target specific component events.

        Returns
        -------
        bool
            True if registered successfully.
        """
        registry = get_registry()
        # If widget_id provided, compound the event type
        if widget_id and ":" not in event_type:
            # e.g., "plotly_click" -> "plotly_click:my_chart_id"
            event_type = f"{event_type}:{widget_id}"

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

    def on_grid(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
        grid_id: str = "*",
    ) -> bool:
        """Register an event handler for grid events.

        Convenience method that filters events to only AG Grid widgets.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "grid:cell-click", "cell_click").
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.
        grid_id : str, optional
            Grid ID to target specific grid instance (default "*" for all).

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
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(
                lbl, event_type, handler, widget_type="grid", widget_id=grid_id
            ):
                success = False
        return success

    def on_chart(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
        chart_id: str = "*",
    ) -> bool:
        """Register an event handler for chart (Plotly) events.

        Convenience method that filters events to only Plotly chart widgets.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "plotly:click", "plotly:hover").
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.
        chart_id : str, optional
            Chart ID to target specific chart instance (default "*" for all).

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
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(
                lbl, event_type, handler, widget_type="chart", widget_id=chart_id
            ):
                success = False
        return success

    def on_toolbar(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
        toolbar_id: str = "*",
    ) -> bool:
        """Register an event handler for toolbar events.

        Convenience method that filters events to only toolbar widgets.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "toolbar:change", custom button events).
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.
        toolbar_id : str, optional
            Toolbar ID to target specific toolbar (default "*" for all).

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
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(
                lbl, event_type, handler, widget_type="toolbar", widget_id=toolbar_id
            ):
                success = False
        return success

    def on_html(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
        element_id: str = "*",
    ) -> bool:
        """Register an event handler for HTML element events.

        Convenience method that filters events to HTML content.

        Parameters
        ----------
        event_type : str
            Event type (e.g., custom events from HTML elements).
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.
        element_id : str, optional
            HTML element ID to target specific element (default "*" for all).

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
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(
                lbl, event_type, handler, widget_type="html", widget_id=element_id
            ):
                success = False
        return success

    def on_window(
        self,
        event_type: str,
        handler: CallbackFunc,
        label: str | None = None,
    ) -> bool:
        """Register an event handler for window-level events.

        Convenience method that filters events to window lifecycle events.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "window:close", "window:resize").
        handler : CallbackFunc
            Callback function.
        label : str, optional
            Window label. If None, registers on all active windows.

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
            labels = ["main"]

        success = True
        for lbl in labels:
            if not registry.register(lbl, event_type, handler, widget_type="window", widget_id="*"):
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

    def show_window(self, label: str) -> bool:
        """Show a hidden window.

        Parameters
        ----------
        label : str
            Window label to show.

        Returns
        -------
        bool
            True if window was shown.
        """
        return self._mode.show_window(label)

    def hide_window(self, label: str) -> bool:
        """Hide a window (keeps it alive, just not visible).

        Parameters
        ----------
        label : str
            Window label to hide.

        Returns
        -------
        bool
            True if window was hidden.
        """
        return self._mode.hide_window(label)

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

    # Storage for server-side grid data
    _grid_data: dict[str, list[dict[str, Any]]]

    def _setup_server_side_handler(
        self,
        grid_id: str,
        row_data: list[dict[str, Any]],
        label: str | None,
    ) -> None:
        """Set up IPC handler for server-side grid data requests.

        This keeps the data in Python and sends slices on demand.

        Parameters
        ----------
        grid_id : str
            Unique grid identifier.
        row_data : list[dict[str, Any]]
            The full dataset (kept in Python memory).
        label : str or None
            Window label to register handler on.
        """
        # Initialize storage if needed
        if not hasattr(self, "_grid_data"):
            self._grid_data = {}

        # Store the data
        self._grid_data[grid_id] = row_data

        def handle_page_request(event_data: dict[str, Any]) -> None:
            """Handle grid:request-page events from frontend."""
            # Only respond to requests for this grid
            if event_data.get("gridId") != grid_id:
                return

            request_id = event_data.get("requestId", "")
            start_row = event_data.get("startRow", 0)
            end_row = event_data.get("endRow", 100)
            sort_model = event_data.get("sortModel", [])
            filter_model = event_data.get("filterModel", {})

            debug(
                f"Grid {grid_id}: page request {request_id} "
                f"rows {start_row}-{end_row}, "
                f"sort={sort_model}, filter={filter_model}"
            )

            # Get the full dataset
            data = self._grid_data.get(grid_id, [])

            # Apply filtering (simple contains/equals logic)
            filtered_data = self._apply_grid_filter(data, filter_model)

            # Apply sorting
            sorted_data = self._apply_grid_sort(filtered_data, sort_model)

            # Get the requested slice
            total_rows = len(sorted_data)
            rows = sorted_data[start_row:end_row]
            is_last_page = end_row >= total_rows

            # Add row IDs for selection persistence
            for i, row in enumerate(rows):
                row["__rowId"] = start_row + i

            # Send response back to frontend
            self.send_event(
                "grid:page-response",
                {
                    "gridId": grid_id,
                    "requestId": request_id,
                    "rows": rows,
                    "totalRows": total_rows,
                    "isLastPage": is_last_page,
                },
                label=label,
            )

        # Register the handler
        target_label = label or (self._mode.get_labels() or ["main"])[0]
        registry = get_registry()
        registry.register(target_label, "grid:request-page", handle_page_request)

        debug(f"Registered server-side handler for grid {grid_id} on label {target_label}")

    def _apply_grid_filter(
        self,
        data: list[dict[str, Any]],
        filter_model: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Apply AG Grid filter model to data.

        Parameters
        ----------
        data : list[dict[str, Any]]
            Data to filter.
        filter_model : dict[str, Any]
            AG Grid filter model.

        Returns
        -------
        list[dict[str, Any]]
            Filtered data.
        """
        if not filter_model:
            return data

        result = data
        for field, filter_def in filter_model.items():
            filter_type = filter_def.get("filterType", "text")
            filter_op = filter_def.get("type", "contains")
            filter_value = filter_def.get("filter")

            if filter_value is None:
                continue

            result = [
                row
                for row in result
                if self._row_matches_filter(row, field, filter_type, filter_op, filter_value)
            ]

        return result

    def _row_matches_filter(
        self,
        row: dict[str, Any],
        field: str,
        filter_type: str,
        filter_op: str,
        filter_value: Any,
    ) -> bool:
        """Check if a row matches a single filter condition."""
        val = row.get(field)
        if val is None:
            return False

        if filter_type == "text":
            return self._text_filter_match(val, filter_op, filter_value)

        if filter_type == "number":
            return self._number_filter_match(val, filter_op, filter_value)

        return True

    def _text_filter_match(  # noqa: PLR0911  # pylint: disable=too-many-return-statements
        self, val: Any, filter_op: str, filter_value: Any
    ) -> bool:
        """Check if value matches text filter."""
        val_str = str(val).lower()
        filter_str = str(filter_value).lower()

        if filter_op == "contains":
            return filter_str in val_str
        if filter_op == "equals":
            return val_str == filter_str
        if filter_op == "startsWith":
            return val_str.startswith(filter_str)
        if filter_op == "endsWith":
            return val_str.endswith(filter_str)
        if filter_op == "notContains":
            return filter_str not in val_str
        if filter_op == "notEqual":
            return val_str != filter_str
        return filter_str in val_str

    def _number_filter_match(  # noqa: PLR0911  # pylint: disable=too-many-return-statements
        self, val: Any, filter_op: str, filter_value: Any
    ) -> bool:
        """Check if value matches number filter."""
        try:
            num_val = float(val)
            num_filter = float(filter_value)
        except (ValueError, TypeError):
            return False

        if filter_op == "equals":
            return num_val == num_filter
        if filter_op == "notEqual":
            return num_val != num_filter
        if filter_op == "lessThan":
            return num_val < num_filter
        if filter_op == "lessThanOrEqual":
            return num_val <= num_filter
        if filter_op == "greaterThan":
            return num_val > num_filter
        if filter_op == "greaterThanOrEqual":
            return num_val >= num_filter
        return True

    def _apply_grid_sort(
        self,
        data: list[dict[str, Any]],
        sort_model: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Apply AG Grid sort model to data.

        Parameters
        ----------
        data : list[dict[str, Any]]
            Data to sort.
        sort_model : list[dict[str, Any]]
            AG Grid sort model.

        Returns
        -------
        list[dict[str, Any]]
            Sorted data.
        """
        if not sort_model:
            return data

        # Apply sorts in reverse order (last sort is primary)
        result = list(data)
        for sort_item in reversed(sort_model):
            col_id = sort_item.get("colId")
            sort_dir = sort_item.get("sort", "asc")

            if not col_id:
                continue

            # Use functools.partial or lambda with default arg to capture col_id
            result.sort(
                key=lambda row, c=col_id: self._get_sort_key(row, c),  # type: ignore[misc]
                reverse=(sort_dir == "desc"),
            )

        return result

    def _get_sort_key(self, row: dict[str, Any], col_id: str) -> tuple[int, Any]:
        """Get sort key for a row value."""
        val = row.get(col_id)
        if val is None:
            return (1, "")
        try:
            return (0, float(val))
        except (ValueError, TypeError):
            return (0, str(val).lower())

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

    def block(self, label: str | None = None) -> None:
        """Block until window(s) are closed or KeyboardInterrupt.

        This is the recommended way to keep your script running while
        windows are open. Works for all modes:

        - Native modes (NEW_WINDOW, SINGLE_WINDOW, MULTI_WINDOW): Waits for
          windows to close via the Tauri event loop.
        - BROWSER mode: Delegates to pywry.inline.block() to wait for
          browser tabs to disconnect.

        Parameters
        ----------
        label : str or None, optional
            Specific window label to wait for. If None, waits for all windows.

        Examples
        --------
        >>> app = PyWry()
        >>> label = app.show("<h1>Hello</h1>")
        >>> app.block()  # Wait until all windows are closed

        >>> # Or wait for a specific window
        >>> app.block(label)  # Wait until this specific window is closed
        """
        if isinstance(self._mode, BrowserMode):
            # Browser mode uses inline server
            from . import inline as pywry_inline

            pywry_inline.block()
        else:
            # Native mode - wait for window(s) to close
            try:
                if label:
                    # Wait for specific window to close
                    while label in self._mode.get_labels():
                        import time

                        time.sleep(0.1)
                else:
                    # Wait for all windows to close
                    while self._mode.get_labels():
                        import time

                        time.sleep(0.1)
            except KeyboardInterrupt:
                info("Interrupted, closing windows...")
                self.destroy()
