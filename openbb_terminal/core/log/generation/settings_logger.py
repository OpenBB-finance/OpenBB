# IMPORTATION STANDARD
import json
import logging

# IMPORTATION INTERNAL
from openbb_terminal.core.log.generation.common import do_rollover
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import get_current_user

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
    log_startup()

    if with_rollover:
        do_rollover()


def get_system() -> dict:
    """Log system"""
    system_dict = get_current_system().to_dict()
    system_dict.pop("LOGGING_AWS_ACCESS_KEY_ID", None)
    system_dict.pop("LOGGING_AWS_SECRET_ACCESS_KEY", None)

    return system_dict


def get_credentials() -> dict:
    """Log credentials"""

    current_user = get_current_user()

    var_list = [v for v in dir(current_user.credentials) if v.startswith("API_")]

    current_keys = {}

    for cfg_var_name in var_list:
        cfg_var_value = getattr(current_user.credentials, cfg_var_name)

        if cfg_var_value != "REPLACE_ME":
            current_keys[cfg_var_name] = "defined"
        else:
            current_keys[cfg_var_name] = "not_defined"

    return current_keys


def log_preferences() -> None:
    """Log preferences"""
    logger.info(
        "PREFERENCES: %s ", json.dumps(get_current_user().preferences.to_dict())
    )


def log_startup() -> None:
    """Combined logging of all settings"""
    logger.info("STARTUP: %s ", json.dumps(get_startup()))


def get_startup():
    return {
        "PREFERENCES": get_current_user().preferences.to_dict(),
        "KEYS": get_credentials(),
        "SYSTEM": get_system(),
    }
