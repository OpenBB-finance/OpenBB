# IMPORTATION STANDARD
from pathlib import Path
import dotenv


HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
USER_ENV_FILE = SETTINGS_DIRECTORY / ".env"

if dotenv.get_key(USER_ENV_FILE, "OPENBB_USER_DATA_FOLDER_PATH"):
    USER_DATA_DIRECTORY = Path(
        dotenv.get_key(USER_ENV_FILE, "OPENBB_USER_DATA_FOLDER_PATH")
    )
else:
    USER_DATA_DIRECTORY = Path.home() / "OpenBBUserData"

USER_EXPORTS_DIRECTORY = USER_DATA_DIRECTORY / "exports"

CUSTOM_IMPORTS_DIRECTORY = USER_DATA_DIRECTORY / "custom_imports"
