# IMPORTATION STANDARD
import json
import logging
import platform
from types import FunctionType, ModuleType

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
import openbb_terminal.feature_flags as obbff
from openbb_terminal import config_terminal as cfg
from openbb_terminal.core.log.generation.common import do_rollover
from openbb_terminal.terminal_helper import is_installer

SENSITIVE_WORDS = [
    "API",
    "DG_",
    "KEY",
    "PASSWORD",
    "SECRET",
    "TOKEN",
    "USER",
    "USERNAME",
    "ACCOUNT",
]

logger = logging.getLogger(__name__)


def log_all_settings(with_rollover: bool = True) -> None:
    """Log all settings"""
    log_settings()
    log_config_terminal()
    log_feature_flags()
    log_keys()

    if with_rollover:
        do_rollover()


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
    settings_dict["packaged"] = "True" if is_installer() else "False"
    settings_dict["python"] = str(platform.python_version())
    settings_dict["os"] = str(platform.system())

    logger.info("SETTINGS: %s ", json.dumps(settings_dict))


def log_config_terminal() -> None:
    """Log config_terminal"""

    config_terminal_dict = {}

    for item in dir(cfg):
        prop = getattr(cfg, item)
        if (
            not item.startswith("__")
            and not isinstance(prop, FunctionType)
            and not isinstance(prop, ModuleType)
            and not any(substring in item for substring in SENSITIVE_WORDS)
        ):
            config_terminal_dict[item] = str(prop)

    logger.info("CONFIG_TERMINAL: %s ", json.dumps(config_terminal_dict))


def log_feature_flags() -> None:
    """Log feature flags"""

    feature_flags_dict = {}

    for item in dir(obbff):
        prop = getattr(obbff, item)
        if (
            not item.startswith("__")
            and not isinstance(prop, FunctionType)
            and not isinstance(prop, ModuleType)
        ):
            feature_flags_dict[item] = str(prop)

    logger.info("FEATURE_FLAGS: %s ", json.dumps(feature_flags_dict))


def log_keys() -> None:
    """Log keys"""

    var_list = [v for v in dir(cfg) if v.startswith("API_")]

    current_keys = {}

    for cfg_var_name in var_list:
        cfg_var_value = getattr(cfg, cfg_var_name)

        if cfg_var_value != "REPLACE_ME":
            current_keys[cfg_var_name] = "defined"
        else:
            current_keys[cfg_var_name] = "not_defined"

    logger.info("KEYS: %s ", json.dumps(current_keys))
