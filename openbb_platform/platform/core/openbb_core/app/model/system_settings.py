"""The OpenBB Platform System Settings."""
import json
import platform as pl  # I do this so that the import doesn't conflict with the variable name
from functools import partial
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_core.app.constants import (
    HOME_DIRECTORY,
    OPENBB_DIRECTORY,
    SYSTEM_SETTINGS_PATH,
    USER_SETTINGS_PATH,
)
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.version import VERSION

FrozenField = partial(Field, frozen=True)


class SystemSettings(Tagged):
    """System settings model."""

    # System section
    os: str = FrozenField(default=str(pl.system()))
    python_version: str = FrozenField(default=str(pl.python_version()))
    platform: str = FrozenField(default=str(pl.platform()))

    # OpenBB section
    # TODO: Get the version of the Platform from somewhere that's not pyproject.toml
    version: str = FrozenField(default=VERSION)
    home_directory: str = FrozenField(default=str(HOME_DIRECTORY))
    openbb_directory: str = FrozenField(default=str(OPENBB_DIRECTORY))
    user_settings_path: str = FrozenField(default=str(USER_SETTINGS_PATH))
    system_settings_path: str = FrozenField(default=str(SYSTEM_SETTINGS_PATH))

    # Logging section
    logging_app_name: Literal["platform"] = FrozenField(default="platform")
    logging_commit_hash: Optional[str] = FrozenField(default=None)
    logging_frequency: Literal["D", "H", "M", "S"] = FrozenField(default="H")
    logging_handlers: List[str] = FrozenField(default_factory=lambda: ["file"])
    logging_rolling_clock: bool = FrozenField(default=False)
    logging_verbosity: int = FrozenField(default=20)
    logging_sub_app: Literal["python", "api", "pro"] = FrozenField(default="python")
    logging_suppress: bool = FrozenField(default=False)
    log_collect: bool = FrozenField(default=True)

    # Others
    test_mode: bool = FrozenField(default=False)
    headless: bool = FrozenField(default=False)

    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @staticmethod
    def create_empty_json(path: Path) -> None:
        """Create an empty JSON file."""
        path.write_text(json.dumps({}), encoding="utf-8")

    @model_validator(mode="after")
    @classmethod
    def create_openbb_directory(cls, values: "SystemSettings") -> "SystemSettings":
        """Create the OpenBB directory if it doesn't exist."""
        obb_dir = Path(values.openbb_directory).resolve()
        user_settings = Path(values.user_settings_path).resolve()
        system_settings = Path(values.system_settings_path).resolve()
        obb_dir.mkdir(parents=True, exist_ok=True)

        for path in [user_settings, system_settings]:
            if not path.exists():
                cls.create_empty_json(path)

        return values

    @model_validator(mode="after")
    @classmethod
    def validate_posthog_handler(cls, values: "SystemSettings") -> "SystemSettings":
        """If the user has enabled log collection, then we need to add the Posthog."""
        if (
            not any([values.test_mode, values.logging_suppress])
            and values.log_collect
            and "posthog" not in values.logging_handlers
        ):
            values.logging_handlers.append("posthog")

        return values

    @field_validator("logging_handlers")
    @classmethod
    def validate_logging_handlers(cls, v):
        """Validate the logging handlers."""
        for value in v:
            if value not in ["stdout", "stderr", "noop", "file", "posthog"]:
                raise ValueError("Invalid logging handler")
        return v
