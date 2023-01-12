import argparse
from typing import List
from openbb_terminal.rich_config import console, MenuText


class LoginController:
    def __init__(self):
        self.print_help()

    def print_help(self):
        """Print help"""

        mt = MenuText("login/", 100)
        mt.add_cmd("login")
        mt.add_cmd("register")
        console.print(text=mt.menu_text, menu="Login")

    def call_login(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="login",
            description="Login to your openbb account",
        )
        parser.add_argument(
            "-e",
            "--email",
            type=str,
            dest="email",
            help="The email for the user",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="The password for the user",
            required="-h" not in other_args,
        )


if __name__ == "__main__":
    LoginController()
