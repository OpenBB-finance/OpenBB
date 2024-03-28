from pathlib import Path
from typing import List

from openbb_terminal.core.config.paths import (
    REPOSITORY_ENV_FILE,
    SETTINGS_DIRECTORY,
    SETTINGS_ENV_FILE,
)
from openbb_terminal.core.session.current_user import get_platform_user


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


current_user = get_platform_user()
user_data_directory = Path(current_user.preferences.data_directory)
user_export_directory = Path(current_user.preferences.export_directory)

dirs_list = [
    SETTINGS_DIRECTORY,
    user_data_directory,
    user_data_directory / "styles",
    user_export_directory,
    user_export_directory / "routines",
]
dirs_files = [
    SETTINGS_ENV_FILE,
    REPOSITORY_ENV_FILE,
]
initialized = False


def init_userdata():
    """
    Initializes the user data folder
    """
    global initialized  # pylint: disable=global-statement
    if not initialized:
        create_paths(dirs_list)
        create_files(dirs_files)
        initialized = True
