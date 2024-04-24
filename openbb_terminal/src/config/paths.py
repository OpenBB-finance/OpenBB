"""Paths for the package."""

from pathlib import Path

# Installation related paths
HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
SRC_DIRECTORY = Path(__file__).parent.parent
ASSETS_DIRECTORY = SRC_DIRECTORY / "assets"

SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
HIST_FILE_PATH = SETTINGS_DIRECTORY / ".openbb_terminal.his"

# i18n_dict_location
I18N_DICT_LOCATION = ASSETS_DIRECTORY / "i18n"

# styles
STYLES_DIRECTORY_REPO = ASSETS_DIRECTORY / "styles"

# env
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
PROJECT_ENV_FILE = REPOSITORY_DIRECTORY / "openbb_terminal" / ".env"
SETTINGS_ENV_FILE = SETTINGS_DIRECTORY / ".env"
