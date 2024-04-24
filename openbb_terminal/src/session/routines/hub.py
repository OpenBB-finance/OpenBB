"""Routines handler module."""

from typing import Optional

import requests

from src.config.constants import (
    CONNECTION_ERROR_MSG,
    CONNECTION_TIMEOUT_MSG,
    TIMEOUT,
)
from src.config.env import BackendEnvironment
from src.session.console import console
from src.session.settings import get_current_settings
from src.session.user import get_platform_user

# created dictionaries for personal and default routines with the structure
# {"file_name" :["script","personal/default"]}
# and stored dictionaries in list
# created new directory structure to account for personal and default routines


# pylint: disable=too-many-arguments
def upload(
    auth_header: str,
    name: str = "",
    description: str = "",
    routine: str = "",
    override: bool = False,
    tags: str = "",
    public: bool = False,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Send a routine to the server.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    name : str
        The name of the routine.
    routine : str
        The routine.
    override : bool
        Whether to override the routine if it already exists.
    tags : str
        The tags of the routine.
    public : bool
        Whether to make the routine public or not.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the post request.
    """
    data = {
        "name": name,
        "description": description,
        "script": routine,
        "override": override,
        "tags": tags,
        "version": get_current_settings().VERSION,
        "public": public,
    }
    try:
        response = requests.post(
            headers={"Authorization": auth_header},
            url=base_url + "terminal/script",
            json=data,
            timeout=timeout,
        )
        if response.status_code == 200:
            username = getattr(
                get_platform_user().profile.hub_session, "username", None
            )
            if not username:
                console.print("[red]No username found.[/red]")
                console.print("[red]Failed to upload your routine.[/red]")
                return None
            console.print("[green]Successfully uploaded your routine.[/]")

            run_env = BackendEnvironment.HUB_URL.rstrip("/")

            if public:
                console.print(
                    f"\n[yellow]Share or edit it at {run_env}/u/{username}/routine/{name.replace(' ', '-')}[/]"
                )
            else:
                console.print(f"\n[yellow]Go to {run_env} to edit this script,[/]")
                console.print(
                    f"[yellow]or even make it public so you can access it at "
                    f"{run_env}/u/{username}/routine/{name.replace(' ', '-')}[/]"
                )
        elif response.status_code != 409:  # 409: routine already exists
            console.print(
                "[red]" + response.json().get("detail", "Unknown error.") + "[/red]"
            )
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to upload your routine.[/red]")
        return None
