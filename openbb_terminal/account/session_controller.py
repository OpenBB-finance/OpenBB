from typing import Tuple
import json
import requests
import openbb_terminal.account.local_model as Local
import openbb_terminal.account.hub_model as Hub
from openbb_terminal.account.user import User
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import terminal_controller


def display_welcome_message():
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "account" / "banner.txt") as f:
        console.print(f.read(), style="blue")


def get_user_input() -> Tuple[str, str, bool]:
    """Get user input

    Returns
    -------
    Tuple[str, str, bool]
        The user email, password and save login option.
    """
    console.print("\nPlease enter your credentials:", style="info")
    email = console.input("> Email: ", style="blue")
    password = console.getpass("> Password: ", style="blue")

    save_str = ""
    while save_str not in ["y", "n"]:
        save_str = console.input("> Keep me logged in (y/n): ", style="blue").lower()

    save = False
    if save_str == "y":
        save = True

    return email, password, save


def create_session(email: str, password: str, save: bool) -> dict:
    """Create a session."""

    session = Hub.get_session(email, password)
    if session and save:
        Local.save_session(session)
    return session


def login_prompt(welcome=True):
    """Login prompt and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    if welcome:
        display_welcome_message()

    while True:
        email, password, save = get_user_input()
        session = create_session(email, password, save)
        if isinstance(session, dict) and session:
            break

    login(session=session)


def login(session: dict):
    """Login and launch terminal.

    Parameters
    ----------
    session : dict
        The session info.
    """
    User.load_user_info(session)
    response = Hub.fetch_user_configs(session)
    if response:
        if response.status_code == 200:
            Local.apply_configs(configs=json.loads(response.content))
            terminal_controller.parse_args_and_run()
        else:
            login_prompt(welcome=False)
    else:
        login_prompt(welcome=True)


def main():
    """Main function"""
    local_session = Local.get_session()
    if not local_session:
        login_prompt()
    else:
        login(session=local_session)


if __name__ == "__main__":
    main()
