# IMPORTATION STANDARD
from pathlib import Path
import os
import dotenv

REPO_DIR = Path(__file__).parent.parent.parent.parent
USER_HOME = Path(os.path.expanduser("~"))
ENV_FILE_DIR = Path(str(Path.home()) + "/.openbb_terminal")
if not os.path.exists(ENV_FILE_DIR):
    os.mkdir(ENV_FILE_DIR)

ENV_FILE_DEFAULT = ENV_FILE_DIR.joinpath(".env")
if not ENV_FILE_DEFAULT.is_file():
    with open(str(ENV_FILE_DEFAULT), "w"):
        pass
dotenv.load_dotenv(ENV_FILE_DEFAULT)
# check if there is a predefined user data folder
if os.getenv("USER_DATA_FOLDER"):
    USER_DATA_DIR = Path.home() / os.getenv("USER_DATA_FOLDER")  # type: ignore
else:
    dotenv.set_key(ENV_FILE_DEFAULT, "USER_DATA_FOLDER", "OpenBBUserData")
    USER_DATA_DIR = Path.home() / "OpenBBUserData"
if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)

ENV_FILE_REPO = REPO_DIR.joinpath(".env")
if not ENV_FILE_REPO.is_file():
    with open(str(ENV_FILE_REPO), "w"):
        pass

folders = ["settings", "settings/styles"]

folder_paths = {}

for folder in folders:
    full_folder = str(USER_DATA_DIR) + "/" + folder
    if not os.path.exists(full_folder):
        os.mkdir(full_folder)
    folder_paths[folder] = full_folder
