# IMPORTATION STANDARD
from pathlib import Path
import os
from dotenv import load_dotenv


def load_dotenv_with_priority():
    """Loads the dotenv files in the following order:
    1. Repository .env file
    2. Package .env file
    3. User .env file

    This allows the user to override the package settings with their own
    settings, and the package to override the repository settings.
    """
    load_dotenv(REPOSITORY_ENV_FILE, override=True)
    load_dotenv(PACKAGE_ENV_FILE, override=True)
    load_dotenv(USER_ENV_FILE, override=True)


def get_user_data_directory():
    """Gets user data path from .env file or returns default path"""
    load_dotenv_with_priority()
    if os.getenv("OPENBB_USER_DATA_DIRECTORY"):
        user_data_directory = Path(os.getenv("OPENBB_USER_DATA_DIRECTORY"))
    else:
        user_data_directory = Path.home() / "OpenBBUserData"
    return user_data_directory


HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
PACKAGE_DIRECTORY = Path(__file__).parent.parent.parent
MISCELLANEOUS_DIRECTORY = PACKAGE_DIRECTORY / "miscellaneous"
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
PACKAGE_ENV_FILE = PACKAGE_DIRECTORY / ".env"

SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
USER_ENV_FILE = SETTINGS_DIRECTORY / ".env"
USER_DATA_DIRECTORY = get_user_data_directory()
USER_EXPORTS_DIRECTORY = USER_DATA_DIRECTORY / "exports"
USER_CUSTOM_IMPORTS_DIRECTORY = USER_DATA_DIRECTORY / "custom_imports"
USER_PORTFOLIO_DATA_DIRECTORY = USER_DATA_DIRECTORY / "portfolio"
USER_ROUTINES_DIRECTORY = USER_DATA_DIRECTORY / "routines"
USER_DATA_SOURCES_DEFAULT_FILE = USER_DATA_DIRECTORY / "data_sources_default.json"
USER_PRESETS_DIRECTORY = USER_DATA_DIRECTORY / "presets"
USER_REPORTS_DIRECTORY = USER_DATA_DIRECTORY / "reports"
USER_CUSTOM_REPORTS_DIRECTORY = USER_DATA_DIRECTORY / "reports" / "custom reports"
USER_FORECAST_MODELS_DIRECTORY = USER_DATA_DIRECTORY / "exports" / "forecast_models"
