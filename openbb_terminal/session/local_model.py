import importlib
import os
from pathlib import Path
import json
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.rich_config import console

from openbb_terminal import feature_flags as obbff
from openbb_terminal import config_terminal as cfg
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
        keys = configs.get("features_keys", {})
        if keys:
            for k, v in keys.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)

        # Since settings come from different files we use the format {var_name: "path:value"}
        settings = configs.get("features_settings", {})
        if settings:
            for var_name, v in settings.items():
                if v.find(":") > 0:
                    path, value = v.split(":")

                    module = importlib.import_module(path)
                    if hasattr(module, var_name):
                        if value.lower() in ["true", "false"]:
                            setattr(module, var_name, strtobool(value))
                        elif isinstance(getattr(module, var_name), int):
                            setattr(module, var_name, int(value))
                        else:
                            setattr(module, var_name, value)
