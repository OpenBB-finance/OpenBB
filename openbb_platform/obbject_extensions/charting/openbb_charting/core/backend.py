"""Backend for Plotly."""

# pylint: disable=R0915,R0917,W0613,C0415

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

    from openbb_core.app.model.charts.charting_settings import ChartingSettings
    from pandas import DataFrame
    from plotly.graph_objs import Figure


class Backend:
    """Custom backend for Plotly."""

    instance: ClassVar["Backend | None"] = None

    def __new__(cls, *args, **kwargs):
        """Create or return the singleton Backend instance."""
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, charting_settings: "ChartingSettings"):
        """Initialize the Backend."""

        self._pending_query = ""
        self._original_df: DataFrame | None = None
        self.charting_settings = charting_settings
        chart_style = getattr(charting_settings, "chart_style", "dark")
        self._is_dark = chart_style != "light"

        try:
            from pywry import (
                PyWry,
                ThemeMode,
            )  # pylint: disable=import-outside-toplevel

            theme = ThemeMode.LIGHT if chart_style == "light" else ThemeMode.DARK
            self._app = PyWry(
                title="Open Data Platform by OpenBB",
                width=1400,
                height=762,
                theme=theme,
            )
        except ImportError:
            from .dummy_backend import (
                DummyBackend,
            )  # pylint: disable=import-outside-toplevel

            self._app = DummyBackend()

        self._template_dark, self._template_light = self._register_templates()
        self._current_fig = None

    @staticmethod
    def _register_templates() -> tuple[dict, dict]:
        """Bake OpenBB styles into plotly_dark/plotly_white and return the raw dicts."""
        import plotly.graph_objects as go  # pylint: disable=import-outside-toplevel
        import plotly.io as pio  # pylint: disable=import-outside-toplevel

        from openbb_charting.core.chart_style import (
            ChartStyle,
        )  # pylint: disable=import-outside-toplevel

        cs = ChartStyle()
        dark = {}
        light = {}
        for obb_name, plotly_name in [
            ("dark", "plotly_dark"),
            ("light", "plotly_white"),
        ]:
            if obb_name in cs.plt_styles_available:
                data = cs.load_json_style(cs.plt_styles_available[obb_name])
                data.pop("line", None)
                merged = go.layout.Template(pio.templates[plotly_name])
                merged.update(data)
                pio.templates[plotly_name] = merged
                if obb_name == "dark":
                    dark = data
                else:
                    light = data

        pio.templates.default = (
            f"plotly_{'dark' if cs.plt_style != 'light' else 'white'}"
        )
        return dark, light

    _SUN_SVG = (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="5"/>'
        '<line x1="12" y1="1" x2="12" y2="3"/>'
        '<line x1="12" y1="21" x2="12" y2="23"/>'
        '<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>'
        '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>'
        '<line x1="1" y1="12" x2="3" y2="12"/>'
        '<line x1="21" y1="12" x2="23" y2="12"/>'
        '<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>'
        '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
        "</svg>"
    )
    _MOON_SVG = (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>'
        "</svg>"
    )
    _ODP_SVG = (
        '<svg viewBox="0 0 249 9" width="249px" height="100%" xmlns="http://www.w3.org/2000/svg" fill="currentColor">'
        '<path d="M6.58831 0.0126953H0V8.0127H7.53062V0.0126953H6.58943H6.58831ZM6.58831 1.51307V7.01284H0.940066V1.01255'
        'H6.58831V1.51307Z"/>'
        '<path d="M20.5331 0.018648H13.5306V8.0127H14.531V5.01418H21.5335V0.0126953H20.5331V0.018648ZM20.5331 1.51791V4.0'
        '1865H14.531V1.01776H20.5331V1.51791Z"/>'
        '<path d="M34.4889 0.0438232H34.4865H33.9915H33.4954H32.9981H32.502H32.0046H31.5085H31.0112H30.5151H30.0177H29.52'
        "16H29.0243H28.5281H28.0308H27.5335V0.540518V1.03603V1.53154V2.02824V2.52493V3.02044V3.51714V4.01265V4.50935V5.00"
        "486V5.50155V5.99707V6.49376V6.99045V7.48597V7.98148H28.0308H28.5281H29.0243H29.5216H30.0177H30.5151H31.0112H31.5"
        "085H32.0046H32.502H32.9981H33.4954H33.9915H34.4865H34.4889H34.9838H35.4799V7.48597V6.99045H34.9838H34.4889H34.48"
        "65H33.9915H33.4954H32.9981H32.502H32.0046H31.5085H31.0112H30.5151H30.0177H29.5216H29.0243H28.5281V6.49376V5.9970"
        "7V5.50155V5.00486H29.0243H29.5216H30.0177H30.5151H31.0112H31.5085H32.0046H32.502H32.9957H32.9981H33.493H33.9892H"
        "34.4865V4.50935V4.01265H33.9892H33.493H32.9981H32.9957H32.502H32.0046H31.5085H31.0112H30.5151H30.0177H29.5216H29"
        ".0243H28.5281V3.51714V3.02044V2.52493V2.02824V1.53154V1.03603H29.0243H29.5216H30.0177H30.5151H31.0112H31.5085H32"
        '.0046H32.502H32.9981H33.4954H33.9915H34.4865H34.4889H34.9838H35.4799V0.540518V0.0438232H34.9838H34.4889Z"/>'
        '<path d="M48.469 0.0246582V0.52376V1.02167V1.51959V2.01869V2.51779V3.01571V3.51481V4.01272V4.51183V5.00974V5.508'
        "84V6.00676L47.9693 5.50884L47.4708 5.00974L46.971 4.51183L46.4725 4.01272L45.9728 3.51481L45.473 3.01571L44.9745"
        " 2.51779L44.4748 2.01869L43.9762 1.51959L43.4765 1.02167L42.9779 0.52376L42.4782 0.0246582H41.9797H41.4799V0.523"
        "76V1.02167V1.51959V2.01869V2.51779V3.01571V3.51481V4.01272V4.51183V5.00974V5.50884V6.00676V6.50586V7.00496V7.502"
        "88V8.00079H41.9797H42.4782V7.50288V7.00496V6.50586V6.00676V5.50884V5.00974V4.51183V4.01272V3.51481V3.01571V2.517"
        "79V2.01869V1.51959L42.9779 2.01869L43.4765 2.51779L43.9762 3.01571L44.4748 3.51481L44.9745 4.01272L45.473 4.5118"
        "3L45.9728 5.00974L46.4725 5.50884L46.971 6.00676L47.4708 6.50586L47.9693 7.00496L48.469 7.50288L48.9676 8.00079H"
        "49.4673V7.50288V7.00496V6.50586V6.00676V5.50884V5.00974V4.51183V4.01272V3.51481V3.01571V2.51779V2.01869V1.51959V"
        '1.02167V0.52376V0.0246582H48.9676H48.469Z"/>'
        '<path d="M76.2938 0.0126953H70.1772V8.01268H76.2926L76.3183 8.0127L77.3103 7.08677V0.6053L76.2938 0.0126953ZM76.'
        '2926 1.51307V7.01283H71.1925V1.01255H76.2926V1.51307Z"/>'
        '<path d="M90.3128 0.018648H83.3103V8.0127H84.3107V5.01418H90.3128V8.0127H91.3132V0.0126953H90.3128V0.018648ZM90.'
        '3128 4.01865H84.3107V1.01776H90.3128V4.01865Z"/>'
        '<path d="M105.313 1.0293H101.822V8.0127H100.804V1.0293H97.3132V0.0126953H105.313V1.0293Z"/>'
        '<path d="M118.316 0.018648H111.313V8.0127H112.314V5.01418H118.316V8.0127H119.316V0.0126953H118.316V0.018648ZM118'
        '.316 4.01865H112.314V1.01776H118.316V4.01865Z"/>'
        '<path d="M147.029 0.00692926H140.026V8.00098H141.026V5.00247H148.029V0.000976562H147.029V0.00692926ZM147.029 1.5'
        '0619V4.00693H141.026V1.00604H147.029V1.50619Z"/>'
        '<path d="M154.538 0.0253906H155.555V7.14403H161.657V8.02539H154.538V0.0253906Z"/>'
        '<path d="M175.091 0.00692926H168.089V8.00098H169.089V5.00247H175.091V8.00098H176.091V0.000976562H175.091V0.00692'
        '926ZM175.091 4.00693H169.089V1.00604H175.091V4.00693Z"/>'
        '<path d="M190.601 1.04199H187.11V8.02539H186.092V1.04199H182.601V0.0253906H190.601V1.04199Z"/>'
        '<path d="M204.093 0.0253906H204.096H204.594H205.094V0.525986V1.02539H204.594H204.096H204.093H203.594H203.094H202'
        ".593H202.093H201.592H201.092H200.591H200.091H199.589H199.089H198.588H198.088V1.52479V2.02539V2.52599V3.02539V3.5"
        "2599V4.02539H198.588H199.089H199.589H200.091H200.591H201.092H201.592H202.093H202.591H202.593H203.092H203.592H204"
        ".594V5.02539H203.592H203.092H202.593H202.591H202.093H201.592H201.092H200.591H200.091H199.589H199.089H198.588H198"
        ".088V5.52599V6.02539V6.52599V7.02658V7.64606V8.02539H197.587H197.086V7.52599V7.02658V6.52599V6.02539V5.52599V5.0"
        "2539V4.52599V4.02539V3.52599V3.02539V2.52599V2.02539V1.52479V1.02539V0.525986V0.0253906H197.587H198.088H198.588H"
        '199.089H199.589H200.091H200.591H201.092H201.592H202.093H202.593H203.094H203.594H204.093Z"/>'
        '<path d="M218.587 0.00732422H211.58V4.00732V8.00732H219.59V0.00732422H218.589H218.587ZM218.587 1.5077V7.00747H21'
        '2.58V1.00718H218.587V1.5077Z"/>'
        '<path d="M233.097 8L231.269 4.85241H232.269L234.097 8H233.097Z"/>'
        '<path d="M233.095 0.00595197H226.093V7.99902H227.094V5.00087H234.095V0H233.095V0.00595197ZM233.095 4.00546H227.0'
        '94V1.00494H233.095V4.00546Z"/>'
        '<path d="M240.607 8.02258V0.022583H241.624L244.843 3.27575L247.588 0.022583H248.604V8.02258H247.588V1.58139L245.'
        '351 4.29236H244.335L241.624 1.58139V8.02258H240.607Z"/>'
        "</svg>"
    )
    _OPENBB_SVG = (
        '<svg viewBox="0 0 255 157" width="36" height="36" fill="currentColor" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M151.404 103.189V95.2524H223.137V111.126H151.404V103.189ZM151.404 39.6893V31.7524H239.064V47.6262H151.4'
        "04V39.6893ZM247.032 15.8738H135.468V127H239.064V79.3738H151.404V63.5H255V15.8738H247.032ZM31.8726 103.189V95.252"
        "4H103.605V111.126H31.8726V103.189ZM15.9363 39.6893V31.7524H103.596V47.6262H15.9363V39.6893ZM119.532 0V15.8738H0V"
        '63.5H103.596V79.3738H15.9363V127H119.532V15.8738H135.468V0H119.532Z"/>'
        "</svg>"
    )

    def _handle_theme_toggle(self, data, event_type, label):
        import plotly.io as pio
        from pywry import ThemeMode

        from openbb_charting.core.chart_style import ChartStyle

        new_style = "light" if self._is_dark else "dark"
        self._is_dark = not self._is_dark
        self.charting_settings.chart_style = new_style

        cs = ChartStyle()
        cs.load_style(new_style)
        template_name = "plotly_dark" if new_style == "dark" else "plotly_white"
        pio.templates.default = template_name

        self._app.theme = ThemeMode.DARK if new_style == "dark" else ThemeMode.LIGHT

        if self._current_fig is not None:
            self._current_fig.update_layout(template=pio.templates[template_name])

        icon_label = "☀" if self._is_dark else "☾"
        self._app.emit("pywry:update-theme", {"theme": new_style}, label)
        self._app.emit(
            "toolbar:set-value",
            {"componentId": "theme-toggle", "label": icon_label},
            label,
        )

    def _header_toolbar(self):
        from pywry import (
            Button,
            Div,
            Toolbar,
        )  # pylint: disable=import-outside-toplevel

        icon_label = "☀" if self._is_dark else "☾"

        return Toolbar(
            position="top",
            items=[
                Div(content=self._ODP_SVG, style="display:flex;align-items:center"),
                Div(style="flex:1"),
                Button(
                    label=icon_label,
                    event="app:toggle-theme",
                    variant="icon",
                    component_id="theme-toggle",
                    style="font-size:20px",
                    description="Toggle theme",
                ),
                Div(
                    content=self._OPENBB_SVG,
                    style="display:flex;align-items:center",
                ),
            ],
            style="width:100%;padding:12px 16px 0 16px;display:flex;align-items:center;gap:20px",
        )

    def _query_toolbar(self):
        from pywry import Button, Div, TextArea, Toolbar

        return Toolbar(
            position="top",
            items=[
                Div(
                    content="<span style='font-size:12px;margin-left:10px;'>Pandas Query:</span>",
                ),
                TextArea(
                    event="query:input",
                    placeholder="e.g. df.query('close > 200').nlargest(10, 'volume')",
                    component_id="query-input",
                    rows=1,
                    cols=60,
                    min_height="30px",
                    resize="both",
                ),
                Button(
                    label="Submit",
                    event="query:submit",
                    variant="primary",
                    size="sm",
                ),
                Button(
                    label="Reset",
                    event="query:reset",
                    variant="secondary",
                    size="sm",
                ),
            ],
            style="border-bottom:1px solid var(--pywry-border-color);margin-bottom:5px;padding-bottom:10px;",
            collapsible=True,
        )

    _BLOCKED_TOKENS = (
        "import",
        "exec",
        "eval",
        "compile",
        "open",
        "__",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "os.",
        "sys.",
        "subprocess",
        "shutil",
        "pathlib",
        "breakpoint",
        "exit",
        "quit",
    )

    def _handle_query_submit(self, data, event_type, label):
        import pandas as pd
        from pywry.grid import build_column_defs, normalize_data

        query_str = self._pending_query or ""
        if not query_str.strip():
            return

        lowered = query_str.lower()
        for token in self._BLOCKED_TOKENS:
            if token in lowered:
                self._app.emit(
                    "pywry:alert",
                    {"message": f"Blocked token: '{token}'", "type": "error"},
                    label,
                )
                return

        try:
            result = eval(  # noqa: S307  # pylint: disable=W0123
                query_str,
                {"__builtins__": {}},
                {"df": self._original_df, "pd": pd},
            )
            if not isinstance(result, pd.DataFrame):
                self._app.emit(
                    "pywry:alert",
                    {"message": "Expression must return a DataFrame", "type": "error"},
                    label,
                )
                return
            include_named_index = any(name is not None for name in result.index.names)
            result_for_grid = result.reset_index() if include_named_index else result
            grid_data = normalize_data(result_for_grid)
            col_defs = build_column_defs(
                columns=grid_data.columns,
                index_columns=grid_data.index_columns,
                column_types=grid_data.column_types,
            )
            self._app.emit(
                "grid:update-columns",
                {"columnDefs": col_defs},
                label,
            )
            self._app.emit(
                "grid:update-data",
                {"data": grid_data.row_data, "strategy": "set"},
                label,
            )
        except Exception as exc:
            self._app.emit(
                "pywry:alert",
                {"message": f"Query error: {exc}", "type": "error"},
                label,
            )

    def _handle_query_input(self, data, event_type, label):
        self._pending_query = data.get("value", "")

    def _handle_query_reset(self, data, event_type, label):
        from pywry.grid import build_column_defs, normalize_data

        self._pending_query = ""
        self._app.emit(
            "toolbar:set-value",
            {"componentId": "query-input", "value": ""},
            label,
        )
        grid_data = normalize_data(self._original_df)
        col_defs = build_column_defs(
            columns=grid_data.columns,
            index_columns=grid_data.index_columns,
            column_types=grid_data.column_types,
        )
        self._app.emit(
            "grid:update-columns",
            {"columnDefs": col_defs},
            label,
        )
        self._app.emit(
            "grid:update-data",
            {"data": grid_data.row_data, "strategy": "set"},
            label,
        )
        self._app.emit(
            "grid:reset-state",
            {"hard": True},
            label,
        )

    def _callbacks(self):
        return {"app:toggle-theme": self._handle_theme_toggle}

    def _table_callbacks(self):
        return {
            "app:toggle-theme": self._handle_theme_toggle,
            "query:submit": self._handle_query_submit,
            "query:input": self._handle_query_input,
            "query:reset": self._handle_query_reset,
        }

    def send_figure(
        self,
        fig: "Figure",
        export_image: "Path | str | None" = "",
        command_location: str | None = "",
    ):
        """Send a Plotly figure to the PyWry window."""
        import re

        from pywry import PlotlyConfig

        self._current_fig = fig

        title = "Open Data Platform by OpenBB"
        fig.layout.title.text = re.sub(
            r"<[^>]*>", "", fig.layout.title.text if fig.layout.title.text else title
        )

        display_title = title + (f" - {command_location}" if command_location else "")

        self._app.show_plotly(
            figure=fig,
            title=display_title,
            config=PlotlyConfig(
                scroll_zoom=True,
                template_dark=self._template_dark or None,
                template_light=self._template_light or None,
            ),
            toolbars=[self._header_toolbar()],
            callbacks=self._callbacks(),
        )

    def send_table(
        self,
        df_table: "DataFrame",
        title: str = "",
        source: str = "",
        theme: str = "dark",
        command_location: str | None = "",
        include_query_toolbar: bool = True,
    ):
        """Send a DataFrame table to the PyWry window."""
        import re

        self._original_df = df_table.copy()
        self._pending_query = ""

        if title:
            title = re.sub(r"<[^>]*>", "", title)
            title = re.sub(r"\[\/?[a-z]+\]", "", title)

        display_title = "Open Data Platform by OpenBB" + (
            f" - {title}" if title else ""
        )

        self._app.show_dataframe(
            data=df_table,
            title=display_title,
            toolbars=[self._header_toolbar()]
            + ([self._query_toolbar()] if include_query_toolbar else []),
            callbacks=(
                self._table_callbacks() if include_query_toolbar else self._callbacks()
            ),
            grid_options={"rowSelection": False},
        )

    def send_url(
        self,
        url: str,
        title: str = "",
        width: int | None = None,
        height: int | None = None,
    ):
        """Send a URL to the PyWry window."""
        import html as html_module  # pylint: disable=import-outside-toplevel

        safe_url = html_module.escape(url, quote=True)
        content = f'<meta http-equiv="refresh" content="0;url={safe_url}">'
        display_title = "Open Data Platform by OpenBB" + (
            f" - {title}" if title else ""
        )

        self._app.show(
            content=content,
            title=display_title,
            width=width or 1400,
            height=height or 762,
            toolbars=[self._header_toolbar()],
            callbacks=self._callbacks(),
        )

    def close(self, reset: bool = False):
        """Close the PyWry window."""
        self._app.close()
