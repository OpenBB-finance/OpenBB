"""OpenBB OBBject extension for charting."""

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from warnings import warn

import numpy as np
import pandas as pd
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension
from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
from openbb_core.provider.abstract.data import Data

from openbb_charting import charting_router
from openbb_charting.core.backend import Backend, create_backend, get_backend
from openbb_charting.core.to_chart import ChartIndicators, to_chart
from openbb_charting.utils.helpers import get_charting_functions

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
        Returns the plotly json representation of the chart.
    functions
        Returns a list of Platform commands with charting functions.
    indicators
        Returns a list of the available indicators to use with the `to_chart` method.
    """

    def __init__(self, obbject):
        """Initialize Charting extension."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.charts.charting_settings import ChartingSettings
        from openbb_core.app.model.obbject import OBBject

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,  # type: ignore
            system_settings=self._obbject._system_settings,  # type: ignore
        )
        self._backend: Backend = self._handle_backend()

    @classmethod
    def indicators(cls):
        """Return a list of the available indicators."""
        return ChartIndicators.get_available_indicators()

    @classmethod
    def functions(cls):
        """Return a list of the available functions."""
        return get_charting_functions()

    def _handle_backend(self):
        """Create and start the backend."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.backend import (  # pylint: disable=W0621, W0404
            create_backend,  # noqa
            get_backend,  # noqa
        )

        create_backend(self._charting_settings)
        backend = get_backend()
        backend.start(debug=self._charting_settings.debug_mode)
        return backend

    @staticmethod
    def _get_chart_function(route: str) -> Callable:
        """Given a route, it returns the chart function. The module must contain the given route."""
        adjusted_route = route.replace("/", "_")[1:]
        return getattr(charting_router, adjusted_route)

    def show(self, render: bool = True, **kwargs):
        """Display chart and save it to the OBBject."""
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
        kwargs["provider"] = self._obbject.provider  # pylint: disable=protected-access
        kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access
        kwargs["warnings"] = self._obbject.warnings  # pylint: disable=protected-access
        fig, content = charting_function(**kwargs)
        self._obbject.chart = Chart(
            fig=fig, content=content, format=charting_router.CHART_FORMAT
        )
        if render:
            fig.show(**kwargs)

    def _prepare_data_as_df(
        self, data: Optional[Union[pd.DataFrame, pd.Series]]
    ) -> Tuple[pd.DataFrame, bool]:
        has_data = (isinstance(data, (pd.DataFrame, pd.Series)) and not data.empty) or (
            bool(data)
        )
        index = (
            data.index.name
            if has_data and isinstance(data, (pd.DataFrame, pd.Series))
            else None
        )
        data_as_df: pd.DataFrame = (
            basemodel_to_df(convert_to_basemodel(data), index=index)
            if has_data
            else self._obbject.to_dataframe()
        )
        if "date" in data_as_df.columns:
            data_as_df = data_as_df.set_index("date")
        if "provider" in data_as_df.columns:
            data_as_df.drop(columns="provider", inplace=True)
        return data_as_df, has_data

    # pylint: disable=too-many-arguments
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
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        volume_ticks_x: int = 7,
        render: bool = True,
        **kwargs,
    ):
        """Create a OpenBBFigure with user customizations (if any) and saves it to the OBBject.

        This function is used so it can be called at the module level and used out of the box,
        which allows some more flexibility, ease of use and doesn't require the user to know
        about the PlotlyTA class.

        Parameters
        ----------
        data : Union[pd.DataFrame, pd.Series]
            Data to be plotted Data to be plotted (OHLCV data).
        indicators : Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]], optional
            Indicators to be plotted, by default None
        symbol : str, optional
            Symbol to be plotted, by default ""
        candles : bool, optional
            If True, candles will be plotted, by default True
        volume : bool, optional
            If True, volume will be plotted, by default True
        prepost : bool, optional
            If True, prepost will be plotted, by default False
        volume_ticks_x : int, optional
            Volume ticks, by default 7
        render : bool, optional
            If True, the chart will be rendered, by default True

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
        data_as_df, has_data = self._prepare_data_as_df(data)  # type: ignore
        try:
            fig, content = to_chart(
                data_as_df,
                indicators=indicators,
                symbol=symbol,
                candles=candles,
                volume=volume,
                prepost=prepost,
                volume_ticks_x=volume_ticks_x,
            )
            self._obbject.chart = Chart(
                fig=fig, content=content, format=charting_router.CHART_FORMAT
            )
            if render:
                fig.show(**kwargs)

        except Exception:
            try:
                if has_data:
                    self.show(data=data_as_df, symbol=symbol, render=render, **kwargs)
                else:
                    self.show(**kwargs)
            except Exception as e:
                raise RuntimeError("Could not create chart from the OBBject.") from e

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
