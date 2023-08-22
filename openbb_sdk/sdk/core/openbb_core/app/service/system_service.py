import json
from pathlib import Path
from typing import Optional

from openbb_core.app.constants import SYSTEM_SETTINGS_PATH
from openbb_core.app.model.system_settings import SystemSettings


class SystemService:
    """System service."""

    SYSTEM_SETTINGS_PATH = SYSTEM_SETTINGS_PATH
    SYSTEM_SETTINGS_ALLOWED_FIELD_SET = {
        "log_collect",
        "test_mode",
        "headless",
        "debug_mode",
        "dbms_uri",
    }

    @classmethod
    def read_default_system_settings(
        cls, path: Optional[Path] = None
    ) -> SystemSettings:
        """Read default system settings."""
        path = path or cls.SYSTEM_SETTINGS_PATH

        if path.exists():
            with path.open(mode="r") as file:
                system_settings_json = file.read()

            system_settings_dict = json.loads(system_settings_json)
            S = system_settings_dict.copy()
            for field in S:
                if field not in cls.SYSTEM_SETTINGS_ALLOWED_FIELD_SET:
                    del system_settings_dict[field]

            system_settings = SystemSettings.parse_obj(system_settings_dict)
        else:
            system_settings = SystemSettings()

        return system_settings

    @classmethod
    def write_default_system_settings(
        cls,
        system_settings: SystemSettings,
        path: Optional[Path] = None,
    ) -> None:
        """Write default system settings."""
        path = path or cls.SYSTEM_SETTINGS_PATH

        system_settings_json = system_settings.json(
            include=cls.SYSTEM_SETTINGS_ALLOWED_FIELD_SET,
            indent=4,
            sort_keys=True,
        )
        with path.open(mode="w") as file:
            file.write(system_settings_json)

    def __init__(
        self,
        path: Path = SYSTEM_SETTINGS_PATH,
    ):
        self._path = path
        self._system_settings = self.read_default_system_settings()

    @property
    def system_settings(self) -> SystemSettings:
        """Get system settings."""
        return self._system_settings

    @system_settings.setter
    def system_settings(self, system_settings: SystemSettings) -> None:
        """Set system settings."""
        self._system_settings = system_settings

    def refresh_system_settings(self) -> SystemSettings:
        """Refresh system settings."""
        self._system_settings = self.read_default_system_settings()

        return self._system_settings
