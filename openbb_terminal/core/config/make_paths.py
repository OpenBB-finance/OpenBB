# IMPORTATION STANDARD
import os
from typing import List
from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    ENV_FILE_REPOSITORY,
    STYLES_FOLDER,
)


def create_paths(list_dirs: List):
    """
    Creates dirs/files for user data and .env files outside the
    terminal if they don't exist
    """
    for dirs in list_dirs:
        if not os.path.exists(dirs):
            os.mkdir(dirs)


dirs_list = [
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    ENV_FILE_REPOSITORY,
    STYLES_FOLDER,
]
create_paths(dirs_list)
