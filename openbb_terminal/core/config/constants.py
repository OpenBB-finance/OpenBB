# IMPORTATION STANDARD
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent

USER_DATA_DIR = Path(str(Path.home()) + "/OpenBBUserData")
if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)

USER_HOME = Path(os.path.expanduser("~"))
ENV_FILE_DIR = Path(str(Path.home()) + "/.openbb_terminal")
ENV_FILE = ENV_FILE_DIR.joinpath(".env")
if not ENV_FILE.is_file():
    open(str(ENV_FILE),"w")

folders = [
    "custom_imports",
    "custom_imports/stocks",
    "custom_imports/stocks/options",
    "exports",
    "routines",
    "logs",
    "stored",
    "settings",
    "settings/styles",
    "portfolio",
    "portfolio/holdings/",
    "portfolio/optimization",
    "portfolio/allocation",
    "presets",
    "presets/stocks",
    "presets/stocks/options",
    "presets/etf",
    "presets/etf/screen",
    "presets/insider",
]
folder_paths = {}

for folder in folders:
    full_folder = str(USER_DATA_DIR) + "/" + folder
    if not os.path.exists(full_folder):
        os.mkdir(full_folder)
    folder_paths[folder] = full_folder


CUSTOM_IMPORTS = Path(str(USER_DATA_DIR) + "/custom_imports")
