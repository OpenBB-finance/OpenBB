"""OpenBB OBBject extension for charting."""
from typing import Any, Callable, Dict, Optional, Tuple, Union

from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension

from charting import charting_router
from charting.core.to_chart import ChartIndicators, OpenBBFigure, to_chart

ext = Extension(name="charting")


@ext.obbject_accessor
class Charting:
    """Charting extension."""

    def __init__(self, obbject):
        """Initialize Charting extension."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.charts.charting_settings import ChartingSettings
        from openbb_core.app.model.obbject import OBBject

        self._obbject: OBBject = obbject
        self._obbject = obbject
        self._charting_settings = ChartingSettings(
            self._obbject._user_settings, self._obbject._system_settings
        )
        self._handle_backend()

    def _handle_backend(self):
        # pylint: disable=import-outside-toplevel
        from charting.core.backend import create_backend, get_backend

        create_backend(self._charting_settings)
        get_backend().start(debug=self._charting_settings.debug_mode)

    @staticmethod
    def _get_chart_function(route: str) -> Callable:
        """Given a route, it returns the chart function. The module must contain the given route."""
        adjusted_route = route.replace("/", "_")[1:]
        return getattr(charting_router, adjusted_route)

    def show(self, **kwargs):
        """Display chart and save it to the OBBject."""
        # TODO: in order for this to perform, either metadata can't be a user preference
        # or this need to be done differently, perhaps add the params and the route to
        # OBBject private attributes at the CommandRunner level.

        route = self._obbject.extra["metadata"].route
        standard_params = self._obbject.extra["metadata"].arguments["standard_params"]

        charting_function = self._get_chart_function(route)

        kwargs["obbject_item"] = self._obbject.results
        kwargs["charting_settings"] = self._charting_settings
        kwargs["standard_params"] = standard_params

        fig, content = charting_function(**kwargs)
        self._obbject.chart = Chart(
            fig=fig, content=content, format=charting_router.CHART_FORMAT
        )
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
            Data to be plotted.
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
        Tuple[OpenBBFigure, Dict[str, Any]]
            Tuple containing the OpenBBFigure and the plotly json representation of the chart.
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
