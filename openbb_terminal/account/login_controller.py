from openbb_terminal.rich_config import console
from openbb_terminal.account.login_model import (
    get_login_info,
    is_login_valid,
    request_login_info,
    launch_terminal,
)


def display_welcome_message():
    console.print(
        "You need to be connected to use the installer version of OpenBB."
        "\nTo register please go on: https://my.openbb.co/register"
    )


def get_user_input():
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


def login_prompt():
    display_welcome_message()
    while True:
        email, password, save = get_user_input()
        login_info = request_login_info(email, password, save)
        if login_info:
            break

    return launch_terminal(login_info)


def main():
    """Main function"""
    login_info = get_login_info()
    if is_login_valid(login_info):
        return launch_terminal(login_info)
    return login_prompt()


if __name__ == "__main__":
    main()
