import json
import os
from pathlib import Path
from typing import Optional, Union

from openbb_terminal import (
    config_plot as cfg_plot,
    config_terminal as cfg,
    feature_flags as obbff,
)
from openbb_terminal.base_helpers import strtobool
from openbb_terminal.core.config import paths
from openbb_terminal.core.config.paths import (
    HIST_FILE_PATH,
    SETTINGS_DIRECTORY,
    USER_ROUTINES_DIRECTORY,
)
from openbb_terminal.rich_config import console
from openbb_terminal.session.user import User

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
        console.print("[red]Failed to save session info.[/red]")


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
        console.print("\n[red]Failed to get login info.[/red]")
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
        console.print("\n[red]Failed to remove login file.[/red]")
        return False


def remove_cli_history_file(file_path: Path = HIST_FILE_PATH) -> bool:
    """Remove the cli history file.

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
        console.print("\n[red]Failed to remove terminal history file.[/red]")
        return False


def apply_configs(configs: dict):
    """Apply configurations.

    Parameters
    ----------
    configs : dict
        The configurations.
    """

    # TODO: Here I'm assuming that obbff, cfg, cfg_plot and paths don't have variables
    # with the same name. If they do, then this assignment will hit the first variable
    # that matches the name.

    if configs:
        settings = configs.get("features_settings", {})
        sync = update_sync_flag(settings)
        if sync:
            if settings:
                for k, v in settings.items():
                    if hasattr(obbff, k):
                        cast_set_attr(obbff, k, v)
                    elif hasattr(cfg, k):
                        cast_set_attr(cfg, k, v)
                    elif hasattr(cfg_plot, k):
                        cast_set_attr(cfg_plot, k, v)
                    elif hasattr(paths, k):
                        cast_set_attr(paths, k, v)

            keys = configs.get("features_keys", {})
            if keys:
                for k, v in keys.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)


def update_sync_flag(settings: dict) -> bool:
    """Update the sync flag.

    Parameters
    ----------
    settings : dict
        The settings.

    Returns
    -------
    bool
        The sync flag.
    """
    if settings and settings.get("SYNC_ENABLED", "").lower() == "false":
        obbff.SYNC_ENABLED = False
        return False
    obbff.SYNC_ENABLED = True
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

    if str(value).lower() in ["true", "false"]:
        setattr(obj, name, strtobool(value))
    elif isinstance(getattr(obj, name), int):
        setattr(obj, name, int(value))
    elif isinstance(getattr(obj, name), float):
        setattr(obj, name, float(value))
    elif isinstance(getattr(obj, name), Path):
        setattr(obj, name, Path(value))
    else:
        setattr(obj, name, value)


def get_routine(
    file_name: str, folder: Path = USER_ROUTINES_DIRECTORY
) -> Optional[str]:
    """Get the routine.

    Returns
    -------
    file_name : str
        The routine.
    folder : Path
        The routines folder.
    """
    try:
        user_folder = USER_ROUTINES_DIRECTORY / User.get_uuid()
        file_path = (
            user_folder / file_name
            if os.path.exists(user_folder / file_name)
            else folder / file_name
        )

        with open(file_path) as f:
            routine = "".join(f.readlines())
        return routine
    except Exception:
        console.print("[red]Failed to find routine.[/red]")
        return None


def save_routine(
    file_name: str,
    routine: str,
    folder: Path = USER_ROUTINES_DIRECTORY,
    force: bool = False,
) -> Union[Optional[Path], str]:
    """Save the routine.

    Parameters
    ----------
    file_name : str
        The routine.
    routine : str
        The routine.
    folder : Path
        The routines folder.
    force : bool
        Force the save.

    Returns
    -------
    Optional[Path, str]
        The path to the routine or None.
    """
    try:
        uuid = User.get_uuid()
        user_folder = folder / uuid
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        file_path = user_folder / file_name
        if os.path.exists(file_path) and not force:
            return "File already exists"
        with open(file_path, "w") as f:
            f.write(routine)
        return user_folder / file_name
    except Exception:
        console.print("[red]\nFailed to save routine.[/red]")
        return None
