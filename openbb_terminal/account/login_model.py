from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import os.path
import json
from typing import Union
import requests
from openbb_terminal import terminal_controller
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags
import jwt

BASE_URL = "http://127.0.0.1:8000/terminal/"


class Status(Enum):
    VALID_LOGIN = "[green]\nLogin successful.[/green]"
    INVALID_LOGIN = "[red]\nInvalid login.[/red]"


class Error(Enum):
    CONNECTION_ERROR = "[red]\nConnection error.[/red]"
    WRONG_CREDENTIALS = "[red]\nWrong credentials.[/red]"
    UNVERIFIED_EMAIL = "[red]\nUnverified email.[/red]"
    UNKNOWN_ERROR = "[red]\nUnknown error.[/red]"
    SAVE_ERROR = "[red]\nError saving login info.[/red]"
    READ_ERROR = "[red]\nError reading login info.[/red]"


@dataclass(frozen=True)
class User:
    email: str
    uuid: str


def launch_terminal(login_info: dict):
    """Launch the terminal.

    Parameters
    ----------
    login_info : dict
        The login info.
    """
    token = login_info.get("access_token", "")
    User.uuid = login_info.get("uuid", "")
    if token:
        decoded_info = jwt.decode(token, options={"verify_signature": False})
        User.email = decoded_info.get("sub", "")
        username = User.email[: User.email.find("@")]
        setattr(feature_flags, "USE_FLAIR", "[" + username + "] 🦋")

        terminal_controller.parse_args_and_run()


def write_to_file(data: dict, file_path: Path):
    """Write data to a file.

    Parameters
    ----------
    data : dict
        The data to write.
    file_path : Path
        The file path.
    """
    try:
        with open(file_path, "w") as outfile:
            outfile.write(json.dumps(data))
    except Exception:
        console.print(Error.SAVE_ERROR.value)


def process_response(response: requests.Response, save: bool) -> Union[dict, Error]:
    """Process the response from the server.

    Parameters
    ----------
    response : requests.Response
        The response from the server.
    save : bool
        Save login info.

    Returns
    -------
    Union[dict, Error]
        The login info, or an error.
    """
    if response.status_code == 200:
        console.print(Status.VALID_LOGIN.value)
        login = response.json()
        if save:
            write_to_file(login, SETTINGS_DIRECTORY / "login.json")
        return login

    if response.status_code == 401:
        console.print(Error.WRONG_CREDENTIALS.value)
        return Error.WRONG_CREDENTIALS
    elif response.status_code == 403:
        console.print(Error.UNVERIFIED_EMAIL.value)
        return Error.UNVERIFIED_EMAIL
    else:
        console.print(Error.UNKNOWN_ERROR.value)
        return Error.UNKNOWN_ERROR


def request_login_info(email: str, password: str, save: bool) -> Union[dict, Error]:
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
    Union[dict, Error]
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
        console.print(Error.CONNECTION_ERROR.value)
        return Error.CONNECTION_ERROR

    return process_response(response, save)


def get_login_info() -> Union[dict, Error]:
    """Get the login info from the file.

    Returns
    -------
    dict
        The login info.
    """
    file_path = SETTINGS_DIRECTORY / "login.json"

    try:
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
    except Exception:
        console.print(Error.READ_ERROR.value)
        return Error.READ_ERROR
    return {}


def get_login_status(login_info: dict) -> Union[Status, Error]:
    """Check if the login info is valid.

    Parameters
    ----------
    login_info : dict
        The login info to check.

    Returns
    -------
    Union[Status, Error]
        The status of the login info, or an error.
    """
    if "access_token" in login_info and "token_type" in login_info:
        try:
            if (
                requests.get(
                    url=BASE_URL + "user",
                    headers={
                        "Authorization": f"{login_info['token_type'].title()} {login_info['access_token']}"
                    },
                ).status_code
                == 200
            ):
                console.print(Status.VALID_LOGIN.value)
                return Status.VALID_LOGIN
        except requests.exceptions.ConnectionError:
            console.print(Error.CONNECTION_ERROR.value)
            return Error.CONNECTION_ERROR
    return Status.INVALID_LOGIN
