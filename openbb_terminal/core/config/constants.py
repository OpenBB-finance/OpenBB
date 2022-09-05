# IMPORTATION STANDARD
import os
import shutil
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent

USER_DATA_DIR = Path(str(Path.home()) + "/OpenBBUserData")
if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)

USER_HOME = Path(os.path.expanduser("~"))
ENV_FILE_DIR = Path(str(Path.home()) + "/.openbb_terminal")
if not os.path.exists(ENV_FILE_DIR):
    os.mkdir(ENV_FILE_DIR)

ENV_FILE_DEFAULT = ENV_FILE_DIR.joinpath(".env")
if not ENV_FILE_DEFAULT.is_file():
    with open(str(ENV_FILE_DEFAULT), "w"):
        pass

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
    "portfolio/holdings",
    "portfolio/optimization",
    "portfolio/allocation",
    "portfolio/portfolios",
    "presets",
    "presets/stocks",
    "presets/stocks/options",
    "presets/stocks/insider",
    "presets/stocks/screener",
    "presets/etf",
    "presets/etf/screener",
]
folder_paths = {}

for folder in folders:
    full_folder = str(USER_DATA_DIR) + "/" + folder
    if not os.path.exists(full_folder):
        os.mkdir(full_folder)
    folder_paths[folder] = full_folder


CUSTOM_IMPORTS = Path(folder_paths["custom_imports"])

# Copy folder contents from files to new path
# Do path in terminal first and desired path second
internal_paths = [
    ["routines", "routines"],
    ["portfolio/allocation", "portfolio/allocation"],
    ["portfolio/holdings", "portfolio/holdings"],
    ["portfolio/optimization", "portfolio/optimization"],
    ["openbb_terminal/stocks/options/presets", "presets/stocks/options"],
    ["openbb_terminal/stocks/insider/presets", "presets/stocks/insider"],
    ["openbb_terminal/etf/screener/presets", "presets/etf/screener"],
    ["openbb_terminal/stocks/screener/presets", "presets/stocks/screener"],
]
for int_path_dif in internal_paths:
    internal_routines = REPO_DIR / os.path.join(*int_path_dif[0].split("/"))
    for file in os.listdir(internal_routines):
        new_path = os.path.join(folder_paths[int_path_dif[1]], file)
        if not Path(new_path).is_file():
            old_path = os.path.join(internal_routines, file)
            shutil.copyfile(old_path, new_path)
