from pathlib import Path
from typing import Optional

from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.app.model.system_settings import SystemSettings


class SystemService:
    SYSTEM_SETTINGS_PATH = Path(OPENBB_DIRECTORY, "system_settings.json")
    SYSTEM_SETTINGS_ALLOWED_FIELD_SET = {"run_in_isolation", "dbms_uri"}

    @classmethod
    def read_default_system_settings(
        cls, path: Optional[Path] = None
    ) -> SystemSettings:
        path = path or cls.SYSTEM_SETTINGS_PATH

        if path.exists():
            with path.open(mode="r") as file:
                system_settings_json = file.read()

            system_settings = SystemSettings.parse_raw(system_settings_json)
        else:
            system_settings = SystemSettings()

        return system_settings

    @classmethod
    def write_default_system_settings(
        cls,
        system_settings: SystemSettings,
        path: Optional[Path] = None,
    ) -> None:
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
        return self._system_settings

    @system_settings.setter
    def system_settings(self, system_settings: SystemSettings) -> None:
        self._system_settings = system_settings

    def refresh_system_settings(self) -> SystemSettings:
        self._system_settings = self.read_default_system_settings()

        return self._system_settings
