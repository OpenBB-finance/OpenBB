# IMPORTATION STANDARD
import os
from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_DATA_DIRECTORY,
    USER_ENV_FILE,
    ENV_FILE_REPOSITORY,
    USER_DATA_FOLDERS,
)


def create_paths():
    """
    Creates dirs/files for user data and .env files outside the
    terminal if they don't exist
    """
    if not os.path.exists(SETTINGS_DIRECTORY):
        os.mkdir(SETTINGS_DIRECTORY)

    if not USER_ENV_FILE.is_file():
        with open(str(USER_ENV_FILE), "w"):
            pass

    if not ENV_FILE_REPOSITORY.is_file():
        with open(str(ENV_FILE_REPOSITORY), "w"):
            pass

    if not os.path.exists(USER_DATA_DIRECTORY):
        os.mkdir(USER_DATA_DIRECTORY)

    for folder in USER_DATA_FOLDERS:
        full_folder = USER_DATA_DIRECTORY / folder
        if not os.path.exists(full_folder):
            os.mkdir(full_folder)


create_paths()
