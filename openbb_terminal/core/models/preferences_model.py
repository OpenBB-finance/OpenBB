import os
from typing import Literal, Optional

from pydantic import NonNegativeInt, PositiveFloat, PositiveInt
from pydantic.dataclasses import dataclass

from openbb_terminal.core.config.paths import (
    HOME_DIRECTORY,
)
from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes, disable=no-member, useless-parent-delegation


@dataclass(config=dict(validate_assignment=True, frozen=True))
class PreferencesModel(BaseModel):
    """Data model for preferences."""

    # PLOT
    # Plot backend
    # Examples:
    # "tkAgg" - This uses the tkinter library.  If unsure, set to this
    # "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
    # "MacOSX" - Mac default.  Does not work with backtesting
    # "Qt5Agg" - This requires the PyQt5 package is installed
    # See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends
    PLOT_BACKEND: Optional[str] = None
    PLOT_DPI: PositiveInt = 100
    PLOT_HEIGHT: PositiveInt = 500
    PLOT_WIDTH: PositiveInt = 800
    PLOT_HEIGHT_PERCENTAGE: PositiveFloat = 50.0
    PLOT_WIDTH_PERCENTAGE: PositiveFloat = 70.0
    # Whether to open plot image exports after they are created
    PLOT_OPEN_EXPORT: bool = False
    # Use interactive window to display plots
    PLOT_ENABLE_PYWRY: bool = True
    PLOT_PYWRY_WIDTH: PositiveInt = 1400
    PLOT_PYWRY_HEIGHT: PositiveInt = 762

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

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
