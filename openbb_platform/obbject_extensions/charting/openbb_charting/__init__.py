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
    Union,
)

import numpy as np
import pandas as pd
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
from openbb_core.provider.abstract.data import Data
from plotly.graph_objs import Figure

from openbb_charting import charting_router
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.to_chart import ChartIndicators
from openbb_charting.query_params import ChartParams, IndicatorsParams
from openbb_charting.utils.generic_charts import bar_chart, line_chart
from openbb_charting.utils.helpers import get_charting_functions

warnings.filterwarnings(
    "ignore", category=UserWarning, module="openbb_core.app.model.extension", lineno=49
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
        Redraws the chart and saves it to the OBBject, with an optional entry point for Data.
    functions
        Returns a list of Platform commands with charting functions.
    indicators
        Returns a list of the available indicators to use with the `to_chart` method.
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

    @classmethod
    def indicators(cls):
        """Returns a list of the available indicators."""
        # return ChartIndicators.get_available_indicators()
        return IndicatorsParams()

    @classmethod
    def functions(cls):
        """Returns a list of the available functions."""
        return get_charting_functions()

    def _handle_backend(self):
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.backend import create_backend, get_backend

        create_backend(self._charting_settings)
        get_backend().start(debug=self._charting_settings.debug_mode)

    @staticmethod
    def _get_chart_function(route: str) -> Callable:
        """Given a route, it returns the chart function. The module must contain the given route."""

        if route is None:
            raise ValueError("OBBject was initialized with no function route.")
        adjusted_route = route.replace("/", "_")[1:]
        return getattr(charting_router, adjusted_route)

    def get_params(self) -> ChartParams:
        """Returns the ChartQueryParams class for the function the OBBject was created from.
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
        self._handle_backend()
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
        render: bool = True,
        **kwargs,
    ) -> Union[OpenBBFigure, Figure, None]:
        """Create a vertical bar chart on a single x-axis with one or more values for the y-axis.

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
        title : Optional[str], optional
            The title of the chart, by default None.
        xtitle : Optional[str], optional
            The x-axis title, by default None.
        ytitle : Optional[str], optional
            The y-axis title, by default None.
        colors: Optional[List[str]], optional
            Manually set the colors to cycle through for each column in 'y', by default None.
        layout_kwargs : Optional[Dict[str, Any]], optional
            Additional keyword arguments to apply with figure.update_layout(), by default None.

        Returns
        -------
        OpenBBFigure
            The OpenBBFigure object.
        """

        self._handle_backend()
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
            layout_kwargs=layout_kwargs,
        )

        if render:
            return fig.show(**kwargs)

        return fig

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
            self._handle_backend()

            fig, content = charting_function(**kwargs)
            self._obbject.chart = Chart(
                fig=fig, content=content, format=charting_router.CHART_FORMAT
            )
            if render:
                fig.show(**kwargs)
        except Exception:
            try:
                fig = self.create_line_chart(render=False, **kwargs)
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

    # pylint: disable=too-many-locals
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
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        volume_ticks_x: int = 7,
        render: bool = True,
        **kwargs,
    ):
        """
        Creates an OpenBBFigure with user customizations (if any) and saves it to the OBBject.

        This function is used so it can be called at the module level and used out of the box,
        which allows some more flexibility, ease of use and doesn't require the user to know
        about the PlotlyTA class.

        Parameters
        ----------
        data : Union[Data, pd.DataFrame, pd.Series]
            Data to be plotted (OHLCV data).
        indicators : Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]], optional
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
        1) Plotting a time series with TA indicators
        > from openbb import obb
        > res = obb.equity.price.historical("AAPL")
        > indicators = dict(
        >    sma=dict(length=[20,30,50]),
        >    adx=dict(length=14),
        >    rsi=dict(length=14),
        >    macd=dict(fast=12, slow=26, signal=9),
        >    bbands=dict(length=20, std=2),
        >    stoch=dict(length=14),
        >    ema=dict(length=[20,30,50]),
        > )
        > res.charting.to_chart(**{"indicators": indicators})

        2) Get all the available indicators
        > from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
        > ChartIndicators.get_available_indicators()
        or
        > from openbb_charting import Charting
        > Charting.indicators()
        """
        has_data = (isinstance(data, (pd.DataFrame, pd.Series)) and not data.empty) or (
            data
        )

        index = (
            data.index.name
            if has_data and isinstance(data, (pd.DataFrame, pd.Series))
            else index
        )
        data_as_df: pd.DataFrame = (
            basemodel_to_df(convert_to_basemodel(data), index=index)
            if has_data
            else self._obbject.to_dataframe()
        )
        if "date" in data_as_df.columns:
            data_as_df = data_as_df.set_index("date")

        if index is not None and index in data_as_df.columns:
            data_as_df = data_as_df.set_index(index)

        if target is not None:
            data_as_df = data_as_df[[target]]

        if (
            hasattr(self._obbject, "_standard_params")
            and self._obbject._standard_params  # pylint: disable=protected-access
        ):
            kwargs["standard_params"] = (
                self._obbject._standard_params.__dict__  # pylint: disable=protected-access
            )

        kwargs["candles"] = candles
        kwargs["volume"] = volume
        kwargs["volume_ticks_x"] = volume_ticks_x
        kwargs["provider"] = self._obbject.provider  # pylint: disable=protected-access
        kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access
        kwargs["warnings"] = self._obbject.warnings  # pylint: disable=protected-access
        kwargs["indicators"] = indicators
        kwargs["symbol"] = symbol
        kwargs["target"] = target
        kwargs["index"] = index

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
