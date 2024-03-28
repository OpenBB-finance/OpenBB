from typing import List, Optional

import requests

from openbb_terminal.core.session.constants import (
    CONNECTION_ERROR_MSG,
    CONNECTION_TIMEOUT_MSG,
    DEFAULT_ROUTINES_URL,
    TIMEOUT,
    BackendEnvironment,
)
from openbb_terminal.core.session.current_settings import get_current_settings
from openbb_terminal.core.session.current_user import get_platform_user
from openbb_terminal.rich_config import console


# pylint: disable=too-many-arguments
def upload_routine(
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
            username = get_platform_user().profile.hub_session.username
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


def list_routines(
    auth_header: str,
    fields: Optional[List[str]] = None,
    page: int = 1,
    size: int = 10,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
    silent: bool = False,
) -> Optional[requests.Response]:
    """List all routines from the server.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    fields : Optional[List[str]]
        The fields to return, by default None
    page : int
        The page number.
    size : int
        The number of routines per page.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT
    silent : bool
        Whether to silence the console output, by default False

    Returns
    -------
    Optional[requests.Response]
        The response from the get request.
    """
    console_print = console.print if not silent else lambda *args, **kwargs: None
    try:
        if fields is None:
            fields = ["name", "description", "version", "updated_date"]

        fields_str = "%2C".join(fields)
        response = requests.get(
            headers={"Authorization": auth_header},
            url=f"{base_url}terminal/script?fields={fields_str}&page={page}&size={size}",
            timeout=timeout,
        )
        if response.status_code != 200:
            console_print("[red]Failed to list your routines.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console_print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console_print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console_print("[red]Failed to list your routines.[/red]")
        return None


def get_default_routines(
    url: str = DEFAULT_ROUTINES_URL, timeout: int = TIMEOUT, silent: bool = False
):
    """Get the default routines from CMS.

    Parameters
    ----------
    timeout : int
        The timeout, by default TIMEOUT
    silent : bool
        Whether to silence the console output, by default False

    Returns
    -------
    Optional[requests.Response]
        The response from the get request.
    """
    console_print = console.print if not silent else lambda *args, **kwargs: None
    try:
        response = requests.get(
            url=url,
            timeout=timeout,
        )
        if response.status_code != 200:
            console_print("[red]Failed to get default routines.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console_print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console_print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console_print("[red]Failed to get default routines.[/red]")
        return None
