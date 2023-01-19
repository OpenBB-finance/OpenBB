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
    console.print("You need to be connected to use the installer version of OpenBB.\n")


def get_user_input():
    """Get user input

    Returns
    -------
    email : str
        User email
    password : str
        User password
    save : bool
        Save login info
    """
    console.print("\nPlease enter your credentials:")
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
    """Login prompt

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
    if login_info == Error.READ_ERROR:
        return login_prompt()

    status = get_login_status(login_info=login_info)
    if status == Status.VALID_LOGIN:
        launch_terminal(login_info=login_info)

    if status == Status.INVALID_LOGIN:
        login_prompt(welcome=False)


if __name__ == "__main__":
    main()
