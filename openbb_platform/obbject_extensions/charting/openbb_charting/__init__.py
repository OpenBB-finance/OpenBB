"""OpenBB OBBject extension for charting."""

from typing import Any, Callable, Dict, Optional, Tuple, Union

from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension

from openbb_charting import charting_router
from openbb_charting.core.to_chart import ChartIndicators, OpenBBFigure, to_chart
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

    Properties
    ----------
    indicators
        Returns a list of the available indicators.


    """

    def __init__(self, obbject):
        """Initialize Charting extension."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.charts.charting_settings import ChartingSettings
        from openbb_core.app.model.obbject import OBBject

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,
            system_settings=self._obbject._system_settings,
        )
        self._handle_backend()

    @classmethod
    def indicators(cls):
        """Returns a list of the available indicators."""
        return ChartIndicators.get_available_indicators()

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
        adjusted_route = route.replace("/", "_")[1:]
        return getattr(charting_router, adjusted_route)

    def show(self, render: bool = True, **kwargs):
        """Display chart and save it to the OBBject."""
        charting_function = self._get_chart_function(
            self._obbject._route  # pylint: disable=protected-access
        )
        kwargs["obbject_item"] = self._obbject.results
        kwargs["charting_settings"] = self._charting_settings
        kwargs["standard_params"] = (
            self._obbject._standard_params.__dict__
        )  # pylint: disable=protected-access

        fig, content = charting_function(**kwargs)
        self._obbject.chart = Chart(
            fig=fig, content=content, format=charting_router.CHART_FORMAT
        )
        if render:
            fig.show()

    def to_chart(
        self,
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        volume_ticks_x: int = 7,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """
        Returns the plotly json representation of the chart.

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

        Returns
        -------
        OpenBBFigure - note that although it only returns the figure, the chart is also saved
        to the OBBject.

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
        > res.to_chart(**{"indicators": indicators})

        2) Get all the available indicators
        > from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
        > ChartIndicators.get_available_indicators()
        """
        data = self._obbject.to_dataframe()
        fig, content = to_chart(
            data,
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
        return fig
