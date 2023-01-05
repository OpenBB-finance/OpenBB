# IMPORTATION STANDARD
import os
import os.path

# IMPORTATION THIRDPARTY
from dotenv import load_dotenv
import i18n

# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_DATA_SOURCES_DEFAULT_FILE,
    USER_ENV_FILE,
)
from openbb_terminal.core.config import paths_helper
from openbb_terminal.base_helpers import load_env_vars, strtobool

paths_helper.init_userdata()

# pylint: disable=no-member,c-extension-no-member

load_dotenv(USER_ENV_FILE)
load_dotenv(REPOSITORY_ENV_FILE, override=True)
load_dotenv(PACKAGE_ENV_FILE, override=True)

try:
    __import__("git")
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True


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

# Select console flair (choose from config_terminal.py list)
USE_FLAIR = str(os.getenv("OPENBB_USE_FLAIR", ":openbb"))

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

# Select language to be used
USE_LANGUAGE = str(os.getenv("OPENBB_USE_LANGUAGE", "en"))

# File that contains a JSON dictionary of preferred sources for commands
PREFERRED_DATA_SOURCE_FILE = str(
    os.getenv(
        "OPENBB_PREFERRED_DATA_SOURCE_FILE",
        USER_DATA_SOURCES_DEFAULT_FILE,
    )
)

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
    version = "2.1.0"
VERSION = str(os.getenv("OPENBB_VERSION", version))

# Select the terminal translation language
i18n_dict_location = MISCELLANEOUS_DIRECTORY / "i18n"
i18n.load_path.append(i18n_dict_location)
i18n.set("locale", USE_LANGUAGE)
i18n.set("filename_format", "{locale}.{format}")
