"""The OpenBB Platform System Settings."""

import json
import platform as pl  # I do this so that the import doesn't conflict with the variable name
from pathlib import Path
from typing import List, Literal, Optional

from openbb_core.app.constants import (
    HOME_DIRECTORY,
    OPENBB_DIRECTORY,
    SYSTEM_SETTINGS_PATH,
    USER_SETTINGS_PATH,
)
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.api_settings import APISettings
from openbb_core.app.model.python_settings import PythonSettings
from openbb_core.app.version import CORE_VERSION, VERSION
from pydantic import ConfigDict, Field, field_validator, model_validator


class SystemSettings(Tagged):
    """System settings model."""

    # System section
    os: str = str(pl.system())
    python_version: str = str(pl.python_version())
    platform: str = str(pl.platform())

    # OpenBB section
    version: str = VERSION
    core: str = CORE_VERSION
    home_directory: str = str(HOME_DIRECTORY)
    openbb_directory: str = str(OPENBB_DIRECTORY)
    user_settings_path: str = str(USER_SETTINGS_PATH)
    system_settings_path: str = str(SYSTEM_SETTINGS_PATH)

    # Logging section
    logging_app_name: Literal["platform"] = "platform"
    logging_commit_hash: Optional[str] = None
    logging_frequency: Literal["D", "H", "M", "S"] = "H"
    logging_handlers: List[str] = Field(default_factory=lambda: ["file"])
    logging_rolling_clock: bool = False
    logging_verbosity: int = 20
    logging_sub_app: Literal["python", "api", "pro", "cli"] = "python"
    logging_suppress: bool = True

    # API section
    api_settings: APISettings = Field(default_factory=APISettings)

    # Python section
    python_settings: PythonSettings = Field(default_factory=PythonSettings)

    # Others
    debug_mode: bool = False
    test_mode: bool = False
    headless: bool = False

    model_config = ConfigDict(validate_assignment=True, frozen=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @staticmethod
    def create_json(path: Path, template: Optional[dict] = None) -> None:
        """Create an empty JSON file."""
        path.write_text(json.dumps(obj=template or {}, indent=4), encoding="utf-8")

    # TODO: Figure out why this works only opposite to what the docs say
    # https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    # based on docs first argument should be self, but it works only with cls
    @model_validator(mode="after")  # type: ignore
    @classmethod
    def create_openbb_directory(cls, values: "SystemSettings") -> "SystemSettings":
        """Create the OpenBB directory if it doesn't exist."""
        obb_dir = Path(values.openbb_directory).resolve()
        user_settings = Path(values.user_settings_path).resolve()
        system_settings = Path(values.system_settings_path).resolve()
        obb_dir.mkdir(parents=True, exist_ok=True)

        if not user_settings.exists():
            cls.create_json(
                user_settings,
                {"credentials": {}, "preferences": {}, "defaults": {"commands": {}}},
            )

        if not system_settings.exists():
            cls.create_json(system_settings, {})

        return values

    @field_validator("logging_handlers")
    @classmethod
    def validate_logging_handlers(cls, v):
        """Validate the logging handlers."""
        for value in v:
            if value not in ["stdout", "stderr", "noop", "file"]:
                raise ValueError("Invalid logging handler")
        return v
