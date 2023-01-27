import importlib
import logging
import os
import sys
import json
from enum import Enum
import matplotlib.pyplot as plt
import openbb_terminal.session.local_model as Local
import openbb_terminal.session.hub_model as Hub
from openbb_terminal.session.user import User
from openbb_terminal.helper_funcs import system_clear
from openbb_terminal.rich_config import console


class LoginStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NO_RESPONSE = "no_response"


def create_session(email: str, password: str, save: bool) -> dict:
    """Create a session.

    Parameters
    ----------
    email : str
        The email.
    password : str
        The password.
    save : bool
        Save the session.
    """

    session = Hub.get_session(email, password)
    if session and save:
        Local.save_session(session)
    return session


def login(session: dict) -> LoginStatus:
    """Login and load user info.

    Parameters
    ----------
    session : dict
        The session info.
    """
    response = Hub.fetch_user_configs(session)
    if response:
        if response.status_code == 200:
            configs = json.loads(response.content)
            email = configs.get("email", "")
            User.load_user_info(session, email)
            Local.apply_configs(configs=configs)
            return LoginStatus.SUCCESS
        return LoginStatus.FAILED
    return LoginStatus.NO_RESPONSE


def logout(cls: bool = False):
    """Logout and clear session.

    Parameters
    ----------
    cls : bool
        Clear the screen.
    """
    if cls:
        system_clear()
    User.clear()

    # Clear openbb environment variables
    for v in os.environ:
        if v.startswith("OPENBB"):
            os.environ.pop(v)

    # Remove the log handlers - needs to be done before reloading modules
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Reload all openbb modules to clear memorized variables
    modules = sys.modules.copy()
    for module in modules:
        if module.startswith("openbb"):
            importlib.reload(sys.modules[module])

    Hub.delete_session()
    Local.remove_session_file()
    plt.close("all")
    console.print("[green]\nLogout successful.[/green]")
