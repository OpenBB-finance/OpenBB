"""OpenBB OBBject extension for charting."""
from typing import Callable

from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.extension import Extension

from charting import charting_router

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
        self._handle_backend()

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
