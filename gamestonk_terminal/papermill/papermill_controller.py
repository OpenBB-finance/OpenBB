"""Papermill Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import subprocess

from gamestonk_terminal.papermill import dark_pool_view, due_diligence_view
from gamestonk_terminal.papermill import econ_data_view

from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import config_terminal

# pylint: disable=R1732


class PapermillController:
    """Papermill Controller class"""

    def __init__(self):
        """Constructor"""
        self.papermill_parser = argparse.ArgumentParser(
            add_help=False, prog="papermill"
        )
        self.papermill_parser.add_argument(
            "cmd",
            choices=["cls", "?", "help", "q", "quit", "dd", "econ", "dp"],
        )

    def switch(self, an_input: str, proc: subprocess.Popen):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments
        proc : subprocess.Popen
            subprocess that calls jupyter notebook for report generation

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
        )(other_args, proc)

    def call_help(self, _):
        """Process Help command"""
        print_papermill()

    def call_q(self, _, proc):
        """Process Q command - quit the menu"""
        proc.kill()
        return False

    def call_quit(self, _, proc):
        """Process Quit command - quit the program"""
        proc.kill()
        return True

    def call_dd(self, other_args: List[str], _):
        """Process DD command"""
        due_diligence_view.due_diligence(other_args)

    def call_econ(self, other_args: List[str], _):
        """Process Econ command"""
        econ_data_view.econ_data(other_args)

    def call_dp(self, other_args: List[str], _):
        """Process DP command"""
        dark_pool_view.dark_pool(other_args)


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
    print("   dd            generate DUE DILIGENCE report")
    print("   econ          generate ECONOMIC DATA summary")
    print("   dp            generate DARK POOL report")
    print("")


def papermill_menu():
    """Papermill Menu"""
    pc = PapermillController()
    print_papermill()

    # Initialize jupyter notebook
    cmd = f"jupyter notebook --port={config_terminal.PAPERMILL_NOTEBOOK_REPORT_PORT}"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    while True:
        # Get input command from user
        an_input = input(f"{get_flair()} (mill)> ")

        try:
            process_input = pc.switch(an_input, proc)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
