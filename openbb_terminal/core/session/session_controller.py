from typing import Dict, Optional, Tuple

from prompt_toolkit import PromptSession

import openbb_terminal.core.session.local_model as Local
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.core.session.constants import REGISTER_URL, SUPPORT_URL
from openbb_terminal.core.session.session_model import (
    LoginStatus,
    create_session,
    login,
)
from openbb_terminal.rich_config import console
from openbb_terminal.terminal_helper import bootup


def display_welcome_message():
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "core" / "session" / "banner.txt") as f:
        console.print(f"[menu]{f.read()}[/menu]\n")
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
        message="> Email: ",
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


def prompt(welcome=True):
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
        prompt(welcome=False)
    else:
        prompt(welcome=True)


def main(session: Optional[Dict] = None):
    """Main function"""
    local_session = Local.get_session() if session is None else session
    if not local_session:
        prompt()
    else:
        login_and_launch(session=local_session, remember=True)


if __name__ == "__main__":
    main()
