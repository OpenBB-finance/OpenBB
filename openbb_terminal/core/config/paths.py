# IMPORTATION STANDARD
from pathlib import Path
from . import user_dir


HOME_DIRECTORY = Path.home()
REPO_DIRECTORY = Path(__file__).parent.parent.parent.parent
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
ENV_FILE_REPOSITORY = HOME_DIRECTORY / ".env"
USER_ENV_FILE = SETTINGS_DIRECTORY / ".env"

USER_DATA_DIRECTORY = HOME_DIRECTORY / user_dir.get_user_dir()  # type: ignore
