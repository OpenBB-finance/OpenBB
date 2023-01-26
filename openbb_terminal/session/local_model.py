import os
from pathlib import Path
import json
from typing import Optional
from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
    USER_ROUTINES_DIRECTORY,
)
from openbb_terminal.rich_config import console

from openbb_terminal import feature_flags as obbff
from openbb_terminal import config_terminal as cfg
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal.base_helpers import strtobool

SESSION_FILE_PATH = SETTINGS_DIRECTORY / "session.json"


def save_session(data: dict, file_path: Path = SESSION_FILE_PATH):
    """Save the login info to a file.

    Parameters
    ----------
    data : dict
        The data to write.
    file_path : Path
        The file path.
    """
    try:
        with open(file_path, "w") as file:
            file.write(json.dumps(data))
    except Exception:
        console.print("Failed to save session info.", style="red")


def get_session(file_path: Path = SESSION_FILE_PATH) -> dict:
    """Get the session info from the file.

    Parameters
    ----------
    file_path : Path
        The file path.

    Returns
    -------
    dict
        The session info.
    """
    try:
        if os.path.isfile(file_path):
            with open(file_path) as file:
                return json.load(file)
    except Exception:
        console.print("[red]\nFailed to get login info.[/red]")
    return {}


def remove_session_file(file_path: Path = SESSION_FILE_PATH) -> bool:
    """Remove the session file.

    Parameters
    ----------
    file_path : Path
        The file path.

    Returns
    -------
    bool
        The status of the removal.
    """

    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        return True
    except Exception:
        console.print("[red]\nFailed to remove login file.[/red]")
        return False


def apply_configs(configs: dict):
    """Apply configurations.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    console.print(configs, style="red")

    if configs:
        settings = configs.get("features_settings", {})

        # TODO: Find a cleaner way to check if user has sync enabled.
        obbff.SYNC_ENABLED = is_sync_enabled(settings)

        if obbff.SYNC_ENABLED:
            if settings:
                for k, v in settings.items():
                    if hasattr(obbff, k):
                        cast_set_attr(obbff, k, v)
                    elif hasattr(cfg, k):
                        cast_set_attr(cfg, k, v)
                    elif hasattr(cfg_plot, k):
                        cast_set_attr(cfg_plot, k, v)

            keys = configs.get("features_keys", {})
            if keys:
                for k, v in keys.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)


def is_sync_enabled(settings: dict) -> bool:
    """Check if sync is enabled.

    Parameters
    ----------
    settings : dict
        The settings.

    Returns
    -------
    bool
        The status of sync.
    """
    if settings:
        if settings.get("SYNC_ENABLED", "").lower() == "false":
            return False
    return True


def cast_set_attr(obj, name, value):
    """Set attribute in object.

    Parameters
    ----------
    obj : object
        The object.
    name : str
        The attribute name.
    value : str
        The attribute value.
    """
    if value.lower() in ["true", "false"]:
        setattr(obj, name, strtobool(value))
    elif isinstance(getattr(obj, name), int):
        setattr(obj, name, int(value))
    else:
        setattr(obj, name, value)


def get_routine(name: str) -> Optional[str]:
    """Get the routine.

    Returns
    -------
    str
        The routine.
    """
    try:
        with open(USER_ROUTINES_DIRECTORY / name) as f:
            routine = "".join(f.readlines())
        return routine
    except Exception:
        console.print("[red]\nFailed to find routine.[/red]")
        return None
