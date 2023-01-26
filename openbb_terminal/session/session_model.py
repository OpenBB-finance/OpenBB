import importlib
import os
import sys
import matplotlib.pyplot as plt
import openbb_terminal.session.local_model as Local
import openbb_terminal.session.hub_model as Hub
from openbb_terminal.session.user import User
from openbb_terminal.helper_funcs import system_clear


def create_session(email: str, password: str, save: bool) -> dict:
    """Create a session."""

    session = Hub.get_session(email, password)
    if session and save:
        Local.save_session(session)
    return session


def logout():
    """Logout and clear session."""
    system_clear()
    User.clear()

    # Clear openbb environment variables
    for v in os.environ:
        if v.startswith("OPENBB"):
            os.environ.pop(v)

    # Reload all openbb modules to clear memorized variables
    modules = sys.modules.copy()
    for module in modules:
        if module.startswith("openbb"):
            importlib.reload(sys.modules[module])

    Hub.delete_session()
    Local.remove_session_file()
    plt.close("all")
