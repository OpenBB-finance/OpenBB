from dataclasses import dataclass
import os.path
import json
import requests
from openbb_terminal import terminal_controller
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags
import jwt

BASE_URL = "http://127.0.0.1:8000/terminal/"
SUCCESS_MSG = "[green]\nLogin successful[/green]"


@dataclass(frozen=True)
class User:
    email: str
    uuid: str


def launch_terminal(login_info: dict):
    token = login_info.get("access_token", "")
    User.uuid = login_info.get("uuid", "")
    if token:
        decoded_info = jwt.decode(token, options={"verify_signature": False})
        User.email = decoded_info.get("sub", "")
        username = User.email[:User.email.find("@")]
        setattr(feature_flags, "USE_FLAIR", "[" + username + "] 🦋")

        terminal_controller.parse_args_and_run()


def request_token(email: str, password: str, save: bool) -> dict:
    """Request token and save it to file

    Parameters
    ----------
    email : str
        Email
    password : str
        Password

    """
    data = {
        "email": email,
        "password": password,
        "remember": True,
    }
    response = requests.post(BASE_URL + "login", json=data)
    code = response.status_code
    if code == 200:
        console.print(SUCCESS_MSG)
        login = response.json()
        if save:
            with open(SETTINGS_DIRECTORY / "login.json", "w") as outfile:
                outfile.write(json.dumps(login))
        return login
    if code == 401:
        console.print(f"[red]\n{str(response.json()['detail']).capitalize()}[/red]\n")
    elif code == 403:
        console.print(f"[red]\n{str(response.json()['message']).capitalize()}[/red]\n")
    else:
        console.print("[red]\nUnknown error.[/red]\n")
    return {}


def get_login_info() -> dict:
    file_path = SETTINGS_DIRECTORY / "login.json"
    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}


def is_login_valid(login_info: dict) -> bool:
    if "access_token" in login_info and "token_type" in login_info:
        response = requests.get(
            url=BASE_URL + "user",
            headers={
                "Authorization": f"{login_info['token_type'].title()} {login_info['access_token']}"
            },
        )
        if response.status_code == 200:
            console.print(SUCCESS_MSG)
            return True
    return False
