# IMPORTATION STANDARD
from pathlib import Path
import os
import dotenv

def get_user_data_directory():
    """"
    Gets user data path from .env file
    """
    dotenv.load_dotenv(USER_ENV_FILE)
    if os.getenv("OPENBB_USER_DATA_DIRECTORY"):
        user_data_directory = Path(os.getenv("OPENBB_USER_DATA_DIRECTORY"))
    else:
        user_data_directory = Path.home() / "OpenBBUserData"
    return user_data_directory

HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
USER_ENV_FILE = SETTINGS_DIRECTORY / ".env"

USER_DATA_DIRECTORY = get_user_data_directory()

USER_EXPORTS_DIRECTORY = USER_DATA_DIRECTORY / "exports"

CUSTOM_IMPORTS_DIRECTORY = USER_DATA_DIRECTORY / "custom_imports"
