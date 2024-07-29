"""Charting settings."""

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from openbb_core.app.logs.utils.utils import get_app_id
from openbb_core.env import Env

if TYPE_CHECKING:
    from openbb_core.app.model.system_settings import SystemSettings
    from openbb_core.app.model.user_settings import UserSettings


# pylint: disable=too-many-instance-attributes
class ChartingSettings:
    """Charting settings."""

    def __init__(
        self,
        user_settings: Optional["UserSettings"] = None,
        system_settings: Optional["SystemSettings"] = None,
    ):
        """Initialize charting settings."""
        user_settings_module = importlib.import_module(
            "openbb_core.app.model.user_settings", "UserSettings"
        )
        system_settings_module = importlib.import_module(
            "openbb_core.app.model.system_settings", "SystemSettings"
        )

        UserSettings = user_settings_module.UserSettings
        SystemSettings = system_settings_module.SystemSettings
        user_settings = user_settings or UserSettings()
        system_settings = system_settings or SystemSettings()

        user_data_directory = (
            str(Path.home() / "OpenBBUserData")
            if not user_settings.preferences
            else user_settings.preferences.data_directory
        )

        # System
        self.log_collect: bool = system_settings.log_collect
        self.version: str = system_settings.version
        self.python_version: str = system_settings.python_version
        self.test_mode = system_settings.test_mode
        self.app_id: str = get_app_id(user_data_directory)
        self.debug_mode: bool = system_settings.debug_mode or Env().DEBUG_MODE
        self.headless: bool = system_settings.headless
        # User
        self.user_email: Optional[str] = getattr(
            user_settings.profile.hub_session, "email", None
        )
        self.user_uuid: Optional[str] = getattr(
            user_settings.profile.hub_session, "user_uuid", None
        )
        self.user_exports_directory = user_settings.preferences.export_directory
        self.user_styles_directory = user_settings.preferences.user_styles_directory
        # Theme
        self.chart_style: str = user_settings.preferences.chart_style
        self.table_style = user_settings.preferences.table_style
