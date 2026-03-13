"""Settings model."""

from enum import Enum
from typing import Any, Literal

from dotenv import dotenv_values, set_key
from openbb_cli.config.constants import AVAILABLE_FLAIRS, ENV_FILE_SETTINGS
from openbb_core.app.version import get_package_version
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pytz import all_timezones

VERSION = get_package_version("openbb-cli")


class SettingGroups(Enum):
    """Setting types."""

    feature_flags = "feature_flag"
    preferences = "preference"


class Settings(BaseModel):
    """Settings model."""

    # Platform CLI version
    VERSION: str = VERSION

    # DEVELOPMENT FLAGS
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    DEV_BACKEND: bool = False

    # OPENBB
    HUB_URL: str = "https://my.openbb.co"
    BASE_URL: str = "https://payments.openbb.co"

    # GENERAL
    PREVIOUS_USE: bool = False

    # FEATURE FLAGS
    FILE_OVERWRITE: bool = Field(
        default=False,
        description="whether to overwrite Excel files if they already exists",
        json_schema_extra={
            "command": "overwrite",
            "group": SettingGroups.feature_flags.value,
        },
    )
    SHOW_VERSION: bool = Field(
        default=True,
        description="whether to show the version in the bottom right corner",
        json_schema_extra={
            "command": "version",
            "group": SettingGroups.feature_flags.value,
        },
    )
    USE_INTERACTIVE_DF: bool = Field(
        default=True,
        description="display tables in interactive window",
        json_schema_extra={
            "command": "interactive",
            "group": SettingGroups.feature_flags.value,
        },
    )
    USE_CLEAR_AFTER_CMD: bool = Field(
        default=False,
        description="clear console after each command",
        json_schema_extra={
            "command": "cls",
            "group": SettingGroups.feature_flags.value,
        },
    )
    USE_DATETIME: bool = Field(
        default=True,
        description="whether to show the date and time before the flair",
        json_schema_extra={
            "command": "datetime",
            "group": SettingGroups.feature_flags.value,
        },
    )
    USE_PROMPT_TOOLKIT: bool = Field(
        default=True,
        description="enable prompt toolkit (autocomplete and history)",
        json_schema_extra={
            "command": "promptkit",
            "group": SettingGroups.feature_flags.value,
        },
    )
    ENABLE_EXIT_AUTO_HELP: bool = Field(
        default=True,
        description="automatically print help when quitting menu",
        json_schema_extra={
            "command": "exithelp",
            "group": SettingGroups.feature_flags.value,
        },
    )
    ENABLE_RICH_PANEL: bool = Field(
        default=True,
        description="enable colorful rich CLI panel",
        json_schema_extra={
            "command": "richpanel",
            "group": SettingGroups.feature_flags.value,
        },
    )
    TOOLBAR_HINT: bool = Field(
        default=True,
        description="displays usage hints in the bottom toolbar",
        json_schema_extra={
            "command": "tbhint",
            "group": SettingGroups.feature_flags.value,
        },
    )
    SHOW_MSG_OBBJECT_REGISTRY: bool = Field(
        default=False,
        description="show obbject registry message after a new result is added",
        json_schema_extra={
            "command": "obbject_msg",
            "group": SettingGroups.feature_flags.value,
        },
    )

    # PREFERENCES
    TIMEZONE: Literal[tuple(all_timezones)] = Field(  # type: ignore[valid-type]
        default="America/New_York",
        description="pick timezone",
        json_schema_extra={
            "command": "timezone",
            "group": SettingGroups.preferences.value,
        },
    )
    FLAIR: Literal[tuple(AVAILABLE_FLAIRS)] = Field(  # type: ignore[valid-type]
        default=":openbb",
        description="choose flair icon",
        json_schema_extra={
            "command": "flair",
            "group": SettingGroups.preferences.value,
        },
    )
    N_TO_KEEP_OBBJECT_REGISTRY: int = Field(
        default=10,
        description="define the maximum number of obbjects allowed in the registry",
        json_schema_extra={
            "command": "obbject_res",
            "group": SettingGroups.preferences.value,
        },
    )
    N_TO_DISPLAY_OBBJECT_REGISTRY: int = Field(
        default=5,
        description="define the maximum number of cached results to display on the help menu",
        json_schema_extra={
            "command": "obbject_display",
            "group": SettingGroups.preferences.value,
        },
    )
    RICH_STYLE: str = Field(
        default="dark",
        description="apply a custom rich style to the CLI",
        json_schema_extra={
            "command": "console_style",
            "group": SettingGroups.preferences.value,
        },
    )
    ALLOWED_NUMBER_OF_ROWS: int = Field(
        default=20,
        description="number of rows to show (when not using interactive tables).",
        json_schema_extra={
            "command": "n_rows",
            "group": SettingGroups.preferences.value,
        },
    )
    ALLOWED_NUMBER_OF_COLUMNS: int = Field(
        default=5,
        description="number of columns to show (when not using interactive tables).",
        json_schema_extra={
            "command": "n_cols",
            "group": SettingGroups.preferences.value,
        },
    )

    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @model_validator(mode="before")
    @classmethod
    def from_env(cls, values: dict) -> dict:
        """Load settings from .env."""
        settings = {}
        settings.update(dotenv_values(ENV_FILE_SETTINGS))
        settings.update(values)
        filtered = {k.replace("OPENBB_", ""): v for k, v in settings.items()}
        return filtered

    def set_item(self, key: str, value: Any) -> None:
        """Set an item in the model and save to .env."""
        setattr(self, key, value)
        set_key(str(ENV_FILE_SETTINGS), "OPENBB_" + key, str(value))
