import json
import os
from pathlib import Path
from typing import Optional, Union

from openbb_terminal.core.config.paths import (
    HIST_FILE_PATH,
    SETTINGS_DIRECTORY,
)
from openbb_terminal.core.session.current_user import (
    get_current_user,
    get_local_user,
    set_credential,
)
from openbb_terminal.rich_config import console

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
    if configs and get_local_user().preferences.SYNC_ENABLED:
        credentials = configs.get("features_keys", {}) or {}
        for k, v in credentials.items():
            set_credential(k, v)

    # TODO: apply other configs here


def get_routine(file_name: str, folder: Optional[Path] = None) -> Optional[str]:
    """Get the routine.

    Returns
    -------
    file_name : str
        The routine.
    folder : Optional[Path]
        The routines folder.
    """

    current_user = get_current_user()
    if folder is None:
        folder = current_user.preferences.USER_ROUTINES_DIRECTORY

    try:
        user_folder = folder / current_user.profile.get_uuid()
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
    folder: Optional[Path] = None,
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

    current_user = get_current_user()
    if folder is None:
        folder = current_user.preferences.USER_ROUTINES_DIRECTORY

    try:
        uuid = current_user.profile.get_uuid()
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
