# IMPORTATION STANDARD
import os
from typing import List
import shutil

from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    REPOSITORY_ENV_FILE,
    CUSTOM_IMPORTS_DIRECTORY,
    REPOSITORY_DIRECTORY,
    PORTFOLIO_DATA_DIRECTORY,
)


def create_paths(list_dirs: List):
    """
    Creates dirs for user data outside the
    terminal if they don't exist
    """
    for dirs in list_dirs:
        if not os.path.exists(dirs):
            os.mkdir(dirs)


def create_files(list_files: List):
    """
    Creates files outside the terminal if they don't exist
    """
    for filename in list_files:
        if not filename.is_file():
            with open(str(filename), "w"):
                pass


def copy_files(from_dir, to_dir):
    """
    Copy default/example files from the repo
    to the user data folder"""

    if from_dir.exists():
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)


dirs_list = [
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_DATA_DIRECTORY / "styles",
    CUSTOM_IMPORTS_DIRECTORY,
    CUSTOM_IMPORTS_DIRECTORY / "econometrics",
    PORTFOLIO_DATA_DIRECTORY,
    PORTFOLIO_DATA_DIRECTORY / "views",
]
dirs_files = [USER_ENV_FILE, REPOSITORY_ENV_FILE]
create_paths(dirs_list)
create_files(dirs_files)
copy_files(REPOSITORY_DIRECTORY / "custom_imports", CUSTOM_IMPORTS_DIRECTORY)
copy_files(REPOSITORY_DIRECTORY / "portfolio", PORTFOLIO_DATA_DIRECTORY)
copy_files(
    REPOSITORY_DIRECTORY
    / "openbb_terminal"
    / "portfolio"
    / "portfolio_analysis"
    / "portfolios",
    PORTFOLIO_DATA_DIRECTORY / "portfolios",
)
