# IMPORTATION STANDARD
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent.parent
ENV_FILE = REPO_DIR.joinpath(".env")
DEFAULT_FILE = REPO_DIR.joinpath("OPENBB_DEFAULTS.json")
