import os
import json
from distutils.util import strtobool
from typing import Union, Optional

from dotenv import load_dotenv

gtff_defaults_path = os.path.join(os.path.dirname(__file__), "GTFF_DEFAULTS.json")
if os.path.exists(gtff_defaults_path):
    with open(gtff_defaults_path) as f:
        GTFF_DEFAULTS = json.load(f)
else:
    GTFF_DEFAULTS = dict()

env_files = [f for f in os.listdir() if f.endswith(".env")]
if env_files:
    load_dotenv(env_files[0])


def assign_feature_flag(
    feature_flag: str, fallback_value: str, return_bool: bool = False
) -> Optional[Union[str, bool]]:
    """Get the feature flag value in order of priority.

    - Env variables have the highest priority
    - The GTFF_DEFAULTS dictionary has the defaults for the bundled app
    - Fallback value is used if none of the above mentioned places have feature flag settings

    Parameters
    ----------
    feature_flag : str
        Feature flag as upper-case string
    fallback_value : str
        Fallback vabue
    return_bool : bool, optional
        If a boolean should be returned vs a string, by default False

    Returns
    -------
    Optional[Union[str, bool]]
        The feature flag value or None
    """
    if bool(os.getenv(feature_flag)):
        feature_flag_value = (
            strtobool(os.getenv(feature_flag))  # type: ignore
            if return_bool
            else os.getenv(feature_flag)
        )
    elif feature_flag in GTFF_DEFAULTS:
        feature_flag_value = (
            strtobool(GTFF_DEFAULTS[feature_flag])
            if return_bool
            else GTFF_DEFAULTS[feature_flag]
        )
    else:
        feature_flag_value = (
            strtobool(fallback_value) if return_bool else fallback_value
        )
    return feature_flag_value


# Use tabulate to print dataframes
USE_TABULATE_DF = assign_feature_flag("GTFF_USE_TABULATE_DF", "True", True)

# Use clear console after each command
USE_CLEAR_AFTER_CMD = assign_feature_flag("GTFF_USE_CLEAR_AFTER_CMD", "False", True)

# Use coloring features
USE_COLOR = assign_feature_flag("GTFF_USE_COLOR", "True", True)

# Select console flair (choose from config_terminal.py list)
USE_FLAIR = assign_feature_flag("GTFF_USE_FLAIR", ":stars")

# Add date and time to command line
USE_DATETIME = assign_feature_flag("GTFF_USE_DATETIME", "True", True)

# Enable interactive matplotlib mode
USE_ION = assign_feature_flag("GTFF_USE_ION", "True", True)

# Enable watermark in the figures
USE_WATERMARK = assign_feature_flag("GTFF_USE_WATERMARK", "True", True)

# Enable command and source in the figures
USE_CMD_LOCATION_FIGURE = assign_feature_flag(
    "GTFF_USE_CMD_LOCATION_FIGURE", "True", True
)

# Enable Prompt Toolkit
USE_PROMPT_TOOLKIT = assign_feature_flag("GTFF_USE_PROMPT_TOOLKIT", "True", True)

# Enable Prediction features
ENABLE_PREDICT = assign_feature_flag("GTFF_ENABLE_PREDICT", "True", True)

# Enable plot autoscaling
USE_PLOT_AUTOSCALING = assign_feature_flag("GTFF_USE_PLOT_AUTOSCALING", "False", True)

# Enable thoughts of the day
ENABLE_THOUGHTS_DAY = assign_feature_flag("GTFF_ENABLE_THOUGHTS_DAY", "False", True)

# Quick exit for testing
ENABLE_QUICK_EXIT = assign_feature_flag("GTFF_ENABLE_QUICK_EXIT", "False", True)

# Open report as HTML, otherwise notebook
OPEN_REPORT_AS_HTML = assign_feature_flag("GTFF_OPEN_REPORT_AS_HTML", "True", True)

# Enable auto print_help when exiting menus
ENABLE_EXIT_AUTO_HELP = assign_feature_flag("GTFF_ENABLE_EXIT_AUTO_HELP", "False", True)

# Remember contexts during session
REMEMBER_CONTEXTS = assign_feature_flag("GTFF_REMEMBER_CONTEXTS", "True", True)

# Use the colorful rich terminal
ENABLE_RICH = assign_feature_flag("GTFF_ENABLE_RICH", "True", True)

# Use the colorful rich terminal
ENABLE_RICH_PANEL = assign_feature_flag("GTFF_ENABLE_RICH_PANEL", "True", True)

# Check API KEYS before running a command
ENABLE_CHECK_API = assign_feature_flag("GTFF_ENABLE_CHECK_API", "True", True)

# Send logs to data lake
LOG_COLLECTION = bool(assign_feature_flag("GTFF_LOG_COLLECTION", "True", True))

# Provide export folder path. If empty that means default.
EXPORT_FOLDER_PATH = assign_feature_flag("GTFF_EXPORT_FOLDER_PATH", "")

# Set a flag if the application is running from a packaged bundle
PACKAGED_APPLICATION = assign_feature_flag("GTFF_PACKAGED_APPLICATION", "False", True)

LOGGING_COMMIT_HASH = str(assign_feature_flag("GTFF_LOGGING_COMMIT_HASH", "REPLACE_ME"))
