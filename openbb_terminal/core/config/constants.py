# IMPORTATION STANDARD
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent
USER_DATA_DIR = Path(str(Path.home()) + "/OpenBBUserData")
if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)