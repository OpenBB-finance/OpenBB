import webbrowser
import requests

from openbb_terminal.core.config.paths import USER_ROUTINES_DIRECTORY
from openbb_terminal.account import account_helpers as ah
from openbb_terminal.account import account_statics
from openbb_terminal.rich_config import console
from openbb_terminal import keys_model


def get_login(
    email: str, password: str, base_url: str = "https://payments.openbb.co"
) -> dict:
    data = {
        "email": email,
        "password": password,
        "remember": True,
    }
    response = requests.post(base_url + "/terminal/login", json=data)
    code = response.status_code
    if code == 200:
        console.print("Login successful\n")
        return response.json()
    if code == 401:
        console.print(f"[red]{response.json()['detail']}[/red]\n")
    elif code == 403:
        console.print(f"[red]{response.json()['message']}[/red]\n")
    else:
        console.print("[red]Unknown error[/red]\n")
    return {}


def get_register() -> None:
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
    if not token:
        console.print("You need to login first\n")
        return

    if script_name:
        name = script_name
    else:
        name = script_file.replace(".openbb", "")

    script = ""
    with open(USER_ROUTINES_DIRECTORY / script_file) as f:
        for line in f.readlines():
            script += f"{line}\n"

    data = {"name": name, "script": script}
    print(data)
    response = requests.put(
        base_url + "/terminal/user",
        json=data,
        headers={"Authorization": token},
    )
    if response.status_code == 200:
        console.print("Successfully uploaded your settings and keys.")
    else:
        console.print("[red]Error uploading your settings and keys.[/red]")
