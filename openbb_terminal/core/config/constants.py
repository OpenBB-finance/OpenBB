# IMPORTATION STANDARD
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent
USER_HOME = Path(os.path.expanduser("~"))
ENV_FILE = REPO_DIR.joinpath(".env")
