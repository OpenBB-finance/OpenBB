import os
import shutil
from pathlib import Path

from openbb_terminal.core.session.current_user import (
    get_env_dict,
    set_preference,
)
from openbb_terminal.rich_config import console


def remove(path: Path) -> bool:
    """Remove path.

    Parameters
    ----------
    path : Path
        The file path.

    Returns
    -------
    bool
        The status of the removal.
    """

    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception:
        console.print(
            f"\n[bold red]Failed to remove {path}"
            "\nPlease delete this manually![/bold red]"
        )
        return False


def update_flair(username: str):
    """Update the flair.

    Parameters
    ----------
    username : str
        The username.
    """
    if "FLAIR" not in get_env_dict():
        MAX_FLAIR_LEN = 20
        flair = "[" + username[:MAX_FLAIR_LEN] + "]" + " 🦋"
        set_preference("FLAIR", flair)
