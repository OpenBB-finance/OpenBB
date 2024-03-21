import os
from typing import Literal

from pydantic import NonNegativeInt, PositiveInt
from pydantic.dataclasses import dataclass

from openbb_terminal.core.config.paths import HOME_DIRECTORY
from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes, disable=no-member, useless-parent-delegation


@dataclass(config=dict(validate_assignment=True, frozen=True))
class PreferencesModel(BaseModel):
    """Data model for preferences."""

    # FEATURE FLAGS
    FILE_OVERWRITE: bool = False
    SHOW_VERSION: bool = True
    RETRY_WITH_LOAD: bool = False
    USE_TABULATE_DF: bool = True
    # Use interactive window to display dataframes with options to sort, filter, etc.
    USE_INTERACTIVE_DF: bool = True
    USE_CLEAR_AFTER_CMD: bool = False
    USE_DATETIME: bool = True
    # Enable interactive matplotlib mode: change variable name to be more descriptive and delete comment
    USE_PROMPT_TOOLKIT: bool = True
    USE_PLOT_AUTOSCALING: bool = False
    ENABLE_THOUGHTS_DAY: bool = False
    ENABLE_QUICK_EXIT: bool = False
    OPEN_REPORT_AS_HTML: bool = True
    ENABLE_EXIT_AUTO_HELP: bool = True
    REMEMBER_CONTEXTS: bool = True
    ENABLE_RICH_PANEL: bool = True
    ENABLE_CHECK_API: bool = True
    TOOLBAR_HINT: bool = True

    # GENERAL
    PREVIOUS_USE: bool = False
    TIMEZONE: str = "America/New_York"
    FLAIR: str = ":bug"
    USE_LANGUAGE: str = "en"
    REQUEST_TIMEOUT: PositiveInt = 5
    MONITOR: NonNegativeInt = 0

    # STYLE
    MPL_STYLE: str = "dark"
    PMF_STYLE: str = "dark"
    RICH_STYLE: str = "dark"
    CHART_STYLE: Literal["dark", "light"] = "dark"
    TABLE_STYLE: Literal["dark", "light"] = "dark"

    # PATHS
    GUESS_EASTER_EGG_FILE: str = os.getcwd() + os.path.sep + "guess_game.json"
    USER_DATA_DIRECTORY = HOME_DIRECTORY / "OpenBBUserData"
    USER_DATA_SOURCES_FILE: str = str(USER_DATA_DIRECTORY / "sources" / "sources.json")
    USER_EXPORTS_DIRECTORY = USER_DATA_DIRECTORY / "exports"
    USER_CUSTOM_IMPORTS_DIRECTORY = USER_DATA_DIRECTORY / "custom_imports"
    USER_PORTFOLIO_DATA_DIRECTORY = USER_DATA_DIRECTORY / "portfolio"
    USER_ROUTINES_DIRECTORY = USER_DATA_DIRECTORY / "routines"
    USER_PRESETS_DIRECTORY = USER_DATA_DIRECTORY / "presets"
    USER_REPORTS_DIRECTORY = USER_DATA_DIRECTORY / "reports"
    USER_CUSTOM_REPORTS_DIRECTORY = USER_DATA_DIRECTORY / "reports" / "custom reports"
    USER_FORECAST_MODELS_DIRECTORY = USER_DATA_DIRECTORY / "exports" / "forecast_models"
    USER_FORECAST_WHISPER_DIRECTORY = USER_DATA_DIRECTORY / "exports" / "whisper"
    USER_STYLES_DIRECTORY = USER_DATA_DIRECTORY / "styles"
    USER_COMPANIES_HOUSE_DIRECTORY = USER_DATA_DIRECTORY / "companies_house"

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
