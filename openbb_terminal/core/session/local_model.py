import json
import os
import shutil
from pathlib import Path
from typing import List, Optional

from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    SESSION_FILE_PATH,
)
from openbb_terminal.core.models.sources_model import get_allowed_sources
from openbb_terminal.core.session.current_user import (
    get_env_dict,
    set_credential,
    set_preference,
    set_sources,
)
from openbb_terminal.core.session.sources_handler import merge_sources
from openbb_terminal.rich_config import console


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


def apply_configs(configs: dict):
    """Apply configurations.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    # Saving the RICH_STYLE state allows user to change the default from 'hub' style to
    # some custom .richstyle.json file
    set_credentials_from_hub(configs)
    set_preferences_from_hub(configs, fields=["RICH_STYLE"])
    set_rich_style_from_hub(configs)
    set_chart_style_from_hub(configs)
    set_table_style_from_hub(configs)
    set_sources_from_hub(configs)


def set_credentials_from_hub(configs: dict):
    """Set credentials from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    if configs:
        credentials = configs.get("features_keys", {}) or {}
        credentials = {k: v for k, v in credentials.items() if v}
        for k, v in credentials.items():
            set_credential(k, v)


def set_preferences_from_hub(configs: dict, fields: Optional[List[str]] = None):
    """Set preferences from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    fields : Optional[List[str]]
        The fields to set, if None, all fields will be set.
    """
    if configs:
        preferences = configs.get("features_settings", {}) or {}
        for k, v in preferences.items():
            if not fields or k in fields:
                set_preference(k, v)


def set_rich_style_from_hub(configs: dict):
    """Set rich style from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    if configs:
        terminal_style = configs.get("features_terminal_style", {}) or {}
        if terminal_style:
            rich_style = terminal_style.get("theme", None)
            if rich_style:
                rich_style = {k: v.replace(" ", "") for k, v in rich_style.items()}
                try:
                    with open(
                        MISCELLANEOUS_DIRECTORY
                        / "styles"
                        / "user"
                        / "hub.richstyle.json",
                        "w",
                    ) as f:
                        json.dump(rich_style, f)

                    # Default to hub theme
                    preferences = configs.get("features_settings", {}) or {}
                    if "RICH_STYLE" not in preferences:
                        set_preference("RICH_STYLE", "hub")

                except Exception:
                    console.print("[red]Failed to set rich style.[/red]")


def set_chart_style_from_hub(configs: dict):
    """Set chart style from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    if configs:
        terminal_style = configs.get("features_terminal_style", {}) or {}
        if terminal_style:
            chart_style = terminal_style.get("chart", None)
            if chart_style:
                set_preference("CHART_STYLE", chart_style)
                # pylint: disable=import-outside-toplevel
                from openbb_terminal import theme

                theme.apply_style(chart_style)


def set_table_style_from_hub(configs: dict):
    """Set table style from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    if configs:
        terminal_style = configs.get("features_terminal_style", {}) or {}
        if terminal_style:
            table_style = terminal_style.get("table", None)
            if table_style:
                set_preference("TABLE_STYLE", table_style)


def set_sources_from_hub(configs: dict):
    """Set sources from hub.

    Parameters
    ----------
    configs : dict
        The configurations.
    """
    if configs:
        incoming = configs.get("features_sources", {}) or {}
        if incoming:
            choices = merge_sources(incoming=incoming, allowed=get_allowed_sources())
            set_sources(choices)
