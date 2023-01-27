import importlib
import logging
import os
import sys
import matplotlib.pyplot as plt
import openbb_terminal.session.local_model as Local
import openbb_terminal.session.hub_model as Hub
from openbb_terminal.session.user import User
from openbb_terminal.helper_funcs import system_clear
from openbb_terminal.rich_config import console


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
