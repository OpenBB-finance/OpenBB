# IMPORTATION STANDARD
from pathlib import Path
from .get_paths import get_folder_paths


HOME_DIRECTORY = Path.home()
REPO_DIRECTORY = Path(__file__).parent.parent.parent.parent
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
ENV_FILE_REPOSITORY = HOME_DIRECTORY / ".env"
USER_ENV_FILE = SETTINGS_DIRECTORY / ".env"

USER_DATA_DIRECTORY = HOME_DIRECTORY / "OpenBBUserData"

FOLDERS = [
    "styles",
    "custom_imports/custom_menu",
    "custom_imports/stocks",
    "custom_imports/pred",
    "custom_imports/qa",
    "custom_imports/econometrics",
]
FOLDER_PATHS = get_folder_paths()
