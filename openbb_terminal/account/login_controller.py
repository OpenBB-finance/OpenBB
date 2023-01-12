import argparse
from typing import List, Optional
import webbrowser
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.helper_funcs import get_flair
from openbb_terminal.terminal_helper import print_goodbye
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal import terminal_controller
from enum import Enum
from openbb_terminal.menu import session


class Action(Enum):
    """Class to handle controller action"""

    EXIT = -1
    DISPLAY_MENU = 1
    LAUNCH_TERMINAL = 420


class LoginController:
    """Login Controller"""

    CHOICES = ["login", "register", "h", "?", "help", "q", "quit", "e", "exit"]

    def __init__(self):
        self.controller_parser = argparse.ArgumentParser(
            add_help=False,
            prog="controller",
        )
        self.controller_parser.exit_on_error = False  # type: ignore
        self.controller_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer = NestedCompleter.from_nested_dict({c: {} for c in self.CHOICES})
        self.call_help()

    @staticmethod
    def parse_simple_args(
        parser: argparse.ArgumentParser, other_args: List[str]
    ) -> Optional[argparse.Namespace]:
        """Parse list of arguments into the supplied parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            Parser with predefined arguments
        other_args: List[str]
            List of arguments to parse

        Returns
        -------
        Optional[argparse.Namespace]:
            Namespace with parsed arguments
        """

        try:
            (ns_parser, unknown_args) = parser.parse_known_args(other_args)
        except SystemExit:
            return None

        if ns_parser.help:
            txt_help = parser.format_help()
            console.print(f"[help]{txt_help}[/help]")
            return None

        if unknown_args:
            console.print(
                f"The following args couldn't be interpreted: {unknown_args}\n"
            )

        return ns_parser

    def switch(self, an_input: str) -> Action:
        """Process and dispatch input

        Parameters
        ----------
        an_input: str
            Input string

        Returns
        -------
        Action
            Action of the controller
        """

        try:
            (
                controller_known_args,
                other_args,
            ) = self.controller_parser.parse_known_args(an_input.split())

            if controller_known_args.cmd in ("h", "help", "?"):
                return self.call_help()
            elif controller_known_args.cmd in ("e", "exit", "q", "quit"):
                return Action.EXIT
            elif controller_known_args.cmd == "register":
                return self.call_register(cmd_args=other_args)
            elif controller_known_args.cmd == "login":
                return self.call_login(cmd_args=other_args)
            else:
                console.print("Command not recognized!")
                return Action.DISPLAY_MENU
        except Exception:
            console.print("Command not recognized!")
            return Action.DISPLAY_MENU

    def call_help(self) -> Action:
        """Print help"""
        mt = MenuText("login/", 100)
        mt.add_cmd("login")
        mt.add_cmd("register")
        console.print(text=mt.menu_text, menu="Login")
        return Action.DISPLAY_MENU

    def call_register(self, cmd_args: List[str]) -> Action:
        """Call register

        Parameters
        ----------
        cmd_args: List[str]
            Other arguments

        Returns
        -------
        Action
            Action of the controller
        """
        cmd_parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="register",
            description="Register openbb account",
        )
        cmd_parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )
        ns_parser = self.parse_simple_args(cmd_parser, cmd_args)

        if ns_parser:
            webbrowser.open("https://my.openbb.co/register")

        return Action.DISPLAY_MENU

    def call_login(self, cmd_args: List[str]) -> Action:
        """Call login

        Parameters
        ----------
        cmd_args: List[str]
            Other arguments

        Returns
        -------
        Action
            Action of the controller
        """

        cmd_parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="login",
            description="Login to your openbb account",
        )
        cmd_parser.add_argument(
            "-e",
            "--email",
            type=str,
            dest="email",
            help="The email for the user",
            required="-h" not in cmd_args and "--help" not in cmd_args,
        )
        cmd_parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="The password for the user",
            required="-h" not in cmd_args and "--help" not in cmd_args,
        )
        cmd_parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )

        ns_parser = self.parse_simple_args(cmd_parser, cmd_args)
        if ns_parser:
            print("Login tried")
            return Action.LAUNCH_TERMINAL
        else:
            print("Failed to attempt login")
            return Action.DISPLAY_MENU


def main():
    """Main function"""
    login_controller = LoginController()

    action = Action.DISPLAY_MENU
    while action == Action.DISPLAY_MENU:
        _input = session.prompt(
            f"{get_flair()} $ ",
            completer=login_controller.completer,
            search_ignore_case=True,
        )
        action = login_controller.switch(an_input=_input)

    if action == Action.LAUNCH_TERMINAL:
        terminal_controller.parse_args_and_run()
    else:
        print_goodbye()


if __name__ == "__main__":
    main()
