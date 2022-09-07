# IMPORTATION STANDARD
from pathlib import Path
from openbb_terminal.helper_funcs import get_user_dir


USER_HOME = Path.home()
REPO_DIR = Path(__file__).parent.parent.parent.parent
USER_DATA_DIR = USER_HOME / get_user_dir()
ENV_FILE_DIR = USER_HOME / ".openbb_terminal"

ENV_FILE_REPO = USER_HOME / ".env"
ENV_FILE_DEFAULT = ENV_FILE_DIR / ".env"
