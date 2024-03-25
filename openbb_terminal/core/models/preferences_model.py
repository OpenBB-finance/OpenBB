
from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes, disable=no-member, useless-parent-delegation


@dataclass(config=dict(validate_assignment=True, frozen=True))
class PreferencesModel(BaseModel):
    """Data model for preferences."""

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
