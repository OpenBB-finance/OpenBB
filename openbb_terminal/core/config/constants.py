# IMPORTATION STANDARD
from pathlib import Path
import os

REPO_DIR = Path(__file__).parent.parent.parent.parent
USER_DATA_DIR = Path.home() / "OpenBBUserData"
USER_HOME = Path(os.path.expanduser("~"))
if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)
ENV_FILE = REPO_DIR.joinpath(".env")
