"""Data model for settings."""

from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class Settings(BaseModel):  # pylint: disable=too-many-instance-attributes
    """Data model for settings."""

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
    ENABLE_QUICK_EXIT: bool = False
    ENABLE_EXIT_AUTO_HELP: bool = True
    REMEMBER_CONTEXTS: bool = True
    ENABLE_RICH_PANEL: bool = True
    TOOLBAR_HINT: bool = True

    # GENERAL
    TIMEZONE: str = "America/New_York"
    FLAIR: str = ":openbb"
    USE_LANGUAGE: str = "en"

    # STYLE
    RICH_STYLE: str = "dark"

    # OUTPUT
    ALLOWED_NUMBER_OF_ROWS: int = 366
    ALLOWED_NUMBER_OF_COLUMNS: int = 15

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        """Return string representation of model."""
        return super().__repr__()
