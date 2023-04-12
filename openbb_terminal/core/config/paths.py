# IMPORTATION STANDARD
from pathlib import Path

# Installation related paths
HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
PACKAGE_DIRECTORY = Path(__file__).parent.parent.parent
MISCELLANEOUS_DIRECTORY = PACKAGE_DIRECTORY / "miscellaneous"
REPOSITORY_ENV_FILE = REPOSITORY_DIRECTORY / ".env"
PACKAGE_ENV_FILE = PACKAGE_DIRECTORY / ".env"
PLOTS_CORE_DIRECTORY = PACKAGE_DIRECTORY / "core" / "plots"

SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
SETTINGS_ENV_FILE = SETTINGS_DIRECTORY / ".env"
HIST_FILE_PATH = SETTINGS_DIRECTORY / ".openbb_terminal.his"

# i18n_dict_location
I18N_DICT_LOCATION = MISCELLANEOUS_DIRECTORY / "i18n"

# styles
STYLES_DIRECTORY_REPO = MISCELLANEOUS_DIRECTORY / "styles"

# sources
DATA_SOURCES_DEFAULT_FILE = MISCELLANEOUS_DIRECTORY / "sources" / "openbb_default.json"

# session
SESSION_FILE_PATH = SETTINGS_DIRECTORY / "session.json"

# sdk trail map paths
MAP_PATH = PACKAGE_DIRECTORY / "core/sdk" / "trail_map.csv"
MAP_FORECASTING_PATH = PACKAGE_DIRECTORY / "core/sdk" / "trail_map_forecasting.csv"
MAP_OPTIMIZATION_PATH = PACKAGE_DIRECTORY / "core/sdk" / "trail_map_optimization.csv"
