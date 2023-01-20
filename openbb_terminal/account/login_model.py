from pathlib import Path
import os.path
import json
from typing import Union
import jwt
import requests
from openbb_terminal import terminal_controller
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags
from openbb_terminal.account.statics import BASE_URL, Success, Failure
from openbb_terminal.account.user import User


def launch_terminal(login_info: dict):
    """Launch the terminal.

    Parameters
    ----------
    login_info : dict
        The login info.
    """
    User.token_type = login_info.get("token_type", "")
    User.token = login_info.get("access_token", "")
    User.uuid = login_info.get("uuid", "")
    if User.token:
        decoded_info = jwt.decode(User.token, options={"verify_signature": False})
        User.email = decoded_info.get("sub", "")

        if feature_flags.USE_FLAIR == ":openbb":
            username = User.email[: User.email.find("@")]
            setattr(feature_flags, "USE_FLAIR", "[" + username + "] 🦋")

        terminal_controller.parse_args_and_run()


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
        console.print(Success.VALID_LOGIN.value)
        login = response.json()
        if save:
            save_login_info(login, SETTINGS_DIRECTORY / "login.json")
        return login
    if response.status_code == 401:
        console.print(Failure.WRONG_CREDENTIALS.value)
        return Failure.WRONG_CREDENTIALS
    if response.status_code == 403:
        console.print(Failure.UNVERIFIED_EMAIL.value)
        return Failure.UNVERIFIED_EMAIL
    console.print("Failed to login.", style="red")
    return Failure.UNKNOWN_ERROR


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
        console.print(Failure.CONNECTION_ERROR.value)
        return Failure.CONNECTION_ERROR
    except Exception:
        console.print("Failed to request login info.", style="red")
        return Failure.UNKNOWN_ERROR
    return process_response(response, save)


def get_login_info() -> Union[dict, Failure]:
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
        console.print("Failed to get login info.", style="red")
        return Failure.UNKNOWN_ERROR
    return {}


def get_login_status(login_info: dict) -> Union[Success, Failure]:
    """Check if the login info is valid.

    Parameters
    ----------
    login_info : dict
        The login info to check.

    Returns
    -------
    Union[Success, Failure]
        The status of the login info, or an error.
    """
    if "access_token" in login_info and "token_type" in login_info:
        try:
            if (
                requests.get(
                    url=BASE_URL + "terminal/user",
                    headers={
                        "Authorization": f"{login_info['token_type'].title()} {login_info['access_token']}"
                    },
                ).status_code
                == 200
            ):
                console.print(Success.VALID_LOGIN.value)
                return Success.VALID_LOGIN
        except requests.exceptions.ConnectionError:
            console.print(Failure.CONNECTION_ERROR.value)
            return Failure.CONNECTION_ERROR
        except Exception:
            console.print("Failed to get login status.", style="red")
            return Failure.UNKNOWN_ERROR

    return Failure.INVALID_LOGIN
