# IMPORTATION STANDARD
import platform
import json
import logging

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL
import openbb_terminal.feature_flags as obbff
from openbb_terminal.config_terminal import (
    MPL_STYLE,
    PMF_STYLE,
    RICH_STYLE,
)
from openbb_terminal.keys_model import get_keys
from openbb_terminal.core.log.generation.path_tracking_file_handler import (
    PathTrackingFileHandler,
)


logger = logging.getLogger(__name__)


def log_settings() -> None:
    """Log settings"""
    settings_dict = {}
    settings_dict["tab"] = "True" if obbff.USE_TABULATE_DF else "False"
    settings_dict["cls"] = "True" if obbff.USE_CLEAR_AFTER_CMD else "False"
    settings_dict["color"] = "True" if obbff.USE_COLOR else "False"
    settings_dict["promptkit"] = "True" if obbff.USE_PROMPT_TOOLKIT else "False"
    settings_dict["thoughts"] = "True" if obbff.ENABLE_THOUGHTS_DAY else "False"
    settings_dict["reporthtml"] = "True" if obbff.OPEN_REPORT_AS_HTML else "False"
    settings_dict["exithelp"] = "True" if obbff.ENABLE_EXIT_AUTO_HELP else "False"
    settings_dict["rcontext"] = "True" if obbff.REMEMBER_CONTEXTS else "False"
    settings_dict["rich"] = "True" if obbff.ENABLE_RICH else "False"
    settings_dict["richpanel"] = "True" if obbff.ENABLE_RICH_PANEL else "False"
    settings_dict["ion"] = "True" if obbff.USE_ION else "False"
    settings_dict["watermark"] = "True" if obbff.USE_WATERMARK else "False"
    settings_dict["autoscaling"] = "True" if obbff.USE_PLOT_AUTOSCALING else "False"
    settings_dict["dt"] = "True" if obbff.USE_DATETIME else "False"
    settings_dict["packaged"] = "True" if obbff.PACKAGED_APPLICATION else "False"
    settings_dict["python"] = str(platform.python_version())
    settings_dict["os"] = str(platform.system())
    settings_dict["theme"] = json.dumps(
        {
            "mpl_style": MPL_STYLE,
            "pmf_style": PMF_STYLE,
            "rich_style": RICH_STYLE,
        }
    )
    settings_dict["keys"] = get_keys().index.tolist()

    logger.info("SETTINGS: %s ", json.dumps(settings_dict))

    do_rollover()


def do_rollover():
    """RollOver the log file."""

    for handler in logging.getLogger().handlers:
        if isinstance(handler, PathTrackingFileHandler):
            handler.doRollover()
