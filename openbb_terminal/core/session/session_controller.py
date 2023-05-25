from typing import Dict, Optional, Tuple

from prompt_toolkit import PromptSession

import openbb_terminal.core.session.local_model as Local
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.constants import (
    REGISTER_URL,
    SUPPORT_URL,
)
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.session_model import (
    LoginStatus,
    create_session,
    login,
)
from openbb_terminal.rich_config import console
from openbb_terminal.terminal_helper import bootup


def display_welcome_message(links: bool = True) -> None:
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "core" / "session" / "banner.txt") as f:
        console.print(f"[menu]{f.read()}[/menu]\n")
        if links:
            console.print(f"Register : [cmds]{REGISTER_URL}[/cmds]")
            console.print(f"Support  : [cmds]{SUPPORT_URL}[/cmds]")


def get_user_input() -> Tuple[str, str, bool]:
    """Get user input

    Returns
    -------
    Tuple[str, str, bool]
        The user email, password and save login option.
    """
    console.print(
        "[info]\nPlease enter your credentials or press <ENTER> for guest mode:[/info]"
    )

    s: PromptSession = PromptSession()

    email = s.prompt(
        message="> Email/Username: ",
    )
    if not email:
        return "", "", False

    password = s.prompt(
        message="> Password: ",
        is_password=True,
    )
    remember = (
        s.prompt(message="> Remember me? (y/n): ", is_password=False).lower() == "y"
    )

    return email, password, remember


def pywry_login(welcome: bool = True):
    """Login using PyWry window and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    bootup()

    plots_backend().start(get_current_system().DEBUG_MODE)
    if plots_backend().isatty:
        if welcome:
            display_welcome_message(False)
        response = plots_backend().show_login_window()
    else:
        return prompt(welcome)

    if response is None:
        return launch_terminal()

    if isinstance(response, dict) and response:
        response.update(
            dict(
                token_type="bearer",
                information_complete=response.get("status", ""),
                access_token=response.get("accessToken", ""),
                primary_usage=response.get("primaryUsage", "personal"),
            )
        )
        return login_and_launch(response, response.get("remember", False))

    return pywry_login(welcome=False)


def prompt(welcome: bool = True):
    """Prompt and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    bootup()

    if welcome:
        display_welcome_message()

    while True:
        email, password, remember = get_user_input()
        if not email:
            return launch_terminal()
        session = create_session(email, password, remember)
        if isinstance(session, dict) and session:
            return login_and_launch(session, remember)


def launch_terminal():
    """Launch terminal"""
    # pylint: disable=import-outside-toplevel
    from openbb_terminal import terminal_controller

    terminal_controller.parse_args_and_run()


def login_and_launch(session: dict, remember: bool = False):
    """Login and launch terminal.

    Parameters
    ----------
    session : dict
        The session info.
    remember : bool, optional
        Remember the session, by default False
    """
    status = login(session, remember)
    if status in [LoginStatus.SUCCESS, LoginStatus.NO_RESPONSE]:
        launch_terminal()
    elif status == LoginStatus.FAILED:
        pywry_login(welcome=False)
    else:
        pywry_login(welcome=True)


def main(session: Optional[Dict] = None):
    """Main function"""

    local_session = Local.get_session() if session is None else session
    if not local_session:
        pywry_login()
    else:
        login_and_launch(session=local_session, remember=True)


if __name__ == "__main__":
    main()
