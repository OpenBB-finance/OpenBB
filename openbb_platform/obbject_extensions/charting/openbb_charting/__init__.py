"""OpenBB OBBject extension for charting."""

# pylint: disable=too-many-arguments,unused-argument

import warnings
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)
from warnings import warn

import numpy as np
import pandas as pd
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
from openbb_core.provider.abstract.data import Data
from plotly.graph_objs import Figure

from openbb_charting import charting_router
from openbb_charting.core.backend import Backend, create_backend, get_backend
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.query_params import ChartParams, IndicatorsParams
from openbb_charting.utils.generic_charts import bar_chart, line_chart
from openbb_charting.utils.helpers import get_charting_functions

warnings.filterwarnings(
    "ignore", category=UserWarning, module="openbb_core.app.model.extension", lineno=47
)

ext = Extension(name="charting")


@ext.obbject_accessor
class Charting:
    """
    Charting extension.

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
    """

    def __init__(self, obbject):
        """Initialize Charting extension."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.charts.charting_settings import ChartingSettings

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,  # type: ignore
            system_settings=self._obbject._system_settings,  # type: ignore
        )
        self._backend: Backend = self._handle_backend()

    @classmethod
    def indicators(cls):
        """
        Return an instance of the IndicatorsParams class, containing all available indicators and their parameters.
        Without assigning to a variable, it will print the the information to the console.
        """
        return IndicatorsParams()

    @classmethod
    def functions(cls):
        """Return a list of the available functions."""
        return get_charting_functions()

    def _handle_backend(self) -> Backend:
        """Create and start the backend."""

        create_backend(self._charting_settings)
        backend = get_backend()
        backend.start(debug=self._charting_settings.debug_mode)
        return backend

    @staticmethod
    def _get_chart_function(route: str) -> Callable:
        """Given a route, it returns the chart function. The module must contain the given route."""

        if route is None:
            raise ValueError("OBBject was initialized with no function route.")
        adjusted_route = route.replace("/", "_")[1:]
        return getattr(charting_router, adjusted_route)

    def get_params(self) -> ChartParams:
        """
        Return the ChartQueryParams class for the function the OBBject was created from.
        Without assigning to a variable, it will print the docstring to the console.
        """
        if self._obbject._route is None:  # pylint: disable=protected-access
            raise ValueError("OBBject was initialized with no function route.")
        charting_function = (
            self._obbject._route  # pylint: disable=protected-access
        ).replace("/", "_")[1:]
        if hasattr(ChartParams, charting_function):
            return getattr(ChartParams, charting_function)()
        raise ValueError(
            f"Error: No chart parameters are defined for the route: {charting_function}"
        )

    def _prepare_data_as_df(
        self, data: Optional[Union[pd.DataFrame, pd.Series]]
    ) -> Tuple[pd.DataFrame, bool]:
        """Convert supplied data to a DataFrame."""
        has_data = (
            isinstance(data, (Data, pd.DataFrame, pd.Series)) and not data.empty
        ) or (bool(data))
        index = (
            data.index.name
            if has_data and isinstance(data, (pd.DataFrame, pd.Series))
            else None
        )
        data_as_df: pd.DataFrame = (
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
            pd.DataFrame,
            List[pd.DataFrame],
            pd.Series,
            List[pd.Series],
            np.ndarray,
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
    ) -> Union[OpenBBFigure, Figure, None]:
        """Create a line chart from external data and render a chart or return the OpenBBFigure.

        Parameters
        ----------
        data : Union[Data, pd.DataFrame, pd.Series]
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
        if render:
            return fig.show(**kwargs)

        return fig

    def create_bar_chart(
        self,
        data: Union[
            list,
            dict,
            pd.DataFrame,
            List[pd.DataFrame],
            pd.Series,
            List[pd.Series],
            np.ndarray,
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
    ) -> Union[OpenBBFigure, Figure, None]:
        """Create a bar chart on a single x-axis with one or more values for the y-axis.

        Parameters
        ----------
        data : Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], np.ndarray, Data]
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

        if render:
            return fig.show(**kwargs)

        return fig

    # pylint: disable=inconsistent-return-statements
    def show(self, render: bool = True, **kwargs):
        """Display chart and save it to the OBBject."""

        try:
            charting_function = self._get_chart_function(
                self._obbject._route  # pylint: disable=protected-access
            )
            kwargs["obbject_item"] = self._obbject.results
            kwargs["charting_settings"] = self._charting_settings
            if (
                hasattr(self._obbject, "_standard_params")
                and self._obbject._standard_params  # pylint: disable=protected-access
            ):
                kwargs["standard_params"] = (
                    self._obbject._standard_params.__dict__  # pylint: disable=protected-access
                )
            kwargs["provider"] = (
                self._obbject.provider
            )  # pylint: disable=protected-access
            kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access

            if "kwargs" in kwargs:
                _kwargs = kwargs.pop("kwargs")
                kwargs.update(_kwargs.get("chart_params", {}))
            fig, content = charting_function(**kwargs)
            self._obbject.chart = Chart(
                fig=fig, content=content, format=charting_router.CHART_FORMAT
            )
            if render:
                fig.show(**kwargs)
        except Exception:
            try:
                fig = self.create_line_chart(data=self._obbject.results, render=False, **kwargs)  # type: ignore
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=charting_router.CHART_FORMAT
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
                pd.DataFrame,
                List[pd.DataFrame],
                pd.Series,
                List[pd.Series],
                np.ndarray,
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
        """
        Create an OpenBBFigure with user customizations (if any) and save it to the OBBject.
        This function is used to populate, or re-populate, the OBBject with a chart using the data within
        the OBBject or external data supplied via the `data` parameter.

        This function modifies the original OBBject by overwriting the existing chart.

        Parameters
        ----------
        data : Union[Data, pd.DataFrame, pd.Series]
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
        if (
            hasattr(self._obbject, "_standard_params")
            and self._obbject._standard_params  # pylint: disable=protected-access
        ):
            kwargs["standard_params"] = (
                self._obbject._standard_params.__dict__  # pylint: disable=protected-access
            )
        kwargs["provider"] = self._obbject.provider  # pylint: disable=protected-access
        kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access
        if "kwargs" in kwargs:
            _kwargs = kwargs.pop("kwargs")
            kwargs.update(_kwargs.get("chart_params", {}))
        try:
            if has_data:
                self.show(data=data_as_df, render=render, **kwargs)
            else:
                self.show(**kwargs, render=render)
        except Exception:
            try:
                fig = self.create_line_chart(data=data_as_df, render=False, **kwargs)
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=charting_router.CHART_FORMAT
                )
                if render:
                    return fig.show(**kwargs)  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                ) from e

    def table(
        self,
        data: Optional[Union[pd.DataFrame, pd.Series]] = None,
        title: str = "",
    ):
        """
        Display an interactive table.

        Parameters
        ----------
        data : Optional[Union[pd.DataFrame, pd.Series]], optional
            Data to be plotted, by default None.
            If no data is provided the OBBject results will be used.
        title : str, optional
            Title of the table, by default "".
        """
        data_as_df, _ = self._prepare_data_as_df(data)
        if isinstance(data_as_df.index, pd.RangeIndex):
            data_as_df.reset_index(inplace=True, drop=True)
        else:
            data_as_df.reset_index(inplace=True)
        if self._backend.isatty:
            try:
                self._backend.send_table(
                    df_table=data_as_df,
                    title=title
                    or self._obbject._route,  # pylint: disable=protected-access
                    theme=self._charting_settings.table_style,
                )
            except Exception as e:
                warn(f"Failed to show figure with backend. {e}")

        else:
            from plotly import (  # pylint:disable=import-outside-toplevel
                optional_imports,
            )

            ipython_display = optional_imports.get_module("IPython.display")
            if ipython_display:
                ipython_display.display(ipython_display.HTML(data_as_df.to_html()))
            else:
                warn("IPython.display is not available.")
