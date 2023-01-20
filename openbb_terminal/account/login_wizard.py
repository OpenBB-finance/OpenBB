from typing import Tuple
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal.account.login_model import (
    Status,
    Error,
    get_login_info,
    get_login_status,
    request_login_info,
    launch_terminal,
)


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
        login_info = request_login_info(email, password, save)
        if isinstance(login_info, dict) and login_info:
            break

    launch_terminal(login_info)


def main():
    """Main function"""
    login_info = get_login_info()
    if login_info == Error.UNKNOWN_ERROR or not login_info:
        login_prompt()
    else:
        status = get_login_status(login_info=login_info)
        if status == Status.VALID_LOGIN:
            launch_terminal(login_info=login_info)
        if status == Status.INVALID_LOGIN:
            login_prompt(welcome=False)


if __name__ == "__main__":
    main()
