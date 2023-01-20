from pathlib import Path
import os.path
import json
from typing import Union
import jwt
import requests
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags as obbff
from openbb_terminal.account.statics import BASE_URL, Failure
from openbb_terminal.account import user


def load_user_info(login_info: dict):
    """Load user info from login info.

    Parameters
    ----------
    login_info : dict
        The login info.
    """
    user.TOKEN_TYPE = login_info.get("token_type", "")
    user.TOKEN = login_info.get("access_token", "")
    user.UUID = login_info.get("uuid", "")

    if user.TOKEN:
        decoded_info = jwt.decode(user.TOKEN, options={"verify_signature": False})
        user.EMAIL = decoded_info.get("sub", "")

        if obbff.USE_FLAIR == ":openbb":
            username = user.EMAIL[: user.EMAIL.find("@")]
            setattr(obbff, "USE_FLAIR", "[" + username + "] 🦋")


def save_login_info(data: dict, file_path: Path):
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
        console.print("Failed to save login info.", style="red")


def process_response(response: requests.Response, save: bool) -> Union[dict, Failure]:
    """Process the response from the server.

    Parameters
    ----------
    response : requests.Response
        The response from the server.
    save : bool
        Save login info.

    Returns
    -------
    Union[dict, Failure]
        The login info, or an error.
    """
    if response.status_code == 200:
        console.print("\nLogin successful.", style="green")
        login = response.json()
        if save:
            save_login_info(login, SETTINGS_DIRECTORY / "login.json")
        return login
    if response.status_code == 401:
        return Failure("[red]\nWrong credentials.[/red]")
    if response.status_code == 403:
        return Failure("[red]\nUnverified email.[/red]")
    return Failure("[red]\nFailed to login.[/red]")


def request_login_info(email: str, password: str, save: bool) -> Union[dict, Failure]:
    """Request login info from the server.

    Parameters
    ----------
    email : str
        The user email.
    password : str
        The user password.
    save : bool
        Save login info.

    Returns
    -------
    Union[dict, Failure]
        The login info, or an error.
    """
    data = {
        "email": email,
        "password": password,
        "remember": True,
    }

    try:
        response = requests.post(BASE_URL + "login", json=data)
    except requests.exceptions.ConnectionError:
        return Failure("[red]\nConnection error.[/red]")
    except Exception:
        return Failure("[red]\nFailed to request login info.[/red]")
    return process_response(response, save)


def get_login_info() -> dict:
    """Get the login info from the file.

    Returns
    -------
    dict
        The login info.
    """
    file_path = SETTINGS_DIRECTORY / "login.json"

    try:
        if os.path.isfile(file_path):
            with open(file_path) as file:
                return json.load(file)
    except Exception:
        console.print("[red]\nFailed to get login info.[/red]")
    return {}
