from importlib import import_module
from typing import Callable, Generic, Optional, Tuple, TypeVar

import pkg_resources

from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.charts.chart import Chart, ChartFormat
from openbb_core.app.model.charts.charting_settings import ChartingSettings
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService

T = TypeVar("T")

POETRY_PLUGIN = "openbb_core_extension"


class ChartingManagerError(Exception):
    pass


class ChartingManager(metaclass=SingletonMeta):
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
        system_settings: Optional[SystemSettings] = None,
    ) -> None:
        user_settings = user_settings or UserService().read_default_user_settings()
        self._system_settings = (
            system_settings or SystemService().read_default_system_settings()
        )

        self._charting_settings = ChartingSettings(user_settings, system_settings)
        self._charting_extension = user_settings.preferences.charting_extension
        self._charting_extension_installed = self.check_charting_extension_installed(
            self._charting_extension
        )

    @property
    def charting_settings(self) -> ChartingSettings:
        return self._charting_settings

    @charting_settings.setter
    def charting_settings(self, value: Tuple[SystemSettings, UserSettings]):
        system_settings, user_settings = value
        self._charting_settings = ChartingSettings(
            user_settings=user_settings,
            system_settings=system_settings,
        )

    @staticmethod
    def check_charting_extension_installed(
        charting_extension: str, plugin: str = POETRY_PLUGIN
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
        adjusted_route = route.replace("/", "_")[1:]
        module = cls._get_extension_module(extension_name)
        return getattr(module, adjusted_route)

    @staticmethod
    def handle_backend(charting_extension: str, charting_settings: ChartingSettings):
        """
        Handles the backend of the given charting extension.
        This function that the module expose in its root (__init__.py) the following functions:
            - `create_backend(charting_settings: ChartingSettings)`
            - `get_backend()`

        Parameters
        ----------
        charting_extension : str
            Charting extension name.
        charting_settings : ChartingSettings
            Charting settings.
        """
        # Dynamically import the backend module
        backend_module = import_module(charting_extension)

        create_backend_func = getattr(backend_module, "create_backend")
        get_backend_func = getattr(backend_module, "get_backend")

        create_backend_func(charting_settings=charting_settings)
        get_backend_func().start(debug=charting_settings.debug_mode)

    def to_plotly_json(self, **kwargs) -> str:
        """
        Returns the plotly json representation of the chart.
        """
        if not self._charting_extension_installed:
            raise ChartingManagerError(
                f"Charting extension `{self._charting_extension}` is not installed"
            )
        self.handle_backend(self._charting_extension, self._charting_settings)

        # Dynamically import the charting module
        backend_module = import_module(self._charting_extension)
        # Get the plotly json function from the charting module
        to_plotly_json_func = getattr(backend_module, "to_plotly_json")
        # Add the charting settings to the kwargs
        kwargs["charting_settings"] = self._charting_settings

        return to_plotly_json_func(**kwargs)

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
        self._charting_settings = ChartingSettings(user_settings, system_settings)
        self._charting_extension = user_settings.preferences.charting_extension
        self._charting_extension_installed = self.check_charting_extension_installed(
            self._charting_extension
        )

        if not self._charting_extension_installed:
            raise ChartingManagerError(
                f"Charting extension `{self._charting_extension}` is not installed"
            )

        self.handle_backend(self._charting_extension, self._charting_settings)

        kwargs["command_output_item"] = command_output_item
        kwargs["charting_settings"] = self._charting_settings

        charting_function = self.get_chart_function(self._charting_extension, route)
        fig, content = charting_function(**kwargs)

        return Chart(
            content=content,
            format=self.get_chart_format(self._charting_extension),
            fig=fig,
        )
