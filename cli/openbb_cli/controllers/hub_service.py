"""Routines handler module."""

from typing import Optional

import requests
from openbb_cli.config.constants import (
    CONNECTION_ERROR_MSG,
    CONNECTION_TIMEOUT_MSG,
    TIMEOUT,
)
from openbb_cli.session import Session

# created dictionaries for personal and default routines with the structure
# {"file_name" :["script","personal/default"]}
# and stored dictionaries in list
# created new directory structure to account for personal and default routines


session = Session()


# pylint: disable=too-many-arguments
def upload_routine(
    auth_header: str,
    name: str = "",
    description: str = "",
    routine: str = "",
    override: bool = False,
    tags: str = "",
    public: bool = False,
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
        "version": session.settings.VERSION,
        "public": public,
    }
    _console = session.console
    try:
        response = requests.post(
            headers={"Authorization": auth_header},
            url=session.settings.BASE_URL + "/terminal/script",
            json=data,
            timeout=timeout,
        )
        if response.status_code == 200:
            username = getattr(session.user.profile.hub_session, "username", None)
            if not username:
                _console.print("[red]No username found.[/red]")
                _console.print("[red]Failed to upload your routine.[/red]")
                return None
            _console.print("[green]Successfully uploaded your routine.[/]")

            hub_url = session.settings.HUB_URL

            if public:
                _console.print(
                    f"\n[yellow]Share or edit it at {hub_url}/u/{username}/routine/{name.replace(' ', '-')}[/]"
                )
            else:
                _console.print(f"\n[yellow]Go to {hub_url} to edit this script,[/]")
                _console.print(
                    f"[yellow]or even make it public so you can access it at "
                    f"{hub_url}/u/{username}/routine/{name.replace(' ', '-')}[/]"
                )
        elif response.status_code != 409:  # 409: routine already exists
            _console.print(
                "[red]" + response.json().get("detail", "Unknown error.") + "[/red]"
            )
        return response
    except requests.exceptions.ConnectionError:
        _console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        _console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        _console.print("[red]Failed to upload your routine.[/red]")
        return None
