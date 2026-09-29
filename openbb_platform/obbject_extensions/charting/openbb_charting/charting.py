"""Charting Class implementation."""

from __future__ import annotations

from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
)
from warnings import warn

from importlib_metadata import entry_points
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.helpers import (
    get_charting_functions,
    get_charting_functions_list,
)

if TYPE_CHECKING:
    from numpy import ndarray
    from pandas import DataFrame, Series
    from plotly.graph_objs import Figure

    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_charting.query_params import ChartParams

CHARTING_EXTENSION_GROUP = "openbb_charting_extension"


class Charting:
    """Charting extension."""

    _extension_views_cache: ClassVar[list[type] | None] = None
    _format = "plotly"

    def __init__(self, obbject):
        """Initialize Charting extension."""
        import importlib

        from openbb_core.app.charting import get_hooks_manager

        charting_settings_module = importlib.import_module(
            "openbb_core.app.model.charts.charting_settings", "ChartingSettings"
        )
        ChartingSettings = charting_settings_module.ChartingSettings

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,
            system_settings=self._obbject._system_settings,
        )
        self._backend = self.get_backend_class()(self._charting_settings)
        self._hooks = get_hooks_manager()
        self._functions: dict[str, Callable] = self._get_functions()

    @classmethod
    def _get_extension_views(cls) -> list[type]:
        """Discover and cache the registered charting view classes."""
        if cls._extension_views_cache is None:
            cls._extension_views_cache = [
                entry_point.load()
                for entry_point in entry_points(group=CHARTING_EXTENSION_GROUP)
            ]
        return cls._extension_views_cache

    @classmethod
    def get_backend_class(cls) -> type:
        """Return the rendering backend class for this engine."""
        from openbb_core.app.charting import get_charting_backend_class

        from openbb_charting.core.backend import Backend

        return get_charting_backend_class() or Backend

    @classmethod
    def get_figure_class(cls) -> type:
        """Return the figure class this engine produces."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        return OpenBBFigure

    @classmethod
    def indicators(cls):
        """Return an instance of the IndicatorsParams class, containing all available indicators and their parameters."""
        from openbb_charting.query_params import IndicatorsParams

        return IndicatorsParams()

    @classmethod
    def functions(cls) -> list[str]:
        """Return a list of the available functions."""
        functions: list[str] = []
        for view in cls._get_extension_views():
            functions.extend(get_charting_functions_list(view))

        return functions

    def _get_functions(self) -> dict[str, Callable]:
        """Return a dict with the available functions."""
        functions: dict[str, Callable] = {}
        for view in self._get_extension_views():
            functions.update(get_charting_functions(view))

        return functions

    def _get_chart_function(self, route: str) -> Callable:
        """Given a route, it returns the chart function. The module must contain the given route."""
        if route is None:
            raise ValueError("OBBject was initialized with no function route.")
        adjusted_route = route.replace("/", "_")[1:]
        if adjusted_route not in self._functions:
            raise ValueError(
                f"Could not find the route `{adjusted_route}` in the charting functions."
            )
        return self._functions[adjusted_route]

    def _make_hook_context(self, stage, **overrides):
        """Build a :class:`HookContext` for the bound OBBject."""
        from openbb_core.app.charting import HookContext

        context = HookContext(
            route=self._obbject._route or "",
            stage=stage,
            data=self._obbject.results,
            settings=self._charting_settings,
            standard_params=self._obbject._standard_params or {},
            extra_params=self._obbject._extra_params or {},
            provider=self._obbject.provider,
            extra=self._obbject.extra,
        )
        for key, value in overrides.items():
            setattr(context, key, value)
        return context

    def _dispatch_hook(self, stage, context=None, **overrides):
        """Dispatch a lifecycle ``stage`` through the registered hooks."""
        if context is None:
            context = self._make_hook_context(stage, **overrides)
        else:
            context.stage = stage
            for key, value in overrides.items():
                setattr(context, key, value)
        return self._hooks.dispatch(stage, context)

    def get_params(self) -> ChartParams | None:
        """Return the ChartQueryParams class for the function the OBBject was created from."""
        from openbb_charting.query_params import ChartParams

        if self._obbject._route is None:
            raise ValueError("OBBject was initialized with no function route.")
        charting_function = (self._obbject._route).replace("/", "_")[1:]
        if hasattr(ChartParams, charting_function):
            return getattr(ChartParams, charting_function)()

        return help(self._get_chart_function(self._obbject.extra["metadata"].route))

    def _prepare_data_as_df(
        self, data: DataFrame | Series | None
    ) -> tuple[DataFrame, bool]:
        """Convert supplied data to a DataFrame."""
        from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
        from pandas import DataFrame, Series

        has_data = (isinstance(data, (Data, DataFrame, Series)) and not data.empty) or (
            bool(data)
        )
        index = (
            data.index.name
            if has_data and isinstance(data, (DataFrame, Series))
            else None
        )
        data_as_df: DataFrame = (
            basemodel_to_df(convert_to_basemodel(data), index=index)  # ty: ignore[invalid-argument-type]
            if has_data
            else self._obbject.to_dataframe(index=index)  # ty: ignore[invalid-argument-type]
        )
        if "date" in data_as_df.columns:
            data_as_df = data_as_df.set_index("date")
        if "provider" in data_as_df.columns:
            data_as_df.drop(columns="provider", inplace=True)
        return data_as_df, has_data

    def create_line_chart(
        self,
        data: (
            list
            | dict
            | DataFrame
            | list[DataFrame]
            | Series
            | list[Series]
            | ndarray
            | Data
        ),
        index: str | None = None,
        target: str | None = None,
        title: str | None = None,
        x: str | None = None,
        xtitle: str | None = None,
        y: str | list[str] | None = None,
        ytitle: str | None = None,
        y2: str | list[str] | None = None,
        y2title: str | None = None,
        layout_kwargs: dict | None = None,
        scatter_kwargs: dict | None = None,
        normalize: bool = False,
        returns: bool = False,
        same_axis: bool = False,
        render: bool = True,
        **kwargs,
    ) -> OpenBBFigure | Figure | None:
        """Create a line chart from external data and render a chart or return the OpenBBFigure.

        Parameters
        ----------
        data : Data | DataFrame | Series
            Data to be plotted (OHLCV data).
        index : str | None, optional
            Index column, by default None
        target : str | None, optional
            Target column to be plotted, by default None
        title : str | None, optional
            Chart title, by default None
        x : str | None, optional
            X-axis column, by default None
        xtitle : str | None, optional
            X-axis title, by default None
        y : str | list[str] | None, optional
            Y-axis column(s), by default None
            If None are supplied, the layout is optimized for the contents of data.
            Where many units/scales are present,
            it will attempt to divide based on the range of values.
        ytitle : str | None, optional
            Y-axis title, by default None
        y2 : str | list[str] | None, optional
            Y2-axis column(s), by default None
        y2title : str | None, optional
            Y2-axis title, by default None
        layout_kwargs : dict | None, optional
            Additional Plotly Layout parameters for `fig.update_layout`, by default None
        scatter_kwargs : dict | None, optional
            Additional Plotly parameters applied on creation of each scatter plot, by default None
        normalize : bool, optional
            Normalize the data with Z-Score Standardization, by default False
        returns : bool, optional
            Convert the data to cumulative returns, by default False
        same_axis: bool, optional
            If True, forces all data onto the same Y-axis, by default False
        render: bool, optional
            If True, the chart will be rendered, by default True
        **kwargs: dict[str, Any]
            Extra parameters to be passed to `figure.show()`
        """
        from openbb_charting.charts.generic_charts import line_chart

        fig = line_chart(
            data=data,
            index=index,
            target=target,
            title=title,
            x=x,
            xtitle=xtitle,
            y=y,
            ytitle=ytitle,
            y2=y2,
            y2title=y2title,
            layout_kwargs=layout_kwargs,
            scatter_kwargs=scatter_kwargs,
            normalize=normalize,
            returns=returns,
            same_axis=same_axis,
            **kwargs,
        )
        fig = self._set_chart_style(fig)
        if render:
            fig.show(**kwargs)

        return fig

    def create_bar_chart(
        self,
        data: (
            list
            | dict
            | DataFrame
            | list[DataFrame]
            | Series
            | list[Series]
            | ndarray
            | Data
        ),
        x: str,
        y: str | list[str],
        barmode: Literal["group", "stack", "relative", "overlay"] = "group",
        xtype: Literal[
            "category", "multicategory", "date", "log", "linear"
        ] = "category",
        title: str | None = None,
        xtitle: str | None = None,
        ytitle: str | None = None,
        orientation: Literal["h", "v"] = "v",
        colors: list[str] | None = None,
        layout_kwargs: dict[str, Any] | None = None,
        bar_kwargs: dict[str, Any] | None = None,
        render: bool = True,
        **kwargs,
    ) -> OpenBBFigure | Figure | None:
        """Create a bar chart on a single x-axis with one or more values for the y-axis.

        Parameters
        ----------
        data : list | dict | DataFrame | list[DataFrame] | Series | list[Series] | ndarray | Data
            Data to plot.
        x : str
            The x-axis column name.
        y : str | list[str]
            The y-axis column name(s).
        barmode : Literal["group", "stack", "relative", "overlay"], optional
            The bar mode, by default "group".
        xtype : Literal["category", "multicategory", "date", "log", "linear"], optional
            The x-axis type, by default "category".
        title : str, optional
            The title of the chart, by default None.
        xtitle : str, optional
            The x-axis title, by default None.
        ytitle : str, optional
            The y-axis title, by default None.
        colors: list[str], optional
            Manually set the colors to cycle through for each column in 'y', by default None.
        bar_kwargs : dict[str, Any], optional
            Additional keyword arguments to apply with figure.add_bar(), by default None.
        layout_kwargs : dict[str, Any], optional
            Additional keyword arguments to apply with figure.update_layout(), by default None.

        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """
        from openbb_charting.charts.generic_charts import bar_chart

        fig = bar_chart(
            data=data,
            x=x,
            y=y,
            barmode=barmode,
            xtype=xtype,
            title=title,
            xtitle=xtitle,
            ytitle=ytitle,
            orientation=orientation,
            colors=colors,
            bar_kwargs=bar_kwargs,
            layout_kwargs=layout_kwargs,
        )
        fig = self._set_chart_style(fig)
        if render:
            fig.show(**kwargs)

        return fig

    def create_3d_surface(
        self,
        X: Series,
        Y: Series,
        Z: Series,
        xtitle: str | None = "DTE",
        ytitle: str | None = "Strike",
        ztitle: str | None = "IV",
        colorscale: str | list | None = None,
        title: str | None = None,
        layout_kwargs: dict[str, Any] | None = None,
        theme: Literal["dark", "light"] | None = None,
    ) -> OpenBBFigure | Figure:
        """Create a 3D surface chart.

        Parameters
        ----------
        X : pd.Series
            The x-axis data.
        Y : pd.Series
            The y-axis data.
        Z : pd.Series
            The z-axis data.
        xtitle : str, optional
            The title for the x-axis, by default "DTE".
        ytitle : str, optional
            The title for the y-axis, by default "Strike".
        ztitle : str, optional
            The title for the z-axis, by default "IV".
        colorscale : str | list, optional
            The colorscale to use for the surface, by default None.
        title : str, optional
            The title of the chart, by default None.
        layout_kwargs : dict[str, Any] | None, optional
            Additional keyword arguments to apply with figure.update_layout(), by default None.

        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """
        from openbb_charting.charts.generic_charts import surface3d

        fig = surface3d(
            X=X,
            Y=Y,
            Z=Z,
            xtitle=xtitle,
            ytitle=ytitle,
            ztitle=ztitle,
            colorscale=colorscale,
            title=title,
            layout_kwargs=layout_kwargs,
            theme=theme,
        )
        fig = self._set_chart_style(fig)
        return fig

    def create_correlation_matrix(
        self,
        data: list[Data] | DataFrame,
        method: Literal["pearson", "kendall", "spearman"] = "pearson",
        colorscale: str = "RdBu",
        title: str = "Asset Correlation Matrix",
        layout_kwargs: dict[str, Any] | None = None,
    ):
        """Create a correlation matrix from external data.

        Parameters
        ----------
        data : list[Data] | DataFrame
            Input dataset.
        method : Literal["pearson", "kendall", "spearman"]
            Method to use for correlation calculation. Default is "pearson".
                pearson : standard correlation coefficient
                kendall : Kendall Tau correlation coefficient
                spearman : Spearman rank correlation
        colorscale : str
            Plotly colorscale to use for the heatmap. Default is "RdBu".
        title : str
            Title of the chart. Default is "Asset Correlation Matrix".
        layout_kwargs : dict[str, Any]
            Additional keyword arguments to apply with figure.update_layout(), by default None.

        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """
        from openbb_charting.charts.correlation_matrix import correlation_matrix

        kwargs = {
            "data": data,
            "method": method,
            "colorscale": colorscale,
            "title": title,
            "layout_kwargs": layout_kwargs,
        }
        fig, _ = correlation_matrix(**kwargs)
        fig = self._set_chart_style(fig)
        return fig

    def _normalize_chart_response(
        self, chart_response: Any, kwargs: dict[str, Any]
    ) -> tuple[Any, Chart]:
        """Normalize a chart function's output into a ``(figure, Chart)`` pair."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        if isinstance(chart_response, Chart):
            return getattr(chart_response, "fig", None), chart_response

        if isinstance(chart_response, OpenBBFigure):
            fig = chart_response
            content = fig.show(external=True, **kwargs).to_plotly_json()
            return fig, Chart(fig=fig, content=content, format=self._format)

        if isinstance(chart_response, tuple) and len(chart_response) == 2:
            fig, content = chart_response
            if isinstance(fig, OpenBBFigure):
                content = fig.show(external=True, **kwargs).to_plotly_json()
                return fig, Chart(fig=fig, content=content, format=self._format)
            return fig, Chart(fig=fig, content=content, format=type(fig).__name__)

        return chart_response, Chart(fig=chart_response, content=None, format="unknown")

    def show(self, render: bool = True, **kwargs):
        """Display chart and save it to the OBBject."""
        from openbb_core.app.charting import ChartLifecycle

        try:
            charting_function = self._get_chart_function(self._obbject._route or "")
            kwargs["obbject_item"] = self._obbject.results
            kwargs["charting_settings"] = self._charting_settings
            kwargs["standard_params"] = self._obbject._standard_params
            obb_kwargs = self._obbject._extra_params or {}
            if obb_kwargs:
                for k, v in obb_kwargs.items():
                    kwargs["extra_params"].update({k: v})

            kwargs["provider"] = self._obbject.provider
            kwargs["extra"] = self._obbject.extra
            kwargs.setdefault("command_location", self._obbject._route or "")

            context = self._dispatch_hook(ChartLifecycle.RESOLVE_DATA)
            context = self._dispatch_hook(ChartLifecycle.PRE_FIGURE, context=context)

            chart_response: Any = charting_function(**kwargs)
            fig, chart = self._normalize_chart_response(chart_response, kwargs)

            context = self._dispatch_hook(
                ChartLifecycle.POST_FIGURE,
                context=context,
                figure=fig,
                content=chart.content,
            )
            if context.figure is not None:
                chart.fig = context.figure
                fig = context.figure
            if context.content is not None:
                chart.content = context.content

            self._obbject.chart = chart

            if render and hasattr(fig, "show"):
                self._dispatch_hook(
                    ChartLifecycle.PRE_RENDER, context=context, figure=fig
                )
                fig.show(**kwargs)
                self._dispatch_hook(
                    ChartLifecycle.POST_RENDER, context=context, figure=fig
                )

        except (RuntimeError, OpenBBError) as e:
            raise e from e

        except Exception:
            try:
                fig = self.create_line_chart(
                    data=self._obbject.results,  # ty: ignore[invalid-argument-type]
                    render=False,
                    **kwargs,
                )
                fig = self._set_chart_style(fig)  # ty: ignore[invalid-argument-type]
                content = fig.show(external=True, **kwargs).to_plotly_json()
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    fig.show(**kwargs)
            except Exception as e:
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                    + f" -> {e} -> {e.args}"
                ) from e

    def to_chart(
        self,
        data: (
            list
            | dict
            | DataFrame
            | list[DataFrame]
            | Series
            | list[Series]
            | ndarray
            | Data
            | None
        ) = None,
        target: str | None = None,
        index: str | None = None,
        indicators: dict[str, dict[str, Any]] | None = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        volume_ticks_x: int = 7,
        render: bool = True,
        **kwargs,
    ):
        """Create an OpenBBFigure with user customizations (if any) and save it to the OBBject.

        Parameters
        ----------
        data : Data | DataFrame | Series
            Data to be plotted.
        indicators : dict[str, dict[str, Any]], optional
            Indicators to be plotted, by default None
        symbol : str, optional
            Symbol to be plotted. This is used for labels and titles, by default ""
        candles : bool, optional
            If True, candles will be plotted, by default True
        volume : bool, optional
            If True, volume will be plotted, by default True
        volume_ticks_x : int, optional
            Volume ticks, by default 7
        render : bool, optional
            If True, the chart will be rendered, by default True
        kwargs: dict[str, Any]
            Extra parameters to be passed to the chart constructor.
        """
        data_as_df, has_data = self._prepare_data_as_df(data)  # ty: ignore[invalid-argument-type]
        if target is not None:
            data_as_df = data_as_df[[target]]
        kwargs["candles"] = candles
        kwargs["volume"] = volume
        kwargs["volume_ticks_x"] = volume_ticks_x
        kwargs["indicators"] = indicators if indicators else {}
        kwargs["symbol"] = symbol
        kwargs["target"] = target
        kwargs["index"] = index
        kwargs["obbject_item"] = self._obbject.results
        kwargs["charting_settings"] = self._charting_settings
        kwargs["standard_params"] = self._obbject._standard_params
        kwargs["extra_params"] = self._obbject._extra_params
        kwargs["provider"] = self._obbject.provider
        kwargs["extra"] = self._obbject.extra
        try:
            if has_data:
                self.show(data=data_as_df, render=render, **kwargs)
            else:
                self.show(**kwargs, render=render)
        except Exception:
            try:
                fig = self.create_line_chart(data=data_as_df, render=False, **kwargs)
                fig = self._set_chart_style(fig)  # ty: ignore[invalid-argument-type]
                content = fig.show(external=True, **kwargs).to_plotly_json()
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    return fig.show(**kwargs)
            except Exception as e:
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                ) from e

    def _set_chart_style(self, figure: Figure):
        """Set the user preference for light or dark mode."""
        return figure

    def toggle_chart_style(self):
        """Toggle the chart style between light and dark mode."""
        import plotly.io as pio

        if not hasattr(self._obbject.chart, "fig"):
            raise ValueError(
                "Error: No chart has been created. Please create a chart first."
            )
        current = self._charting_settings.chart_style
        new = "light" if current == "dark" else "dark"
        self._charting_settings.chart_style = new
        template_name = "plotly_white" if new == "light" else "plotly_dark"
        figure = self._obbject.chart.fig
        figure.update_layout(template=pio.templates[template_name])  # ty: ignore[unresolved-attribute]
        self._obbject.chart.fig = figure
        self._obbject.chart.content = figure.show(external=True).to_plotly_json()  # ty: ignore[unresolved-attribute]

    @staticmethod
    def _convert_to_string(x):
        """Sanitize the data for the table."""
        from numpy import isnan

        if isinstance(x, (float, int)) and not isnan(x):
            return x
        if isinstance(x, dict):
            return ", ".join([str(v) for v in x.values()])
        if isinstance(x, list):
            if all(isinstance(i, dict) for i in x):
                return ", ".join(
                    str(", ".join([str(v) for v in i.values()])) for i in x
                )
            return ", ".join([str(i) for i in x])

        return (
            str(x)
            .replace("[", "")
            .replace("]", "")
            .replace("'{", "")
            .replace("}'", "")
            .replace("nan", "")
        )

    def table(
        self,
        data: DataFrame | Series | None = None,
        title: str = "",
        include_query_toolbar: bool = True,
    ):
        """Display an interactive table.

        Parameters
        ----------
        data : DataFrame | Series | None, optional
            Data to be plotted, by default None.
            If no data is provided the OBBject results will be used.
        title : str, optional
            Title of the table, by default "".
        include_query_toolbar : bool, optional
            Whether to include the Pandas Query toolbar, by default True.
        """
        from pandas import RangeIndex

        data_as_df, _ = self._prepare_data_as_df(data)
        if isinstance(data_as_df.index, RangeIndex):
            data_as_df.reset_index(inplace=True, drop=True)
        else:
            data_as_df.reset_index(inplace=True)
        for col in data_as_df.columns:
            data_as_df[col] = data_as_df[col].apply(self._convert_to_string)
        try:
            send_table = getattr(self._backend, "send_table")
            if include_query_toolbar:
                send_table(
                    df_table=data_as_df,
                    title=title or self._obbject._route or "",
                    theme=self._charting_settings.table_style,
                )
            else:
                send_table(
                    df_table=data_as_df,
                    title=title or self._obbject._route or "",
                    theme=self._charting_settings.table_style,
                    include_query_toolbar=False,
                )
        except Exception as e:
            warn(f"Failed to show table with backend. {e}")

    def url(
        self,
        url: str,
        title: str = "",
        width: int | None = None,
        height: int | None = None,
    ):
        """Return the URL of the chart."""
        try:
            self._backend.send_url(url=url, title=title, width=width, height=height)
        except Exception as e:
            warn(f"Failed to show figure with backend. {e}")
