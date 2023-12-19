# IMPORTS STANDARD
import sys
from typing import Any, Dict, Optional

# IMPORTS THIRDPARTY
from dotenv import dotenv_values, set_key

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    SETTINGS_ENV_FILE,
)

DEFAULT_ORDER = [SETTINGS_ENV_FILE, PACKAGE_ENV_FILE, REPOSITORY_ENV_FILE]


def get_reading_order() -> list:
    """Get order of .env files. If we are on frozen app, we reverse the order to
    read the SETTINGS_ENV_FILE last.

    Returns
    -------
    list
        List of .env files.
    """
    local_order = DEFAULT_ORDER.copy()
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        local_order.reverse()
    return local_order


def read_env() -> Dict[str, Any]:
    __env_dict: Dict[str, Optional[str]] = {}

    for env_file in get_reading_order():
        if env_file.exists():
            __env_dict.update(**dotenv_values(env_file))

    __env_dict_filtered = {
        k[len("OPENBBB_") - 1 :]: v
        for k, v in __env_dict.items()
        if k.startswith("OPENBB_")
    }

    return __env_dict_filtered


def write_to_dotenv(name: str, value: str) -> None:
    """Write to .env file.

    Parameters
    ----------
    name : str
        Name of the variable.
    value : str
        Value of the variable.
    """
    set_key(str(SETTINGS_ENV_FILE), name, str(value))
