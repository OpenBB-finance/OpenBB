"""Screener Controller Module"""
__docformat__ = "numpy"

import os
import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.insider import openinsider_view


class InsiderController:
    """Screener Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "lcb",
        "lpsb",
        "lit",
        "lip",
        "blip",
        "blop",
        "blcp",
        "lis",
        "blis",
        "blos",
        "blcs",
        "topt",
        "toppw",
        "toppm",
        "tipt",
        "tippw",
        "tippm",
        "tist",
        "tispw",
        "tispm",
    ]

    def __init__(self):
        """Constructor"""
        self.insider_parser = argparse.ArgumentParser(add_help=False, prog="ins")
        self.insider_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/insider"
        )
        print("\nInsider Trading:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("Latest:")
        print("   lcb           latest cluster boys")
        print("   lpsb          latest penny stock buys")
        print("   lit           latest insider trading (all filings)")
        print("   lip           latest insider purchases")
        print("   blip          big latest insider purchases ($25k+)")
        print("   blop          big latest officer purchases ($25k+)")
        print("   blcp          big latest CEO/CFO purchases ($25k+)")
        print("   lis           latest insider sales")
        print("   blis          big latest insider sales ($100k+)")
        print("   blos          big latest officer sales ($100k+)")
        print("   blcs          big latest CEO/CFO sales ($100k+)")
        print("")
        print("Top:")
        print("   topt          top officer purchases today")
        print("   toppw         top officer purchases past week")
        print("   toppm         top officer purchases past month")
        print("   tipt          top insider purchases today")
        print("   tippw         top insider purchases past week")
        print("   tippm         top insider purchases past month")
        print("   tist          top insider sales today")
        print("   tispw         top insider sales past week")
        print("   tispm         top insider sales past month")
        print("")

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

        (known_args, other_args) = self.insider_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
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
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_lcb(self, other_args: List[str]):
        """Process latest-cluster-buys"""
        return openinsider_view.print_insider_data(other_args, "lcb")

    def call_lpsb(self, other_args: List[str]):
        """Process latest-penny-stock-buys"""
        return openinsider_view.print_insider_data(other_args, "lpsb")

    def call_lit(self, other_args: List[str]):
        """Process latest-insider-trading"""
        return openinsider_view.print_insider_data(other_args, "lit")

    def call_lip(self, other_args: List[str]):
        """Process insider-purchases"""
        return openinsider_view.print_insider_data(other_args, "lip")

    def call_blip(self, other_args: List[str]):
        """Process latest-insider-purchases-25k"""
        return openinsider_view.print_insider_data(other_args, "blip")

    def call_blop(self, other_args: List[str]):
        """Process latest-officer-purchases-25k"""
        return openinsider_view.print_insider_data(other_args, "blop")

    def call_blcp(self, other_args: List[str]):
        """Process latest-ceo-cfo-purchases-25k"""
        return openinsider_view.print_insider_data(other_args, "blcp")

    def call_lis(self, other_args: List[str]):
        """Process insider-sales"""
        return openinsider_view.print_insider_data(other_args, "lis")

    def call_blis(self, other_args: List[str]):
        """Process latest-insider-sales-100k"""
        return openinsider_view.print_insider_data(other_args, "blis")

    def call_blos(self, other_args: List[str]):
        """Process latest-officer-sales-100k"""
        return openinsider_view.print_insider_data(other_args, "blos")

    def call_blcs(self, other_args: List[str]):
        """Process latest-ceo-cfo-sales-100k"""
        return openinsider_view.print_insider_data(other_args, "blcs")

    def call_topt(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-day"""
        return openinsider_view.print_insider_data(other_args, "topt")

    def call_toppw(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-week"""
        return openinsider_view.print_insider_data(other_args, "toppw")

    def call_toppm(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-month"""
        return openinsider_view.print_insider_data(other_args, "toppm")

    def call_tipt(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-day"""
        return openinsider_view.print_insider_data(other_args, "tipt")

    def call_tippw(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-week"""
        return openinsider_view.print_insider_data(other_args, "tippw")

    def call_tippm(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-month"""
        return openinsider_view.print_insider_data(other_args, "tippm")

    def call_tist(self, other_args: List[str]):
        """Process top-insider-sales-of-the-day"""
        return openinsider_view.print_insider_data(other_args, "tist")

    def call_tispw(self, other_args: List[str]):
        """Process top-insider-sales-of-the-week"""
        return openinsider_view.print_insider_data(other_args, "tispw")

    def call_tispm(self, other_args: List[str]):
        """Process top-insider-sales-of-the-month"""
        return openinsider_view.print_insider_data(other_args, "tispm")


def menu():
    """Insider Menu"""

    ins_controller = InsiderController()
    ins_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ins_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (ins)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (ins)> ")

        try:
            process_input = ins_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
