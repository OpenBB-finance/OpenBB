# This is for helpers that do NOT import any OpenBB Modules
import logging
from typing import Literal

from dotenv import load_dotenv
from rich.console import Console

from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    SETTINGS_ENV_FILE,
)

console = Console()

menus = Literal["", "featflags", "settings"]


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = str(val).lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        output = True
    elif val in ("n", "no", "f", "false", "off", "0"):
        output = False
    else:
        raise ValueError(f"invalid truth value {val}")

    return output


def load_env_files():
    """
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


def remove_log_handlers():
    """Remove the log handlers - needs to be done before reloading modules."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
