from typing import Tuple

from prompt_toolkit import PromptSession

import openbb_terminal.core.session.local_model as Local
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.core.session.constants import REGISTER_URL
from openbb_terminal.core.session.session_model import (
    LoginStatus,
    create_session,
    login,
)
from openbb_terminal.rich_config import console


def display_welcome_message():
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "core" / "session" / "banner.txt") as f:
        console.print(f"[menu]{f.read()}[/menu]\n")
        console.print(f"Register     : [cmds]{REGISTER_URL}[/cmds]")
        console.print("Ask support  : [cmds]https://openbb.co/support[/cmds]")
        console.print(
            "[yellow]\nWARNING: This is a pre-release version published for testing.[/yellow]"
            "[yellow]\nBeware that your account will be deleted without notice.[/yellow]"
        )


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
    save = s.prompt(message="> Remember me? (y/n): ", is_password=False).lower() == "y"

    return email, password, save


def prompt(welcome=True):
    """Prompt and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    if welcome:
        display_welcome_message()

    while True:
        email, password, save = get_user_input()
        if not email:
            return launch_terminal()
        session = create_session(email, password, save)
        if isinstance(session, dict) and session:
            return login_and_launch(session=session)


def launch_terminal():
    """Launch terminal"""
    from openbb_terminal import terminal_controller

    terminal_controller.parse_args_and_run()


def login_and_launch(session: dict):
    """Login and launch terminal.

    Parameters
    ----------
    session : dict
        The session info.
    """
    status = login(session)
    if status in [LoginStatus.SUCCESS, LoginStatus.NO_RESPONSE]:
        launch_terminal()
    elif status == LoginStatus.FAILED:
        prompt(welcome=False)
    else:
        prompt(welcome=True)


def main():
    """Main function"""
    local_session = Local.get_session()
    if not local_session:
        prompt()
    else:
        login_and_launch(session=local_session)


if __name__ == "__main__":
    main()
