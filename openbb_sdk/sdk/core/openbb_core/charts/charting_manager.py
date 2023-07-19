from importlib import import_module
from typing import Callable, Generic, Optional, TypeVar

import pkg_resources
from openbb_core.app.model.chart import Chart, ChartFormat
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.user_service import UserService
from openbb_core.charts.models.charting_settings import ChartingSettings

T = TypeVar("T")

POETRY_PLUGIN = "openbb_core_extension"


class ChartingManagerError(Exception):
    pass


class ChartingManager:
    """
    Charting manager class.
    It is responsible for retrieving and executing the charting function, corresponding
    to a given route, from the user's preferred charting extension.
    Parameters
    ----------
    user_settings : Optional[UserSettings]
        User settings.
    Attributes
    ----------
    _charting_extension : str
        Charting extension name, which is retrieved from the user preferences.
    _charting_extension_installed : bool
        Either charting extension is installed or not.
    Raises
    ------
    ChartingManagerError
        If charting extension is not installed.
    """

    def __init__(
        self,
        user_settings: Optional[UserSettings] = None,
    ) -> None:
        user_settings = user_settings or UserService().read_default_user_settings()

        self._charting_extension = user_settings.preferences.charting_extension
        self._charting_extension_installed = self.check_charting_extension_installed(
            self._charting_extension
        )

    @staticmethod
    def check_charting_extension_installed(
        charting_extension: str, plugin: Optional[str] = POETRY_PLUGIN
    ) -> bool:
        """
        Checks if charting extension is installed.
        Given a charting extension name, it checks if it is installed under the given plugin.
        Parameters
        ----------
        charting_extension : str
            Charting extension name.
        plugin : Optional[str]
            Plugin name.
        Returns
        -------
        bool
            Either charting extension is installed or not.
        """
        extensions = [ext.name for ext in pkg_resources.iter_entry_points(plugin)]
        return charting_extension in extensions

    @staticmethod
    def _get_extension_module(
        extension_name: str, plugin: Optional[str] = POETRY_PLUGIN
    ):
        """
        Get the module of the given extension.
        """
        for entry_point in pkg_resources.iter_entry_points(plugin):
            if entry_point.name == extension_name:
                return import_module(entry_point.module_name)

    @classmethod
    def get_chart_format(cls, extension_name: str) -> ChartFormat:
        """
        Given an extension name, it returns the chart format.
        The module must contain the `CHART_FORMAT` attribute.
        """
        module = cls._get_extension_module(extension_name)
        return getattr(module, "CHART_FORMAT")

    @classmethod
    def get_chart_function(cls, extension_name: str, route: str) -> Callable:
        """
        Given an extension name and a route, it returns the chart function.
        The module must contain the given route.
        """
        module = cls._get_extension_module(extension_name)
        return getattr(module, route)

    def chart(
        self,
        user_settings: UserSettings,
        system_settings: SystemSettings,
        route: str,
        command_output_item: Generic[T],
        **kwargs,
    ):
        """
        If the charting extension is not installed, an error is raised.
        Otherwise, a charting function will be retrieved and executed from the user's preferred charting extension.
        This function assumes that, in order to successfully retrieve the charting function,
        the charting extension uses the following naming convention to convert routes into charting functions:
            - Route: `/stocks/load`
            - Charting function: `stocks_load()`
            - Route: `/ta/ema`
            - Charting function: `ta_ema()`
        Note that the route should be in its original format, since it will be converted inside this function.
        Parameters
        ----------
        user_settings : UserSettings
            User settings.
        route : str
            Route name, example: `/stocks/load`.
        command_output_item
            Command output item.
        Returns
        -------
        Chart
            Chart object.
        """
        charting_settings = ChartingSettings(user_settings, system_settings)

        self._charting_extension = user_settings.preferences.charting_extension
        self._charting_extension_installed = self.check_charting_extension_installed(
            self._charting_extension
        )

        if not self._charting_extension_installed:
            raise ChartingManagerError(
                f"Charting extension {self._charting_extension} is not installed"
            )

        if self._charting_extension == "openbb_charting":
            from openbb_charting.core.backend import (  # pylint: disable=import-outside-toplevel
                create_backend,
                get_backend,
            )

            create_backend(charting_settings=charting_settings)
            get_backend().start()  # TODO: Add debug mode here

        chart_format = self.get_chart_format(self._charting_extension)

        adjusted_route = route.replace("/", "_")[1:]
        charting_function = self.get_chart_function(
            self._charting_extension, adjusted_route
        )

        kwargs["command_output_item"] = command_output_item
        kwargs["charting_settings"] = charting_settings

        return Chart(
            content=charting_function(**kwargs),
            format=chart_format,
        )
