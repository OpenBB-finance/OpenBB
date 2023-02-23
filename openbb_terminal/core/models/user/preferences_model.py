from typing import Literal
from pydantic import PositiveInt
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, PositiveFloat, NonNegativeInt


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
    PLOT_DPI: int = PositiveInt

    # FEATURE FLAGS

    # Sync with OpenBB server
    SYNC_ENABLED: bool = True

    # Always overwrite exported files
    FILE_OVERWITE: bool = False

    # Retry unknown commands with `load`
    RETRY_WITH_LOAD: bool = False

    # Use tabulate to print dataframes
    USE_TABULATE_DF: bool = True

    # Use clear console after each command
    USE_CLEAR_AFTER_CMD: bool = False

    # Use coloring features
    USE_COLOR: bool = True

    # Add date and time to command line
    USE_DATETIME: bool = True

    # Enable interactive matplotlib mode
    USE_ION: bool = True

    # Enable watermark in the figures
    USE_WATERMARK: bool = True

    # Enable command and source in the figures
    USE_CMD_LOCATION_FIGURE: bool = True

    # Enable Prompt Toolkit
    USE_PROMPT_TOOLKIT: bool = True

    # Enable plot autoscaling
    USE_PLOT_AUTOSCALING: bool = False

    # Enable thoughts of the day
    ENABLE_THOUGHTS_DAY: bool = False

    # Quick exit for testing
    ENABLE_QUICK_EXIT: bool = False

    # Open report as HTML, otherwise notebook
    OPEN_REPORT_AS_HTML: bool = True

    # Enable auto print_help when exiting menus
    ENABLE_EXIT_AUTO_HELP: bool = True

    # Remember contexts during session
    REMEMBER_CONTEXTS: bool = True

    # Use the colorful rich terminal
    ENABLE_RICH: bool = True

    # Use the colorful rich terminal
    ENABLE_RICH_PANEL: bool = True

    # Check API KEYS before running a command
    ENABLE_CHECK_API: bool = True

    # Send logs to data lake
    LOG_COLLECTION: bool = True

    # Toolbar hint
    TOOLBAR_HINT: bool = True

    # Toolbar Twitter news
    TOOLBAR_TWEET_NEWS: bool = False

    # Provide export folder path. If empty that means default.
    EXPORT_FOLDER_PATH = str(os.getenv("OPENBB_EXPORT_FOLDER_PATH", ""))

    # Toolbar Twitter news seconds between updates being checked
    TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES = "OPENBB_TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES", int, 300, "settings"

    # Toolbar Twitter news accounts to track
    TOOLBAR_TWEET_NEWS_ACCOUNTS_TO_TRACK: str = "WatcherGuru,unusual_whales,gurgavin,CBSNews"

    # Toolbar Twitter news keywords to look for
    TOOLBAR_TWEET_NEWS_KEYWORDS: str = "BREAKING,JUST IN"

    # Toolbar Twitter news number of last tweets to read
    TOOLBAR_TWEET_NEWS_NUM_LAST_TWEETS_TO_READ: PositiveInt = 3

    # Select language to be used
    USE_LANGUAGE: str = "en"

    # File that contains a JSON dictionary of preferred sources for commands
    PREFERRED_DATA_SOURCE_FILE = str(
        os.getenv(
            "OPENBB_PREFERRED_DATA_SOURCE_FILE",
            USER_DATA_SOURCES_DEFAULT_FILE,))

    # Timezone
    TIMEZONE = str(os.getenv("OPENBB_TIMEZONE", "America/New_York"))

    # Select console flair (choose from config_terminal.py list)
    FLAIR: str = ":openbb"

    # Guess file
    GUESS_EASTER_EGG_FILE = str(
        os.getenv(
            "OPENBB_GUESS_EASTER_EGG_FILE",
            os.getcwd() + os.path.sep + "guess_game.json",
        )
