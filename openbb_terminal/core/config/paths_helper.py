# IMPORTATION STANDARD
from typing import List

from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_CUSTOM_IMPORTS_DIRECTORY,
    USER_EXPORTS_DIRECTORY,
    USER_PORTFOLIO_DATA_DIRECTORY,
    PRESETS_DIRECTORY,
    ROUTINES_DIRECTORY,
    DATA_SOURCES_DEFAULT_FILE,
)

# pylint: disable=W0603


def create_paths(list_dirs: List):
    """
    Creates dirs for user data outside the
    terminal if they don't exist
    """
    for dirs in list_dirs:
        if not dirs.exists():
            dirs.mkdir(
                parents=True,
            )


def create_files(list_files: List):
    """
    Creates files outside the terminal if they don't exist
    """
    for filename in list_files:
        if not filename.is_file():
            with open(str(filename), "w"):
                pass


dirs_list = [
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_DATA_DIRECTORY / "styles",
    USER_CUSTOM_IMPORTS_DIRECTORY,
    USER_CUSTOM_IMPORTS_DIRECTORY / "econometrics",
    USER_CUSTOM_IMPORTS_DIRECTORY / "stocks",
    USER_CUSTOM_IMPORTS_DIRECTORY / "dashboards",
    USER_EXPORTS_DIRECTORY,
    USER_EXPORTS_DIRECTORY / "reports",
    USER_PORTFOLIO_DATA_DIRECTORY,
    USER_PORTFOLIO_DATA_DIRECTORY / "views",
    USER_PORTFOLIO_DATA_DIRECTORY / "holdings",
    USER_PORTFOLIO_DATA_DIRECTORY / "allocation",
    USER_PORTFOLIO_DATA_DIRECTORY / "optimization",
    PRESETS_DIRECTORY,
    PRESETS_DIRECTORY / "stocks" / "options",
    PRESETS_DIRECTORY / "stocks" / "screener",
    PRESETS_DIRECTORY / "stocks" / "insider",
    PRESETS_DIRECTORY / "etf" / "screener",
    ROUTINES_DIRECTORY,
]
dirs_files = [USER_ENV_FILE, REPOSITORY_ENV_FILE, DATA_SOURCES_DEFAULT_FILE]
initialized = False


def init_userdata():
    """
    Initializes the user data folder
    """
    global initialized
    if not initialized:
        create_paths(dirs_list)
        create_files(dirs_files)
        initialized = True
