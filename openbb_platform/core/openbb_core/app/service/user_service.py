"""User service."""

import json
from collections.abc import MutableMapping
from functools import reduce
from pathlib import Path
from typing import Any

from openbb_core.app.constants import USER_SETTINGS_PATH
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings


class UserService(metaclass=SingletonMeta):
    """User service."""

    USER_SETTINGS_PATH = USER_SETTINGS_PATH
    USER_SETTINGS_ALLOWED_FIELD_SET = {"credentials", "preferences", "defaults"}

    def __init__(
        self,
        default_user_settings: UserSettings | None = None,
    ):
        """Initialize user service."""
        self._default_user_settings = default_user_settings or self.read_from_file()

    @classmethod
    def read_from_file(cls, path: Path | None = None) -> UserSettings:
        """Read user settings from json into UserSettings."""
        path = path or cls.USER_SETTINGS_PATH

        return (
            UserSettings.model_validate(json.loads(path.read_text(encoding="utf-8")))
            if path.exists()
            else UserSettings()
        )

    @classmethod
    def write_to_file(
        cls,
        user_settings: UserSettings,
        path: Path | None = None,
    ) -> None:
        """Write user settings to json."""
        path = path or cls.USER_SETTINGS_PATH
        user_settings_json = user_settings.model_dump_json(
            indent=4, include=cls.USER_SETTINGS_ALLOWED_FIELD_SET, exclude_defaults=True
        )
        path.write_text(user_settings_json, encoding="utf-8")

    @staticmethod
    def _merge_dicts(list_of_dicts: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge a list of dictionaries."""

        def recursive_merge(d1: dict, d2: dict) -> dict:
            """Recursively merge dict d2 into dict d1 if d2 is value is not None."""
            for k, v in d1.items():
                if k in d2 and all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                    d2[k] = recursive_merge(v, d2[k])

            d3 = d1.copy()
            d3.update((k, v) for k, v in d2.items() if v is not None)
            return d3

        result: dict[str, Any] = {}
        for d in list_of_dicts:
            result = reduce(recursive_merge, (result, d))
        return result

    @property
    def default_user_settings(self) -> UserSettings:
        """Return default user settings."""
        return self._default_user_settings

    @default_user_settings.setter
    def default_user_settings(self, default_user_settings: UserSettings) -> None:
        """Set default user settings."""
        self._default_user_settings = default_user_settings
