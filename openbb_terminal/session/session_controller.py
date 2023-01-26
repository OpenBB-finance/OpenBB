from typing import Tuple
import json
import openbb_terminal.session.local_model as Local
import openbb_terminal.session.hub_model as Hub
from openbb_terminal.session.session_model import create_session
from openbb_terminal.session.user import User
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import terminal_controller


def display_welcome_message():
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "session" / "banner.txt") as f:
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
    save_str = console.input("> Keep me logged in (y/n): ", style="blue").lower()
    save = False
    if save_str == "y":
        save = True

    return email, password, save


def login_prompt(welcome=True, guest_allowed=True):
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
        if not email and not password:
            if guest_allowed:
                return terminal_controller.parse_args_and_run()
            continue

        session = create_session(email, password, save)
        if isinstance(session, dict) and session:
            break

    login(session=session)


# TODO: Move some login inside this function to the session_model.py
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


def main(guest_allowed: bool = True):
    """Main function"""
    local_session = Local.get_session()
    if not local_session:
        login_prompt(guest_allowed=guest_allowed)
    else:
        login(session=local_session)


if __name__ == "__main__":
    main()
