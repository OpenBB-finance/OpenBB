"""Papermill Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List

from gamestonk_terminal.papermill import due_diligence_view
from gamestonk_terminal.papermill import econ_data_view

from gamestonk_terminal.helper_funcs import get_flair


class PapermillController:
    """Papermill Controller class"""

    def __init__(self):
        """Constructor"""
        self.papermill_parser = argparse.ArgumentParser(
            add_help=False, prog="papermill"
        )
        self.papermill_parser.add_argument(
            "cmd",
            choices=["cls", "?", "help", "q", "quit", "dd", "econ"],
        )

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.papermill_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            print_papermill()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        print_papermill()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_dd(self, other_args: List[str]):
        """Process DD command"""
        due_diligence_view.due_diligence(other_args)

    def call_econ(self, other_args: List[str]):
        """Process Econ command"""
        econ_data_view.econ_data(other_args)


def print_papermill():
    """Print help"""
    print(
        "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/papermill"
    )
    print("\nPapermill Reports:")
    print("   cls           clear screen")
    print("   ?/help        show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   dd            run papermill to generate due diligence summary")
    print("   econ          run papermill to generate economic data summary")
    print("")

    return


def papermill_menu():
    """Papermill Menu"""

    pc = PapermillController()

    print_papermill()

    while True:
        # Get input command from user
        an_input = input(f"{get_flair()} (mill)> ")

        try:
            process_input = pc.switch(an_input)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
