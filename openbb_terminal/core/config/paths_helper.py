# IMPORTATION STANDARD
from typing import List

from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    REPOSITORY_ENV_FILE,
    CUSTOM_IMPORTS_DIRECTORY,
    USER_EXPORTS_DIRECTORY,
    PORTFOLIO_DATA_DIRECTORY,
    PRESETS_DIRECTORY,
    ROUTINES_DIRECTORY,
)


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
    CUSTOM_IMPORTS_DIRECTORY,
    CUSTOM_IMPORTS_DIRECTORY / "econometrics",
    CUSTOM_IMPORTS_DIRECTORY / "stocks",
    CUSTOM_IMPORTS_DIRECTORY / "dashboards",
    USER_EXPORTS_DIRECTORY,
    USER_EXPORTS_DIRECTORY / "reports",
    PORTFOLIO_DATA_DIRECTORY,
    PORTFOLIO_DATA_DIRECTORY / "views",
    PORTFOLIO_DATA_DIRECTORY / "holdings",
    PORTFOLIO_DATA_DIRECTORY / "allocation",
    PORTFOLIO_DATA_DIRECTORY / "optimization",
    PRESETS_DIRECTORY,
    PRESETS_DIRECTORY / "stocks" / "options",
    PRESETS_DIRECTORY / "stocks" / "screener",
    PRESETS_DIRECTORY / "stocks" / "insider",
    PRESETS_DIRECTORY / "etf" / "screener",
    ROUTINES_DIRECTORY,
]
dirs_files = [USER_ENV_FILE, REPOSITORY_ENV_FILE]
create_paths(dirs_list)
create_files(dirs_files)
