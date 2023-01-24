from typing import Optional
import requests
from openbb_terminal.account.user import User

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


def process_session_response(response: Optional[requests.Response]) -> dict:
    """Process the response from the login request.

    Parameters
    ----------
    response : Optional[requests.Response]
        The response from the login request.

    Returns
    -------
    dict
        The login info.
    """
    if response is None:
        return {}

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


def patch_user_configs(data: dict) -> Optional[requests.Response]:
    """Patch user configurations."""
    # When available on the server just need to send the changed configs, not all of them.
    # Adapt this to Colin implementation.
    pass


def put_user_configs(data: dict) -> bool:
    """Push user configurations to the server."""
    try:
        response = requests.put(
            url=BASE_URL + "terminal/user",
            headers={"Authorization": f"{User.TOKEN_TYPE.title()} {User.TOKEN}"},
            json=data,
        )
        if response.status_code == 200:
            console.print("[green]\nPushed user configurations.[/green]")
        else:
            console.print("[red]\nFailed to push configurations.[/red]")
        return True
    except requests.exceptions.ConnectionError:
        console.print("[red]\nConnection error.[/red]")
        return False
    except Exception:
        console.print("[red]\nFailed to push configurations.[/red]")
        return False


def logout_everywhere() -> bool:
    """Request a remote logout.

    Returns
    -------
    bool
        The status of the logout.
    """
    try:
        if (
            requests.get(
                url=BASE_URL + "logout-everywhere",
                headers={"Authorization": f"{User.TOKEN_TYPE.title()} {User.TOKEN}"},
            ).status_code
            == 200
        ):
            console.print("[green]\nLogged out remotely.[/green]")
            return True
        console.print("[red]\nFailed to logout remotely.[/red]")
        return False
    except requests.exceptions.ConnectionError:
        console.print("[red]\nConnection error.[/red]")
        return False
    except Exception:
        console.print("[red]\nFailed to logout remotely.[/red]")
        return False


def delete_session():
    """Delete the session."""
    pass
