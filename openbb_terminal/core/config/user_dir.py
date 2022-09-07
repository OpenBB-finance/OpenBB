import os
import dotenv
from . import paths


def get_user_dir() -> str:
    """
    Gets name of user data directory from .env file.
    If none found, sets it to "OpenBBUserData"
    """

    if paths.USER_ENV_FILE.is_file():
        dotenv.load_dotenv(paths.USER_ENV_FILE)
        # check if there is a predefined user data folder
        if os.getenv("USER_DATA_FOLDER"):
            return os.getenv("USER_DATA_FOLDER")
        else:
            dotenv.set_key(paths.USER_ENV_FILE, "USER_DATA_FOLDER", "OpenBBUserData")
            return "OpenBBUserData"
    else:
        return "OpenBBUserData"
