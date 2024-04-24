"""Environment handler module."""

# IMPORTS STANDARD
import sys
from typing import Any, Dict, Optional

# IMPORTS THIRDPARTY
from dotenv import dotenv_values, load_dotenv, set_key

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    SETTINGS_ENV_FILE,
)

DEFAULT_ORDER = [SETTINGS_ENV_FILE, PACKAGE_ENV_FILE, REPOSITORY_ENV_FILE]


def load_env_files():
    """Load .env files.

    Loads the dotenv files in the following order:
    1. Repository .env file
    2. Package .env file
    3. User .env file

    This allows the user to override the package settings with their own
    settings, and the package to override the repository settings.

    openbb_terminal modules are reloaded to refresh config files with new env,
    otherwise they will use cache with old variables.
    """
    load_dotenv(REPOSITORY_ENV_FILE, override=True)
    load_dotenv(PACKAGE_ENV_FILE, override=True)
    load_dotenv(SETTINGS_ENV_FILE, override=True)


def get_reading_order() -> list:
    """Get order of .env files.

    If we are on frozen app, we reverse the order to read the SETTINGS_ENV_FILE last.

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
    """Read .env files."""
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
