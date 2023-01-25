from typing import Optional
import requests
from openbb_terminal.session.user import User

from openbb_terminal.rich_config import console

BASE_URL = "http://127.0.0.1:8000/"


def create_session(
    email: str, password: str, base_url=BASE_URL
) -> Optional[requests.Response]:
    """Create a session.

    Parameters
    ----------
    email : str
        The email.
    password : str
        The password.
    base_url : str, optional
        The base url, by default BASE_URL

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
        return requests.post(base_url + "login", json=data)
    except requests.exceptions.ConnectionError:
        console.print("[red]\nConnection error.[/red]")
        return None
    except Exception:
        console.print("[red]\nFailed to request login info.[/red]")
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
        console.print("\nLogin successful.", style="green")
        login = response.json()
        return login
    if response.status_code == 401:
        console.print("[red]\nWrong credentials.[/red]")
        return {}
    if response.status_code == 403:
        console.print("[red]\nUnverified email.[/red]")
        return {}
    console.print("[red]\nFailed to login.[/red]")
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
    response = create_session(email, password)
    if response is None:
        return {}
    return process_session_response(response)


def fetch_user_configs(session: dict) -> Optional[requests.Response]:
    """Fetch user configurations."""

    token_type = session.get("token_type", "")
    token = session.get("access_token", "")

    try:
        response = requests.get(
            url=BASE_URL + "terminal/user",
            headers={"Authorization": f"{token_type.title()} {token}"},
        )
        if response.status_code == 200:
            console.print("[green]\nFetched user configurations.[/green]")
        else:
            console.print("[red]\nFailed to fetch configurations.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print("[red]\nConnection error.[/red]")
        return None
    except Exception:
        console.print("[red]\nFailed to fetch configurations.[/red]")
        return None


def patch_user_configs(key: str, value: str, type_: str) -> Optional[requests.Response]:
    """Patch user configurations to the server.

    Parameters
    ----------
    key : str
        The key to patch.
    value : str
        The value to patch.
    type_ : str
        The type of the patch, either "keys" or "settings".

    Returns
    -------
    bool
        The status of the patch.
    """

    if type_ not in ["keys", "settings"]:
        console.print("[red]\nInvalid patch type.[/red]")
        return None

    data = {"key": f"features_{type_}.{key}", "value": value}

    try:
        response = requests.patch(
            url=BASE_URL + "terminal/user-json",
            headers={"Authorization": f"{User.TOKEN_TYPE.title()} {User.TOKEN}"},
            json=data,
        )
        if response.status_code == 200:
            console.print("[green]Saved remotely.[/green]")
        else:
            console.print("[red]Failed to save remotely.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        console.print("[red]Connection error.[/red]")
        return None
    except Exception:
        console.print("[red]Failed to save remotely.[/red]")
        return None


def put_user_configs() -> Optional[requests.Response]:
    """Push user configurations to the server."""
    pass


def delete_session():
    """Delete the session."""
    pass


def logout_everywhere() -> Optional[requests.Response]:
    """Request a remote logout.

    Returns
    -------
    bool
        The status of the logout.
    """
    try:
        response = requests.get(
            url=BASE_URL + "logout-everywhere",
            headers={"Authorization": f"{User.TOKEN_TYPE.title()} {User.TOKEN}"},
        )
        if response.status_code == 200:
            console.print("[green]\nLogged out remotely.[/green]")
            return response
        console.print("[red]\nFailed to logout remotely.[/red]")
        return None
    except requests.exceptions.ConnectionError:
        console.print("[red]\nConnection error.[/red]")
        return None
    except Exception:
        console.print("[red]\nFailed to logout remotely.[/red]")
        return None
