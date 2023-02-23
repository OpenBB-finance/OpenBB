import os
from pydantic import PositiveInt
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt

from openbb_terminal.core.config.paths import (
    USER_DATA_SOURCES_DEFAULT_FILE,
    USER_EXPORTS_DIRECTORY,
)


@dataclass(config=dict(validate_assignment=True))
class PreferencesModel:
    """Data model for preferences."""

    # BACKEND
    # Examples:
    # "tkAgg" - This uses the tkinter library.  If unsure, set to this
    # "module://backend_interagg" - This is what pycharm defaults to in Scientific Mode
    # "MacOSX" - Mac default.  Does not work with backtesting
    # "Qt5Agg" - This requires the PyQt5 package is installed
    # See more: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-builtin-backends
    PLOT_BACKEND: str = None
    PLOT_DPI: PositiveInt = 100

    # FEATURE FLAGS
    SYNC_ENABLED: bool = True
    FILE_OVERWITE: bool = False
    RETRY_WITH_LOAD: bool = False
    USE_TABULATE_DF: bool = True
    USE_CLEAR_AFTER_CMD: bool = False
    USE_COLOR: bool = True
    USE_DATETIME: bool = True
    USE_ION: bool = True  # Enable interactive matplotlib mode: change variable name to be more descriptive and delete comment above
    USE_WATERMARK: bool = True
    USE_CMD_LOCATION_FIGURE: bool = True  # Enable command and source in the figures: change variable name to be more descriptive and delete comment above
    USE_PROMPT_TOOLKIT: bool = True
    USE_PLOT_AUTOSCALING: bool = False
    ENABLE_THOUGHTS_DAY: bool = False
    ENABLE_QUICK_EXIT: bool = False
    OPEN_REPORT_AS_HTML: bool = True
    ENABLE_EXIT_AUTO_HELP: bool = True
    REMEMBER_CONTEXTS: bool = True
    ENABLE_RICH: bool = True
    ENABLE_RICH_PANEL: bool = True
    ENABLE_CHECK_API: bool = True
    LOG_COLLECTION: bool = True
    TOOLBAR_HINT: bool = True
    TOOLBAR_TWEET_NEWS: bool = False
    TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES: PositiveInt = 300
    TOOLBAR_TWEET_NEWS_ACCOUNTS_TO_TRACK: str = (
        "WatcherGuru,unusual_whales,gurgavin,CBSNews"
    )
    TOOLBAR_TWEET_NEWS_KEYWORDS: str = "BREAKING,JUST IN"
    TOOLBAR_TWEET_NEWS_NUM_LAST_TWEETS_TO_READ: PositiveInt = 3
    USE_LANGUAGE: str = "en"
    PREFERRED_DATA_SOURCE_FILE: str = str(USER_DATA_SOURCES_DEFAULT_FILE)
    TIMEZONE: str = "America/New_York"
    FLAIR: str = ":openbb"
    GUESS_EASTER_EGG_FILE: str = os.getcwd() + os.path.sep + "guess_game.json"
    EXPORT_FOLDER_PATH: str = str(USER_EXPORTS_DIRECTORY)
