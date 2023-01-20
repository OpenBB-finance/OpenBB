from typing import Tuple
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal import terminal_controller
from openbb_terminal.account.login_model import (
    apply_configs,
    fetch_user_configs,
    get_login_info,
    load_user_info,
    request_login_info,
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

    # Login successful
    load_user_info(login_info)
    fetch_user_configs()
    apply_configs()
    terminal_controller.parse_args_and_run()


def main():
    """Main function"""
    login_info = get_login_info()
    if not login_info:
        login_prompt()
    else:
        load_user_info(login_info)
        status = fetch_user_configs()
        if status == 200:
            apply_configs()
            terminal_controller.parse_args_and_run()
        else:
            login_prompt(welcome=False)


if __name__ == "__main__":
    main()
