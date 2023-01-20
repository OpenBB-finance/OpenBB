import os.path
from typing import Union
import requests
from openbb_terminal.core.config.paths import SETTINGS_DIRECTORY
from openbb_terminal.helper_funcs import system_clear
from openbb_terminal.rich_config import console
from openbb_terminal.account.statics import BASE_URL, Success, Failure
from openbb_terminal.account.user import User
from openbb_terminal.account import login_controller


def remote_logout() -> Union[Success, Failure]:
    """Request a remote logout.

    Returns
    -------
    Union[Success, Failure]
        The status of the token invalidation, or an error.
    """
    try:
        if (
            requests.get(
                url=BASE_URL + "logout-everywhere",
                headers={"Authorization": f"{User.token_type.title()} {User.token}"},
            ).status_code
            == 200
        ):
            return Success("[green]\nLogged out remotely.[/green]")
        return Failure("[red]\nFailed to logout remotely.[/red]")
    except requests.exceptions.ConnectionError:
        return Failure("[red]\nConnection error.[/red]")
    except Exception:
        return Failure("[red]\nFailed to logout remotely.[/red]")


def remove_login_file() -> Union[Success, Failure]:
    """Remove the login file.

    Returns
    -------
    Success
        The status of the local logout.
    """

    try:
        file_path = SETTINGS_DIRECTORY / "login.json"
        if os.path.isfile(file_path):
            os.remove(file_path)
        return Success("[green]\nRemoved login info.[/green]")
    except Exception:
        return Failure("[red]\nFailed to remove login file.[/red]")


def logout():
    """Logout the user.

    Returns
    -------
    Union[Success, Failure]
        The status of the logout, or an error.
    """
    system_clear()
    remove_login_file()
    remote_logout()
    console.print("")
    login_controller.login_prompt(welcome=True)
