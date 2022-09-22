# IMPORTATION STANDARD
import os
from typing import List
from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_EXPORTS_DIRECTORY,
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


dirs_list = [
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_DATA_DIRECTORY / "styles",
    USER_EXPORTS_DIRECTORY,
]
dirs_files = [USER_ENV_FILE, REPOSITORY_ENV_FILE]
create_paths(dirs_list)
create_files(dirs_files)
