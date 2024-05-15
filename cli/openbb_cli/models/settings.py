"""Settings model"""

from typing import Any

from dotenv import dotenv_values, set_key
from openbb_cli.config.constants import ENV_FILE_SETTINGS
from pydantic import BaseModel, ConfigDict, model_validator


class Settings(BaseModel):
    """Settings model."""

    # Platform CLI version
    VERSION: str = "1.0.0"

    # DEVELOPMENT FLAGS
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    DEV_BACKEND: bool = False

    # FEATURE FLAGS
    FILE_OVERWRITE: bool = False
    SHOW_VERSION: bool = True
    USE_INTERACTIVE_DF: bool = True
    USE_CLEAR_AFTER_CMD: bool = False
    USE_DATETIME: bool = True
    USE_PROMPT_TOOLKIT: bool = True
    ENABLE_EXIT_AUTO_HELP: bool = True
    REMEMBER_CONTEXTS: bool = True
    ENABLE_RICH_PANEL: bool = True
    TOOLBAR_HINT: bool = True
    SHOW_MSG_OBBJECT_REGISTRY: bool = False

    # GENERAL
    TIMEZONE: str = "America/New_York"
    FLAIR: str = ":openbb"
    PREVIOUS_USE: bool = False
    N_TO_KEEP_OBBJECT_REGISTRY: int = 10
    N_TO_DISPLAY_OBBJECT_REGISTRY: int = 5

    # STYLE
    RICH_STYLE: str = "dark"

    # OUTPUT
    ALLOWED_NUMBER_OF_ROWS: int = 20
    ALLOWED_NUMBER_OF_COLUMNS: int = 5

    # OPENBB
    HUB_URL: str = "https://my.openbb.co"
    BASE_URL: str = "https://payments.openbb.co"

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
