# IMPORTATION STANDARD
from pathlib import Path
from typing import List

from openbb_terminal.core.config.paths import (
    REPOSITORY_ENV_FILE,
    SETTINGS_DIRECTORY,
    SETTINGS_ENV_FILE,
)
from openbb_terminal.core.session.current_user import get_current_user

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


current_user = get_current_user()

dirs_list = [
    SETTINGS_DIRECTORY,
    current_user.preferences.USER_DATA_DIRECTORY,
    current_user.preferences.USER_DATA_DIRECTORY / "styles",
    current_user.preferences.USER_DATA_DIRECTORY / "reports",
    current_user.preferences.USER_DATA_DIRECTORY / "reports" / "custom reports",
    current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY,
    current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY / "econometrics",
    current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY / "stocks",
    current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY / "dashboards",
    current_user.preferences.USER_EXPORTS_DIRECTORY,
    current_user.preferences.USER_PORTFOLIO_DATA_DIRECTORY,
    current_user.preferences.USER_PORTFOLIO_DATA_DIRECTORY / "views",
    current_user.preferences.USER_PORTFOLIO_DATA_DIRECTORY / "holdings",
    current_user.preferences.USER_PORTFOLIO_DATA_DIRECTORY / "allocation",
    current_user.preferences.USER_PORTFOLIO_DATA_DIRECTORY / "optimization",
    current_user.preferences.USER_PRESETS_DIRECTORY,
    current_user.preferences.USER_PRESETS_DIRECTORY / "stocks" / "options",
    current_user.preferences.USER_PRESETS_DIRECTORY / "stocks" / "screener",
    current_user.preferences.USER_PRESETS_DIRECTORY / "stocks" / "insider",
    current_user.preferences.USER_PRESETS_DIRECTORY / "etf" / "screener",
    current_user.preferences.USER_ROUTINES_DIRECTORY,
    current_user.preferences.USER_DATA_DIRECTORY / "sources",
]
dirs_files = [
    SETTINGS_ENV_FILE,
    REPOSITORY_ENV_FILE,
    Path(current_user.preferences.USER_DATA_SOURCES_FILE),
]
initialized = False


def init_userdata():
    """
    Initializes the user data folder
    """
    global initialized  # noqa
    if not initialized:
        create_paths(dirs_list)
        create_files(dirs_files)
        initialized = True
