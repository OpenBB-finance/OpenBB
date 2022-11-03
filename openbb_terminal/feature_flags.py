# IMPORTATION STANDARD
import os
import os.path
from distutils.util import strtobool

# IMPORTATION THIRDPARTY
from dotenv import load_dotenv
import pkg_resources
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
from openbb_terminal import base_helpers

paths_helper.init_userdata()

# pylint: disable=no-member,c-extension-no-member

load_dotenv(USER_ENV_FILE)
load_dotenv(REPOSITORY_ENV_FILE, override=True)
load_dotenv(PACKAGE_ENV_FILE, override=True)

# Retry unknown commands with `load`
RETRY_WITH_LOAD = base_helpers.load_env_vars("OPENBB_RETRY_WITH_LOAD", strtobool, False)

# Use tabulate to print dataframes
USE_TABULATE_DF = base_helpers.load_env_vars("OPENBB_USE_TABULATE_DF", strtobool, True)

# Use clear console after each command
USE_CLEAR_AFTER_CMD = base_helpers.load_env_vars(
    "OPENBB_USE_CLEAR_AFTER_CMD", strtobool, False
)

# Use coloring features
USE_COLOR = base_helpers.load_env_vars("OPENBB_USE_COLOR", strtobool, True)

# Select console flair (choose from config_terminal.py list)
USE_FLAIR = str(os.getenv("OPENBB_USE_FLAIR", ":openbb"))

# Add date and time to command line
USE_DATETIME = base_helpers.load_env_vars("OPENBB_USE_DATETIME", strtobool, True)

# Enable interactive matplotlib mode
USE_ION = base_helpers.load_env_vars("OPENBB_USE_ION", strtobool, True)

# Enable watermark in the figures
USE_WATERMARK = base_helpers.load_env_vars("OPENBB_USE_WATERMARK", strtobool, True)

# Enable command and source in the figures
USE_CMD_LOCATION_FIGURE = base_helpers.load_env_vars(
    "OPENBB_USE_CMD_LOCATION_FIGURE", strtobool, True
)

# Enable Prompt Toolkit
USE_PROMPT_TOOLKIT = base_helpers.load_env_vars(
    "OPENBB_USE_PROMPT_TOOLKIT", strtobool, True
)

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = base_helpers.load_env_vars(
    "OPENBB_USE_PLOT_AUTOSCALING", strtobool, False
)

# Enable thoughts of the day
ENABLE_THOUGHTS_DAY = base_helpers.load_env_vars(
    "OPENBB_ENABLE_THOUGHTS_DAY", strtobool, False
)

# Quick exit for testing
ENABLE_QUICK_EXIT = base_helpers.load_env_vars(
    "OPENBB_ENABLE_QUICK_EXIT", strtobool, False
)

# Open report as HTML, otherwise notebook
OPEN_REPORT_AS_HTML = base_helpers.load_env_vars(
    "OPENBB_OPEN_REPORT_AS_HTML", strtobool, True
)

# Enable auto print_help when exiting menus
ENABLE_EXIT_AUTO_HELP = base_helpers.load_env_vars(
    "OPENBB_ENABLE_EXIT_AUTO_HELP", strtobool, True
)

# Remember contexts during session
REMEMBER_CONTEXTS = base_helpers.load_env_vars(
    "OPENBB_REMEMBER_CONTEXTS", strtobool, True
)

# Use the colorful rich terminal
ENABLE_RICH = base_helpers.load_env_vars("OPENBB_ENABLE_RICH", strtobool, True)

# Use the colorful rich terminal
ENABLE_RICH_PANEL = base_helpers.load_env_vars(
    "OPENBB_ENABLE_RICH_PANEL", strtobool, True
)

# Check API KEYS before running a command
ENABLE_CHECK_API = base_helpers.load_env_vars(
    "OPENBB_ENABLE_CHECK_API", strtobool, True
)

# Send logs to data lake
LOG_COLLECTION = base_helpers.load_env_vars("OPENBB_LOG_COLLECT", strtobool, True)

# Provide export folder path. If empty that means default.
EXPORT_FOLDER_PATH = str(os.getenv("OPENBB_EXPORT_FOLDER_PATH", ""))

# Toolbar hint
TOOLBAR_HINT = base_helpers.load_env_vars("OPENBB_TOOLBAR_HINT", strtobool, True)

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
    version = pkg_resources.get_distribution("OpenBBTerminal").version
except Exception:
    version = "1.9.0m"
VERSION = str(os.getenv("OPENBB_VERSION", version))

# Select the terminal translation language
i18n_dict_location = MISCELLANEOUS_DIRECTORY / "i18n"
i18n.load_path.append(i18n_dict_location)
i18n.set("locale", USE_LANGUAGE)
i18n.set("filename_format", "{locale}.{format}")
