# IMPORTATION STANDARD
from pathlib import Path


# def get_user_data_directory():
#     """Gets user data path from .env file or returns default path"""
#     if os.getenv("OPENBB_USER_DATA_DIRECTORY"):
#         user_data_directory = Path(os.getenv("OPENBB_USER_DATA_DIRECTORY"))
#     else:
#         user_data_directory = Path.home() / "OpenBBUserData"
#     return user_data_directory


# Installation related paths
HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
PACKAGE_DIRECTORY = Path(__file__).parent.parent.parent
MISCELLANEOUS_DIRECTORY = PACKAGE_DIRECTORY / "miscellaneous"
USER_DATA_SOURCES_DEFAULT_FILE = MISCELLANEOUS_DIRECTORY / "data_sources_default.json"
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
PACKAGE_ENV_FILE = PACKAGE_DIRECTORY / ".env"
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
SETTINGS_ENV_FILE = SETTINGS_DIRECTORY / ".env"
HIST_FILE_PATH = SETTINGS_DIRECTORY / ".openbb_terminal.his"
