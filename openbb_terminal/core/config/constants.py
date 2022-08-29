# IMPORTATION STANDARD
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent

FILE_DIR = Path(str(Path.home()) + "/OpenBB")
if not os.path.exists(FILE_DIR):
    os.mkdir(FILE_DIR)

USER_HOME = Path(os.path.expanduser("~"))
ENV_FILE = FILE_DIR.joinpath(".env")

if not ENV_FILE.is_file():
    Path(str(FILE_DIR) + ".env")

folders = [
    "custom_imports",
    "custom_imports/stocks",
    "custom_imports/stocks/options",
    "exports",
    "routines",
    "stored",
    "styles",
    "portfolio",
    "portfolio/holdings/",
    "portfolio/optimization",
    "portfolio/allocation",
    "stocks",
    "stocks/presets",
    "options",
    "options/presets",
    "insider",
    "insider/presets",
    "etf",
    "etf/screen",
]
folder_paths = {}

for folder in folders:
    full_folder = str(FILE_DIR) + "/" + folder
    if not os.path.exists(full_folder):
        os.mkdir(full_folder)
    folder_paths[folder] = full_folder


CUSTOM_IMPORTS = Path(str(FILE_DIR) + "/custom_imports")
