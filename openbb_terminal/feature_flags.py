# IMPORTATION STANDARD
import os
import os.path

# IMPORTATION THIRDPARTY
import i18n

from openbb_terminal.base_helpers import load_env_vars, strtobool
from openbb_terminal.core.config import paths_helper

# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    USER_DATA_SOURCES_DEFAULT_FILE,
)

paths_helper.init_userdata()

# pylint: disable=no-member,c-extension-no-member

try:
    __import__("git")
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True

# Sync with OpenBB server
SYNC_ENABLED = load_env_vars("OPENBB_SYNC_ENABLED", strtobool, True, "featflags")

# Always overwrite exported files
FILE_OVERWITE = load_env_vars("OPENBB_FILE_OVERWRITE", strtobool, False, "featflags")

# Retry unknown commands with `load`
RETRY_WITH_LOAD = load_env_vars("OPENBB_RETRY_WITH_LOAD", strtobool, False, "featflags")

# Use tabulate to print dataframes
USE_TABULATE_DF = load_env_vars("OPENBB_USE_TABULATE_DF", strtobool, True, "featflags")

# Use clear console after each command
USE_CLEAR_AFTER_CMD = load_env_vars(
    "OPENBB_USE_CLEAR_AFTER_CMD", strtobool, False, "featflags"
)

# Use coloring features
USE_COLOR = load_env_vars("OPENBB_USE_COLOR", strtobool, True, "featflags")

# Add date and time to command line
USE_DATETIME = load_env_vars("OPENBB_USE_DATETIME", strtobool, True, "featflags")

# Enable interactive matplotlib mode
USE_ION = load_env_vars("OPENBB_USE_ION", strtobool, True, "featflags")

# Enable watermark in the figures
USE_WATERMARK = load_env_vars("OPENBB_USE_WATERMARK", strtobool, True, "featflags")

# Enable command and source in the figures
USE_CMD_LOCATION_FIGURE = load_env_vars(
    "OPENBB_USE_CMD_LOCATION_FIGURE", strtobool, True, "featflags"
)

# Enable Prompt Toolkit
USE_PROMPT_TOOLKIT = load_env_vars(
    "OPENBB_USE_PROMPT_TOOLKIT", strtobool, True, "featflags"
)

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = load_env_vars(
    "OPENBB_USE_PLOT_AUTOSCALING", strtobool, False, "featflags"
)

# Enable thoughts of the day
ENABLE_THOUGHTS_DAY = load_env_vars(
    "OPENBB_ENABLE_THOUGHTS_DAY", strtobool, False, "featflags"
)

# Quick exit for testing
ENABLE_QUICK_EXIT = load_env_vars(
    "OPENBB_ENABLE_QUICK_EXIT", strtobool, False, "featflags"
)

# Open report as HTML, otherwise notebook
OPEN_REPORT_AS_HTML = load_env_vars(
    "OPENBB_OPEN_REPORT_AS_HTML", strtobool, True, "featflags"
)

# Enable auto print_help when exiting menus
ENABLE_EXIT_AUTO_HELP = load_env_vars(
    "OPENBB_ENABLE_EXIT_AUTO_HELP", strtobool, True, "featflags"
)

# Remember contexts during session
REMEMBER_CONTEXTS = load_env_vars(
    "OPENBB_REMEMBER_CONTEXTS", strtobool, True, "featflags"
)

# Use the colorful rich terminal
ENABLE_RICH = load_env_vars("OPENBB_ENABLE_RICH", strtobool, True, "featflags")

# Use the colorful rich terminal
ENABLE_RICH_PANEL = load_env_vars(
    "OPENBB_ENABLE_RICH_PANEL", strtobool, True, "featflags"
)

# Check API KEYS before running a command
ENABLE_CHECK_API = load_env_vars(
    "OPENBB_ENABLE_CHECK_API", strtobool, True, "featflags"
)

# Send logs to data lake
LOG_COLLECTION = load_env_vars("OPENBB_LOG_COLLECT", strtobool, True, "featflags")

# Provide export folder path. If empty that means default.
EXPORT_FOLDER_PATH = str(os.getenv("OPENBB_EXPORT_FOLDER_PATH", ""))

# Toolbar hint
TOOLBAR_HINT = load_env_vars("OPENBB_TOOLBAR_HINT", strtobool, True, "featflags")

# Toolbar Twitter news
TOOLBAR_TWEET_NEWS = load_env_vars(
    "OPENBB_TOOLBAR_TWEET_NEWS", strtobool, False, "featflags"
)

# Toolbar Twitter news seconds between updates being checked
TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES = load_env_vars(
    "OPENBB_TOOLBAR_TWEET_NEWS_SECONDS_BETWEEN_UPDATES", int, 300, "settings"
)

# Toolbar Twitter news accounts to track
TOOLBAR_TWEET_NEWS_ACCOUNTS_TO_TRACK = load_env_vars(
    "OPENBB_TOOLBAR_TWEET_NEWS_ACCOUNTS_TO_TRACK",
    str,
    "WatcherGuru,unusual_whales,gurgavin,CBSNews",
    "settings",
)

# Toolbar Twitter news keywords to look for
TOOLBAR_TWEET_NEWS_KEYWORDS = load_env_vars(
    "OPENBB_TOOLBAR_TWEET_NEWS_KEYWORDS",
    str,
    "BREAKING,JUST IN",
    "settings",
)


# Toolbar Twitter news number of last tweets to read
TOOLBAR_TWEET_NEWS_NUM_LAST_TWEETS_TO_READ = load_env_vars(
    "OPENBB_TOOLBAR_TWEET_NEWS_NUM_LAST_TWEETS_TO_READ", int, 3, "settings"
)

# Select language to be used
USE_LANGUAGE = str(os.getenv("OPENBB_USE_LANGUAGE", "en"))

# File that contains a JSON dictionary of preferred sources for commands
PREFERRED_DATA_SOURCE_FILE = str(
    os.getenv(
        "OPENBB_PREFERRED_DATA_SOURCE_FILE",
        USER_DATA_SOURCES_DEFAULT_FILE,
    )
)

# Timezone
TIMEZONE = str(os.getenv("OPENBB_TIMEZONE", "America/New_York"))

# Select console flair (choose from config_terminal.py list)
USE_FLAIR = str(os.getenv("OPENBB_USE_FLAIR", ":openbb"))

# Guess file
GUESS_EASTER_EGG_FILE = str(
    os.getenv(
        "OPENBB_GUESS_EASTER_EGG_FILE",
        os.getcwd() + os.path.sep + "guess_game.json",
    )
)

try:
    if not WITH_GIT:
        import pkg_resources

        version = pkg_resources.get_distribution("OpenBB").version
    else:
        raise Exception("Using git")
except Exception:
    version = "2.5.1"
VERSION = str(os.getenv("OPENBB_VERSION", version))

# Select the terminal translation language
i18n_dict_location = MISCELLANEOUS_DIRECTORY / "i18n"
i18n.load_path.append(i18n_dict_location)
i18n.set("locale", USE_LANGUAGE)
i18n.set("filename_format", "{locale}.{format}")
