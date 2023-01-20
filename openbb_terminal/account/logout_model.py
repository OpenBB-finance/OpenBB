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
            console.print(Success.REMOTE_LOGOUT.value)
            return Success.REMOTE_LOGOUT
        console.print("Failed to logout remotely.", style="red")
        return Failure.UNKNOWN_ERROR
    except requests.exceptions.ConnectionError:
        console.print(Failure.CONNECTION_ERROR.value)
        return Failure.CONNECTION_ERROR
    except Exception:
        console.print("Failed to logout remotely.", style="red")
        return Failure.UNKNOWN_ERROR


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
        console.print(Success.LOCAL_LOGOUT.value)
        return Success.LOCAL_LOGOUT
    except Exception:
        console.print("Failed to remove login file.", style="red")
        return Failure.UNKNOWN_ERROR


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
