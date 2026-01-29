"""系统服务。"""

import hashlib
import json
from pathlib import Path

from openbb_core.app.constants import SYSTEM_SETTINGS_PATH
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.system_settings import SystemSettings


class SystemService(metaclass=SingletonMeta):
    """系统服务。"""

    SYSTEM_SETTINGS_PATH = SYSTEM_SETTINGS_PATH
    SYSTEM_SETTINGS_ALLOWED_FIELD_SET = {
        "test_mode",
        "headless",
        "logging_sub_app",
        "api_settings",
        "python_settings",
        "debug_mode",
        "logging_suppress",
        "allow_mutable_extensions",
        "allow_on_command_output",
    }

    PRO_VALIDATION_HASH = "300ac59fdcc8f899e0bc5c18cda8652220735da1a00e2af365efe9d8e5fe8306"  # pragma: allowlist secret

    def __init__(
        self,
        **kwargs,
    ):
        """初始化系统服务。"""
        self._system_settings = self._read_from_file(
            path=self.SYSTEM_SETTINGS_PATH, **kwargs
        )

    @classmethod
    def _compare_hash(cls, input_value, existing_hash: str | None = None):
        existing_hash = existing_hash or cls.PRO_VALIDATION_HASH

        hash_object = hashlib.sha256()
        hash_object.update(input_value.encode("utf-8"))
        hashed_input = hash_object.hexdigest()

        return hashed_input == existing_hash

    @classmethod
    def _read_from_file(cls, path: Path | None = None, **kwargs) -> SystemSettings:
        """读取默认系统设置。"""
        path = path or cls.SYSTEM_SETTINGS_PATH

        if path.exists():
            with path.open(mode="r") as file:
                system_settings_json = file.read()

            system_settings_dict = json.loads(system_settings_json)

            S = system_settings_dict.copy()
            for field in S:
                if field not in cls.SYSTEM_SETTINGS_ALLOWED_FIELD_SET:
                    del system_settings_dict[field]
                elif field == "logging_sub_app":
                    if cls._compare_hash(system_settings_dict[field]):
                        system_settings_dict[field] = "pro"
                        kwargs.pop(field, None)
                    else:
                        del system_settings_dict[field]

            system_settings_dict.update(kwargs)
            system_settings = SystemSettings.model_validate(system_settings_dict)
        else:
            system_settings = SystemSettings.model_validate(kwargs)

        return system_settings

    @classmethod
    def write_to_file(
        cls,
        system_settings: SystemSettings,
        path: Path | None = None,
    ) -> None:
        """写入默认系统设置。"""
        path = path or cls.SYSTEM_SETTINGS_PATH

        system_settings_json = system_settings.model_dump_json(
            indent=4,
            include=cls.SYSTEM_SETTINGS_ALLOWED_FIELD_SET,
            exclude_defaults=True,
        )
        with path.open(mode="w") as file:
            file.write(system_settings_json)

    @property
    def system_settings(self) -> SystemSettings:
        """获取系统设置。"""
        return self._system_settings

    @system_settings.setter
    def system_settings(self, system_settings: SystemSettings) -> None:
        """设置系统设置。"""
        self._system_settings = system_settings

    def refresh_system_settings(self) -> SystemSettings:
        """刷新系统设置。"""
        self._system_settings = self._read_from_file()

        return self._system_settings
