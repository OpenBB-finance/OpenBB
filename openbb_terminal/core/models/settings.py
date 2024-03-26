from pydantic.dataclasses import dataclass
from openbb_terminal.core.models import BaseModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class Settings(BaseModel):
    """Data model for settings."""

    # Platform CLI version
    VERSION: str = "4.0.0"

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

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
