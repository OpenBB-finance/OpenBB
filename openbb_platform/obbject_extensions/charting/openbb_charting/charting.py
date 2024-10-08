"""Charting Class implementation."""

# pylint: disable=too-many-arguments,unused-argument,too-many-positional-arguments

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)
from warnings import warn

from importlib_metadata import entry_points
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.helpers import (
    get_charting_functions,
    get_charting_functions_list,
)

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from plotly.graph_objs import Figure  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa
    from openbb_charting.query_params import ChartParams  # noqa
    from openbb_charting.core.backend import Backend  # noqa


class Charting:
    """Charting extension.

    Methods
    -------
    show
        Display chart and save it to the OBBject.
    to_chart
        Redraw the chart and save it to the OBBject, with an optional entry point for Data.
    functions
        Return a list of Platform commands with charting functions.
    get_params
        Return the charting parameters for the function the OBBject was created from.
    indicators
        Return the list of the available technical indicators to use with the `to_chart` method and OHLC+V data.
    table
        Display an interactive table.
    create_line_chart
        Create a line chart from external data.
    create_bar_chart
        Create a bar chart, on a single x-axis with one or more values for the y-axis, from external data.
    create_correlation_matrix
        Create a correlation matrix from external data.
    toggle_chart_style
        Toggle the chart style, of an existing chart, between light and dark mode.
    """

    _extension_views: ClassVar[List[Type]] = [
        entry_point.load()
        for entry_point in entry_points(group="openbb_charting_extension")
    ]
    _format = "plotly"  # the charts computed by this extension will be in plotly format

    def __init__(self, obbject):
        """Initialize Charting extension."""
        # pylint: disable=import-outside-toplevel
        import importlib  # noqa

        charting_settings_module = importlib.import_module(
            "openbb_core.app.model.charts.charting_settings", "ChartingSettings"
        )
        ChartingSettings = charting_settings_module.ChartingSettings

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,  # type: ignore
            system_settings=self._obbject._system_settings,  # type: ignore
        )
        self._backend = self._handle_backend()
        self._functions: Dict[str, Callable] = self._get_functions()

    @classmethod
    def indicators(cls):
        """Return an instance of the IndicatorsParams class, containing all available indicators and their parameters.

        Without assigning to a variable, it will print the the information to the console.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.query_params import IndicatorsParams

        return IndicatorsParams()

    @classmethod
    def functions(cls) -> List[str]:
        """Return a list of the available functions."""
        functions: List[str] = []
        for view in cls._extension_views:
            functions.extend(get_charting_functions_list(view))

        return functions

    def _get_functions(self) -> Dict[str, Callable]:
        """Return a dict with the available functions."""
        functions: Dict[str, Callable] = {}
        for view in self._extension_views:
            functions.update(get_charting_functions(view))

        return functions

    def _handle_backend(self) -> "Backend":
        """Create and start the backend."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.backend import create_backend, get_backend

        create_backend(self._charting_settings)
        backend = get_backend()
        backend.start(debug=self._charting_settings.debug_mode)
        return backend

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

    def get_params(self) -> Union["ChartParams", None]:
        """Return the ChartQueryParams class for the function the OBBject was created from.

        Without assigning to a variable, it will print the docstring to the console.
        If the class is not defined, the help for the function will be returned.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.query_params import ChartParams

        if self._obbject._route is None:  # pylint: disable=protected-access
            raise ValueError("OBBject was initialized with no function route.")
        charting_function = (
            self._obbject._route  # pylint: disable=protected-access
        ).replace("/", "_")[1:]
        if hasattr(ChartParams, charting_function):
            return getattr(ChartParams, charting_function)()

        return help(  # type: ignore
            self._get_chart_function(  # pylint: disable=protected-access
                self._obbject.extra[  # pylint: disable=protected-access
                    "metadata"
                ].route
            )
        )

    def _prepare_data_as_df(
        self, data: Optional[Union["DataFrame", "Series"]]
    ) -> Tuple["DataFrame", bool]:
        """Convert supplied data to a DataFrame."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
        from pandas import DataFrame, Series

        has_data = (
            isinstance(data, (Data, DataFrame, Series)) and not data.empty  # type: ignore
        ) or (bool(data))
        index = (
            data.index.name
            if has_data and isinstance(data, (DataFrame, Series))
            else None
        )
        data_as_df: DataFrame = (
            basemodel_to_df(convert_to_basemodel(data), index=index)
            if has_data
            else self._obbject.to_dataframe(index=index)
        )
        if "date" in data_as_df.columns:
            data_as_df = data_as_df.set_index("date")
        if "provider" in data_as_df.columns:
            data_as_df.drop(columns="provider", inplace=True)
        return data_as_df, has_data

    # pylint: disable=too-many-locals
    def create_line_chart(
        self,
        data: Union[
            list,
            dict,
            "DataFrame",
            List["DataFrame"],
            "Series",
            List["Series"],
            "ndarray",
            Data,
        ],
        index: Optional[str] = None,
        target: Optional[str] = None,
        title: Optional[str] = None,
        x: Optional[str] = None,
        xtitle: Optional[str] = None,
        y: Optional[Union[str, List[str]]] = None,
        ytitle: Optional[str] = None,
        y2: Optional[Union[str, List[str]]] = None,
        y2title: Optional[str] = None,
        layout_kwargs: Optional[dict] = None,
        scatter_kwargs: Optional[dict] = None,
        normalize: bool = False,
        returns: bool = False,
        same_axis: bool = False,
        render: bool = True,
        **kwargs,
    ) -> Union["OpenBBFigure", "Figure", None]:
        """Create a line chart from external data and render a chart or return the OpenBBFigure.

        Parameters
        ----------
        data : Union[Data, DataFrame, Series]
            Data to be plotted (OHLCV data).
        index : Optional[str], optional
            Index column, by default None
        target : Optional[str], optional
            Target column to be plotted, by default None
        title : Optional[str], optional
            Chart title, by default None
        x : Optional[str], optional
            X-axis column, by default None
        xtitle : Optional[str], optional
            X-axis title, by default None
        y : Optional[Union[str, List[str]]], optional
            Y-axis column(s), by default None
            If None are supplied, the layout is optimized for the contents of data.
            Where many units/scales are present,
            it will attempt to divide based on the range of values.
        ytitle : Optional[str], optional
            Y-axis title, by default None
        y2 : Optional[Union[str, List[str]]], optional
            Y2-axis column(s), by default None
        y2title : Optional[str], optional
            Y2-axis title, by default None
        layout_kwargs : Optional[dict], optional
            Additional Plotly Layout parameters for `fig.update_layout`, by default None
        scatter_kwargs : Optional[dict], optional
            Additional Plotly parameters applied on creation of each scatter plot, by default None
        normalize : bool, optional
            Normalize the data with Z-Score Standardization, by default False
        returns : bool, optional
            Convert the data to cumulative returns, by default False
        same_axis: bool, optional
            If True, forces all data onto the same Y-axis, by default False
        render: bool, optional
            If True, the chart will be rendered, by default True
        **kwargs: Dict[str, Any]
            Extra parameters to be passed to `figure.show()`
        """
        # pylint: disable=import-outside-toplevel
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
            return fig.show(**kwargs)

        return fig

    def create_bar_chart(
        self,
        data: Union[
            list,
            dict,
            "DataFrame",
            List["DataFrame"],
            "Series",
            List["Series"],
            "ndarray",
            Data,
        ],
        x: str,
        y: Union[str, List[str]],
        barmode: Literal["group", "stack", "relative", "overlay"] = "group",
        xtype: Literal[
            "category", "multicategory", "date", "log", "linear"
        ] = "category",
        title: Optional[str] = None,
        xtitle: Optional[str] = None,
        ytitle: Optional[str] = None,
        orientation: Literal["h", "v"] = "v",
        colors: Optional[List[str]] = None,
        layout_kwargs: Optional[Dict[str, Any]] = None,
        bar_kwargs: Optional[Dict[str, Any]] = None,
        render: bool = True,
        **kwargs,
    ) -> Union["OpenBBFigure", "Figure", None]:
        """Create a bar chart on a single x-axis with one or more values for the y-axis.

        Parameters
        ----------
        data : Union[list, dict, DataFrame, List[DataFrame], Series, List[Series], ndarray, Data]
            Data to plot.
        x : str
            The x-axis column name.
        y : Union[str, List[str]]
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
        colors: List[str], optional
            Manually set the colors to cycle through for each column in 'y', by default None.
        bar_kwargs : Dict[str, Any], optional
            Additional keyword arguments to apply with figure.add_bar(), by default None.
        layout_kwargs : Dict[str, Any], optional
            Additional keyword arguments to apply with figure.update_layout(), by default None.
        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """
        # pylint: disable=import-outside-toplevel
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
            return fig.show(**kwargs)

        return fig

    def create_correlation_matrix(
        self,
        data: Union[
            list[Data],
            "DataFrame",
        ],
        method: Literal["pearson", "kendall", "spearman"] = "pearson",
        colorscale: str = "RdBu",
        title: str = "Asset Correlation Matrix",
        layout_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Create a correlation matrix from external data.

        Parameters
        ----------
        data : Union[list[Data], DataFrame]
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
        layout_kwargs : Dict[str, Any]
            Additional keyword arguments to apply with figure.update_layout(), by default None.

        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """
        # pylint: disable=import-outside-toplevel
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

    # pylint: disable=inconsistent-return-statements
    def show(self, render: bool = True, **kwargs):
        """Display chart and save it to the OBBject."""
        try:
            charting_function = self._get_chart_function(
                self._obbject._route  # pylint: disable=protected-access
            )
            kwargs["obbject_item"] = self._obbject.results
            kwargs["charting_settings"] = self._charting_settings  #
            kwargs["standard_params"] = (
                self._obbject._standard_params  # pylint: disable=protected-access
            )
            kwargs["extra_params"] = (
                self._obbject._extra_params  # pylint: disable=protected-access
            )
            kwargs["provider"] = self._obbject.provider
            kwargs["extra"] = self._obbject.extra
            fig, content = charting_function(**kwargs)
            fig = self._set_chart_style(fig)
            content = fig.show(external=True, **kwargs).to_plotly_json()
            self._obbject.chart = Chart(fig=fig, content=content, format=self._format)
            if render:
                fig.show(**kwargs)
        except Exception:  # pylint: disable=W0718
            try:
                fig = self.create_line_chart(data=self._obbject.results, render=False, **kwargs)  # type: ignore
                fig = self._set_chart_style(fig)
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    return fig.show(**kwargs)  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                ) from e

    # pylint: disable=too-many-locals,inconsistent-return-statements
    def to_chart(
        self,
        data: Optional[
            Union[
                list,
                dict,
                "DataFrame",
                List["DataFrame"],
                "Series",
                List["Series"],
                "ndarray",
                Data,
            ]
        ] = None,
        target: Optional[str] = None,
        index: Optional[str] = None,
        indicators: Optional[Dict[str, Dict[str, Any]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        volume_ticks_x: int = 7,
        render: bool = True,
        **kwargs,
    ):
        """Create an OpenBBFigure with user customizations (if any) and save it to the OBBject.

        This function is used to populate, or re-populate, the OBBject with a chart using the data within
        the OBBject or external data supplied via the `data` parameter.
        This function modifies the original OBBject by overwriting the existing chart.

        Parameters
        ----------
        data : Union[Data, DataFrame, Series]
            Data to be plotted.
        indicators : Dict[str, Dict[str, Any]], optional
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
        kwargs: Dict[str, Any]
            Extra parameters to be passed to the chart constructor.

        Examples
        --------
        Plotting a time series with TA indicators

        >>> from openbb import obb
        >>> res = obb.equity.price.historical("AAPL")
        >>> indicators = dict(
        >>>    sma=dict(length=[20,30,50]),
        >>>    adx=dict(length=14),
        >>>    rsi=dict(length=14),
        >>>    macd=dict(fast=12, slow=26, signal=9),
        >>>    bbands=dict(length=20, std=2),
        >>>    stoch=dict(length=14),
        >>>    ema=dict(length=[20,30,50]),
        >>> )
        >>> res.charting.to_chart(**{"indicators": indicators})

        Get all the available indicators

        >>> res = obb.equity.price.historical("AAPL")
        >>> indicators = res.charting.indicators()
        >>> indicators?
        """
        data_as_df, has_data = self._prepare_data_as_df(data)  # type: ignore
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
        kwargs["standard_params"] = (
            self._obbject._standard_params  # pylint: disable=protected-access
        )
        kwargs["extra_params"] = (
            self._obbject._extra_params  # pylint: disable=protected-access
        )
        kwargs["provider"] = self._obbject.provider  # pylint: disable=protected-access
        kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access
        try:
            if has_data:
                self.show(data=data_as_df, render=render, **kwargs)
            else:
                self.show(**kwargs, render=render)
        except Exception:  # pylint: disable=W0718
            try:
                fig = self.create_line_chart(data=data_as_df, render=False, **kwargs)
                fig = self._set_chart_style(fig)
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    return fig.show(**kwargs)  # type: ignore
            except Exception as e:  # pylint: disable=W0718
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                ) from e

    def _set_chart_style(self, figure: "Figure"):
        """Set the user preference for light or dark mode."""
        style = self._charting_settings.chart_style
        font_color = "black" if style == "light" else "white"
        paper_bgcolor = "white" if style == "light" else "black"
        figure = figure.update_layout(
            dict(  # pylint: disable=R1735
                font_color=font_color, paper_bgcolor=paper_bgcolor
            )
        )
        return figure

    def toggle_chart_style(self):
        """Toggle the chart style between light and dark mode."""
        if not hasattr(self._obbject.chart, "fig"):
            raise ValueError(
                "Error: No chart has been created. Please create a chart first."
            )
        current = self._charting_settings.chart_style
        new = "light" if current == "dark" else "dark"
        self._charting_settings.chart_style = new
        figure = self._obbject.chart.fig  # type: ignore[union-attr]
        updated_figure = self._set_chart_style(figure)
        self._obbject.chart.fig = updated_figure  # type: ignore[union-attr]
        self._obbject.chart.content = updated_figure.show(  # type: ignore[union-attr]
            external=True
        ).to_plotly_json()

    @staticmethod
    def _convert_to_string(x):
        """Sanitize the data for the table."""
        # pylint: disable=import-outside-toplevel
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
        data: Optional[Union["DataFrame", "Series"]] = None,
        title: str = "",
    ):
        """Display an interactive table.

        Parameters
        ----------
        data : Optional[Union[DataFrame, Series]], optional
            Data to be plotted, by default None.
            If no data is provided the OBBject results will be used.
        title : str, optional
            Title of the table, by default "".
        """
        # pylint: disable=import-outside-toplevel
        from pandas import RangeIndex

        data_as_df, _ = self._prepare_data_as_df(data)
        if isinstance(data_as_df.index, RangeIndex):
            data_as_df.reset_index(inplace=True, drop=True)
        else:
            data_as_df.reset_index(inplace=True)
        for col in data_as_df.columns:
            data_as_df[col] = data_as_df[col].apply(self._convert_to_string)
        if self._backend.isatty:
            try:
                self._backend.send_table(
                    df_table=data_as_df,
                    title=title
                    or self._obbject._route,  # pylint: disable=protected-access
                    theme=self._charting_settings.table_style,
                )
            except Exception as e:  # pylint: disable=W0718
                warn(f"Failed to show figure with backend. {e}")

        else:
            from plotly import optional_imports

            ipython_display = optional_imports.get_module("IPython.display")
            if ipython_display:
                ipython_display.display(ipython_display.HTML(data_as_df.to_html()))
            else:
                warn("IPython.display is not available.")

    def url(
        self,
        url: str,
        title: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """Return the URL of the chart."""
        try:
            self._backend.send_url(url=url, title=title, width=width, height=height)
        except Exception as e:  # pylint: disable=W0718
            warn(f"Failed to show figure with backend. {e}")
