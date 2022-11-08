import json
import webbrowser

import requests

from openbb_terminal.core.config.paths import (
    USER_ROUTINES_DIRECTORY,
    SETTINGS_DIRECTORY,
)
from openbb_terminal.account import account_helpers as ah
from openbb_terminal.account import account_statics
from openbb_terminal.rich_config import console
from openbb_terminal import keys_model


def get_login(
    email: str,
    password: str,
    base_url: str = "https://payments.openbb.co",
    save: bool = True,
) -> dict:
    """Logs the user in.

    Parameters
    ----------
    email: str
        The user's email
    password: str
        The user's password
    base_url: str
        The url for the backend
    save: bool
        Whether or not to save the login information as json

    Returns
    ----------
    token: dict
        The user's login information
    """
    data = {
        "email": email,
        "password": password,
        "remember": True,
    }
    response = requests.post(base_url + "/terminal/login", json=data)
    code = response.status_code
    if code == 200:
        console.print("Login successful\n")
        login = response.json()
        if save:
            with open(SETTINGS_DIRECTORY / "login.json", "w") as outfile:
                outfile.write(json.dumps(login))
        return login
    if code == 401:
        console.print(f"[red]{response.json()['detail']}[/red]\n")
    elif code == 403:
        console.print(f"[red]{response.json()['message']}[/red]\n")
    else:
        console.print("[red]Unknown error[/red]\n")
    return {}


def get_register() -> None:
    """Opens a web browser for the user to register."""
    webbrowser.open("https://my.openbb.dev/register")


def get_upload(token: str, base_url: str = "https://payments.openbb.co") -> None:
    if not token:
        console.print("You need to login first\n")
        return

    settings = account_statics.features_settings
    keys = account_statics.features_keys
    features_settings = ah.clean_keys_dict(settings)
    features_keys = ah.clean_keys_dict(keys)
    data = {
        "features_settings": features_settings,
        "features_keys": features_keys,
    }
    response = requests.put(
        base_url + "/terminal/user",
        json=data,
        headers={"Authorization": token},
    )
    if response.status_code == 200:
        console.print("Successfully uploaded your settings and keys.")
    else:
        console.print("[red]Error uploading your settings and keys.[/red]")


def get_download(token: str, base_url: str = "https://payments.openbb.co") -> None:
    """Downloads's a user's settings and keys and then updates them locally

    Parameters
    ----------
    token: str
        The login token for a user
    base_url: str
        The url for the backend
    """
    if not token:
        console.print("You need to login first\n")
        return

    response = requests.get(
        base_url + "/terminal/user",
        headers={"Authorization": token},
    )
    if response.status_code != 200:
        console.print("[red]Error downloading your settings and keys.[/red]")
        return

    info = response.json()
    settings = info["features_settings"]
    keys = info["features_keys"]
    for key, value in settings.items():
        if key in account_statics.features_settings_objects and value:
            obj = account_statics.features_settings_objects[key]
            setattr(obj, key.replace("OPENBB_", ""), value)
            keys_model.set_key(key, value, True)
    for key, value in keys.items():
        if value:
            keys_model.set_key(key, value, True)

    console.print("Successfully downloaded your settings and keys.")


def get_send(
    token: str,
    script_file: str,
    script_name: str = "",
    base_url: str = "https://payments.openbb.co",
) -> None:
    """Send's the users script

    Parameters
    ----------
    token: str
        The login token for a user
    script_file: str
        The file for the script to submit
    script_name: str
        The desired name for the script to submit
    base_url: str
        The url for the backend
    """
    if not token:
        console.print("You need to login first\n")
        return

    if script_name:
        name = script_name
    else:
        name = script_file.replace(".openbb", "")

    script = ""
    with open(USER_ROUTINES_DIRECTORY / script_file) as f:
        script = "".join(f.readlines())

    data = {"name": name, "script": script}
    response = requests.post(
        base_url + "/terminal/script",
        json=data,
        headers={"Authorization": token},
    )
    if response.status_code == 200:
        console.print("Successfully uploaded your script.")
    else:
        console.print("[red]Error uploading your script.[/red]")


def get_get(
    token: str,
    script_name: str,
    base_url: str = "https://payments.openbb.co",
) -> None:
    """Gets a specific script

    Parameters
    ----------
    token: str
        The login token for a user
    script_name: str
        The desired name for the script to submit
    base_url: str
        The url for the backend
    """
    if not token:
        console.print("You need to login first\n")
        return

    print("Under construction")

    data = {"name": script_name}
    response = requests.get(
        base_url + "/terminal/script",
        json=data,
        headers={"Authorization": token},
    )
    if response.status_code == 200:
        console.print("Successfully uploaded your settings and keys.")
    else:
        console.print("[red]Error uploading your settings and keys.[/red]")
