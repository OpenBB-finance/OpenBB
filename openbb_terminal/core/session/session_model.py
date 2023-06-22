import json
import sys
from enum import Enum
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt

import openbb_terminal.core.session.hub_model as Hub
import openbb_terminal.core.session.local_model as Local
from openbb_terminal.base_helpers import remove_log_handlers
from openbb_terminal.core.config.paths import HIST_FILE_PATH, SESSION_FILE_PATH
from openbb_terminal.core.models.user_model import ProfileModel, SourcesModel, UserModel
from openbb_terminal.core.session.current_user import (
    get_current_user,
    set_current_user,
    set_default_user,
)
from openbb_terminal.core.session.routines_handler import (
    download_routines,
    save_routine,
)
from openbb_terminal.core.session.sources_handler import get_updated_hub_sources
from openbb_terminal.core.session.utils import run_thread
from openbb_terminal.helper_funcs import system_clear
from openbb_terminal.loggers import setup_logging
from openbb_terminal.rich_config import console

# pylint: disable=consider-using-f-string


class LoginStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NO_RESPONSE = "no_response"
    UNAUTHORIZED = "unauthorized"


def create_session(email: str, password: str, save: bool) -> Dict[Any, Any]:
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


def create_session_from_token(token: str, save: bool) -> Dict[Any, Any]:
    """Create a session from token.

    Parameters
    ----------
    token : str
        The token.
    save : bool
        Save the session.
    """

    session = Hub.get_session_from_token(token)
    if session and save:
        Local.save_session(session)
    return session


def login(session: Dict, remember: bool = False) -> LoginStatus:
    """Login and load user info.

    Parameters
    ----------
    session : dict
        The session info.
    remember : bool, optional
        Remember the session, by default False
    """
    # Create a new user:
    #   credentials: stored in hub, but we fallback to local (.env)
    #   profile: stored in hub, so we set default here
    #   preferences: stored locally, so we use the current user preferences
    #   sources: stored in hub, so we set default here

    hub_user = UserModel(  # type: ignore
        credentials=get_current_user().credentials,
        profile=ProfileModel(),
        preferences=get_current_user().preferences,
        sources=SourcesModel(),
    )
    response = Hub.fetch_user_configs(session)
    if response is not None:
        if response.status_code == 200:
            configs = json.loads(response.content)
            email = configs.get("email", "")
            hub_user.profile.load_user_info(session, email, remember)
            set_current_user(hub_user)

            auth_header = hub_user.profile.get_auth_header()
            if sys.stdin.isatty():
                download_and_save_routines(auth_header)
                run_thread(
                    update_backend_sources,
                    {"auth_header": auth_header, "configs": configs},
                )
            Local.apply_configs(configs)
            Local.update_flair(get_current_user().profile.username)

            return LoginStatus.SUCCESS
        if response.status_code == 401:
            return LoginStatus.UNAUTHORIZED
        return LoginStatus.FAILED
    return LoginStatus.NO_RESPONSE


def download_and_save_routines(auth_header: str):
    """Download and save routines.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    """
    routines = download_routines(auth_header=auth_header)
    personal_routines_dict = routines[0]
    default_routines_dict = routines[1]
    try:
        for name, content in personal_routines_dict.items():
            save_routine(file_name=f"{name}.openbb", routine=content, force=True)
        for name, content in default_routines_dict.items():
            save_routine(file_name=f"{name}.openbb", routine=content, force=True)
    except Exception:
        console.print("[red]\nFailed to save routines.[/red]")


def update_backend_sources(auth_header, configs, silent: bool = True):
    """Update backend sources if new source or command path available.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    configs : Dict
        Dictionary with configs
    silent : bool
        Whether to silence the console output, by default True
    """
    console_print = console.print if not silent else lambda *args, **kwargs: None

    try:
        updated_sources = get_updated_hub_sources(configs)
        if updated_sources:
            Hub.upload_user_field(
                key="features_sources",
                value=updated_sources,
                auth_header=auth_header,
                silent=silent,
            )
    except Exception:
        console_print("[red]Failed to update backend sources.[/red]")


def logout(
    auth_header: Optional[str] = None,
    token: Optional[str] = None,
    cls: bool = False,
):
    """Logout and clear session.

    Parameters
    ----------
    auth_header : str, optional
        The authorization header, e.g. "Bearer <token>".
    token : str, optional
        The token to delete.
        In the terminal we want to delete the current session, so we use the user own token.
    cls : bool
        Clear the screen.
    """
    if cls:
        system_clear()

    if not auth_header or not token:
        return

    success = True

    r = Hub.delete_session(auth_header, token)
    if not r or r.status_code != 200:
        success = False

    if not Local.remove(SESSION_FILE_PATH):
        success = False

    if not Local.remove(HIST_FILE_PATH):
        success = False

    if not Local.remove(get_current_user().preferences.USER_ROUTINES_DIRECTORY / "hub"):
        success = False

    remove_log_handlers()
    set_default_user()
    setup_logging()

    plt.close("all")

    if success:
        console.print("[green]\nLogout successful.[/green]")
