import datetime
import json
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

import requests
from jose import jwt

from openbb_terminal.core.session.constants import (
    CONNECTION_ERROR_MSG,
    CONNECTION_TIMEOUT_MSG,
    DEFAULT_ROUTINES_URL,
    TIMEOUT,
    BackendEnvironment,
)
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.rich_config import console


def create_session(
    email: str,
    password: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Create a session.

    Parameters
    ----------
    email : str
        The email.
    password : str
        The password.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the login request.
    """
    try:
        data = {
            "email": email,
            "password": password,
            "remember": True,
        }
        return requests.post(url=base_url + "login", json=data, timeout=timeout)
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("\n[red]Failed to request login info.[/red]")
        return None


def check_token_expiration(token: str):
    """Raises ExpiredSignatureError if the token is expired."""
    header_data = jwt.get_unverified_header(token)

    tok = jwt.decode(
        token,
        key="",
        algorithms=[header_data["alg"]],
        options={"verify_signature": False, "verify_exp": True},
    )
    expiration_time = datetime.datetime.fromtimestamp(tok["exp"])
    console.print(f"Token expires at {expiration_time}")


def create_session_from_token(
    token: str, base_url: str = BackendEnvironment.BASE_URL, timeout: int = TIMEOUT
):
    """Create a session from token.

    Parameters
    ----------
    token : str
        The token.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT
    """

    try:
        check_token_expiration(token)
        data = {
            "token": token,
        }
        return requests.post(url=base_url + "sdk/login", json=data, timeout=timeout)
    except jwt.ExpiredSignatureError:
        console.print(
            "\n[red]Token expired. Please regenerate on the OpenBB Hub (my.openbb.co).[/red]"
        )
        return None
    except requests.exceptions.ConnectionError:
        console.print("\n[red]Connection error.[/red]")
        return None
    except requests.exceptions.Timeout:
        console.print("\n[red]Connection timeout.[/red]")
        return None
    except Exception:
        console.print("\n[red]Failed to request login info.[/red]")
        return None


def delete_session(
    auth_header: str,
    token: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Delete the session.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    token : str
        The token to delete.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the logout request.
    """
    try:
        response = requests.get(
            url=base_url + "logout",
            headers={"Authorization": auth_header},
            json={"token": token},
            timeout=timeout,
        )
        if response.status_code != 200:
            console.print("[red]Failed to delete server session.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[bold red]Failed to delete server session.[/bold red]")
        return None


def process_session_response(response: requests.Response) -> dict:
    """Process the response from the login request.

    Parameters
    ----------
    response : requests.Response
        The response from the login request.

    Returns
    -------
    dict
        The login info.
    """
    if response.status_code == 200:
        login = response.json()
        return login
    if response.status_code == 401:
        console.print("\n[red]Wrong credentials.[/red]")
        return {}
    if response.status_code == 403:
        console.print("\n[red]Unverified email.[/red]")
        return {}
    console.print("\n[red]Failed to login.[/red]")
    return {}


def get_session(email: str, password: str) -> dict:
    """Get the session info.

    Parameters
    ----------
    email : str
        The email.
    password : str
        The password.

    Returns
    -------
    dict
        The session info.
    """
    response = create_session(email, password, base_url=BackendEnvironment.BASE_URL)
    if response is None:
        return {}
    return process_session_response(response)


def get_session_from_token(token: str) -> dict:
    """Get the session info from token.

    Parameters
    ----------
    token : str
        The token.

    Returns
    -------
    dict
        The session info.
    """
    response = create_session_from_token(token, base_url=BackendEnvironment.BASE_URL)
    if response is None:
        return {}
    return process_session_response(response)


def fetch_user_configs(
    session: dict, base_url: str = BackendEnvironment.BASE_URL, timeout: int = TIMEOUT
) -> Optional[requests.Response]:
    """Fetch user configurations.

    Parameters
    ----------
    session : dict
        The session info.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the get request.
    """
    token_type = session.get("token_type", "")
    token = session.get("access_token", "")

    try:
        response = requests.get(
            url=base_url + "terminal/user",
            headers={"Authorization": f"{token_type.title()} {token}"},
            timeout=timeout,
        )
        if response.status_code not in [200, 401]:  # 401: invalid token
            console.print("[red]\nFailed to fetch configurations.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]\nFailed to fetch configurations.[/red]")
        return None


def clear_user_configs(
    config: str,
    auth_header: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Clear user configurations to the server.

    Parameters
    ----------
    config : str
        The config to clear.
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the put request.
    """
    data: Dict[str, dict] = {config: {}}

    try:
        response = requests.put(
            url=base_url + "user",
            headers={"Authorization": auth_header},
            json=data,
            timeout=timeout,
        )
        if response.status_code == 200:
            console.print("[green]Cleared data.[/green]")
        else:
            console.print("[red]Failed to clear data.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to clear data.[/red]")
        return None


def upload_user_field(
    key: str,
    value: Any,
    auth_header: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
    silent: bool = False,
) -> Optional[requests.Response]:
    """Send user field to the server.

    Parameters
    ----------
    key : str
        The key to put, e.g. 'features_settings', 'features_keys', 'features_sources'.
    value : Any
        The value to put.
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT
    silent : bool
        Whether to silence the console output, by default False

    Returns
    -------
    Optional[requests.Response]
        The response from the put request.
    """
    console_print = console.print if not silent else lambda *args, **kwargs: None
    try:
        data: Dict[str, dict] = {key: value}

        console_print("Sending to OpenBB hub...")
        response = requests.put(
            url=base_url + "user",
            headers={"Authorization": auth_header},
            json=data,
            timeout=timeout,
        )
        if response.status_code == 200:
            console_print("[green]Saved remotely.[/green]")
        else:
            console_print("[red]Failed to save remotely.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console_print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console_print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console_print("[red]Failed to save remotely.[/red]")
        return None


def upload_config(
    key: str,
    value: str,
    type_: Literal["settings", "terminal_style"],
    auth_header: str,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Patch user configurations to the server.

    Parameters
    ----------
    key : str
        The key to patch.
    value : str
        The value to patch.
    type_ : Literal["settings", "terminal_style"]
        The type of the patch.
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the patch request.
    """
    if type_ not in ["settings", "terminal_style"]:
        console.print("[red]\nInvalid patch type.[/red]")
        return None

    data = {"key": f"features_{type_}.{key}", "value": value}

    try:
        console.print("Sending to OpenBB hub...")
        response = requests.patch(
            url=BackendEnvironment.BASE_URL + "terminal/user",
            headers={"Authorization": auth_header},
            json=data,
            timeout=timeout,
        )
        if response.status_code == 200:
            console.print("[green]Saved remotely.[/green]")
        else:
            console.print("[red]Failed to save remotely.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to save remotely.[/red]")
        return None


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
        "version": get_current_system().VERSION,
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
            username = get_current_user().profile.username
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


def download_routine(
    auth_header: str,
    uuid: UUID,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Download a routine from the server.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    uuid : UUID
        The uuid of the routine.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the get request.
    """
    try:
        response = requests.get(
            headers={"Authorization": auth_header},
            url=base_url + "terminal/script/" + uuid,  # type: ignore
            timeout=timeout,
        )
        if response.status_code == 404:
            console.print("[red]Routine not found.[/red]")
        elif response.status_code != 200:
            console.print("[red]Failed to download your routine.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to download your routine.[/red]")
        return None


def delete_routine(
    auth_header: str,
    uuid: UUID,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """Delete a routine from the server.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    uuid : UUID
        The uuid of the routine.
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
        The response from the delete request.
    """
    try:
        response = requests.delete(
            headers={"Authorization": auth_header},
            url=base_url + "terminal/script/" + uuid,  # type: ignore
            timeout=timeout,
        )
        if response.status_code == 200:
            console.print("[green]Successfully deleted your routine.[/green]")
        elif response.status_code == 404:
            console.print("[red]Routine not found.[/red]")
        else:
            console.print("[red]Failed to delete your routine.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to delete your routine.[/red]")
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


def generate_personal_access_token(
    auth_header: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
    days: int = 30,
) -> Optional[requests.Response]:
    """
    Generate an OpenBB Personal Access Token.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT
    days : int
        The number of days the token should be valid for.

    Returns
    -------
    Optional[requests.Response]
    """

    url = f"{base_url}sdk/token"

    payload = json.dumps({"days": days})
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }

    try:
        response = requests.put(url=url, headers=headers, data=payload, timeout=timeout)

        if response.status_code != 200:
            console.print("[red]Failed to generate personal access token.[/red]")

        return response

    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to generate personal access token.[/red]")
        return None


def get_personal_access_token(
    auth_header: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """
    Show the user's OpenBB Personal Access Token.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
    """

    url = f"{base_url}sdk/token"

    headers = {"Authorization": auth_header}

    try:
        response = requests.get(url=url, headers=headers, timeout=timeout)

        if response.status_code == 404:
            console.print("[red]No personal access token found.[/red]")
        elif response.status_code != 200:
            console.print("[red]Failed to get personal access token.[/red]")

        return response

    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to get personal access token.[/red]")
        return None


def revoke_personal_access_token(
    auth_header: str,
    base_url: str = BackendEnvironment.BASE_URL,
    timeout: int = TIMEOUT,
) -> Optional[requests.Response]:
    """
    Delete the user's OpenBB Personal Access Token.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    base_url : str
        The base url, by default BASE_URL
    timeout : int
        The timeout, by default TIMEOUT

    Returns
    -------
    Optional[requests.Response]
    """

    url = f"{base_url}sdk/token"

    headers = {"Authorization": auth_header}

    try:
        response = requests.delete(url=url, headers=headers, timeout=timeout)

        if response.status_code not in [200, 202]:
            console.print("[red]Failed to revoke personal access token.[/red]")

        return response

    except requests.exceptions.ConnectionError:
        console.print(f"\n{CONNECTION_ERROR_MSG}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"\n{CONNECTION_TIMEOUT_MSG}")
        return None
    except Exception:
        console.print("[red]Failed to revoke personal access token.[/red]")
        return None
