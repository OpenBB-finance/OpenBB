""" Disc Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.discovery import (
    alpha_vantage_view,
    ark_view,
    fidelity_view,
    finviz_view,
    seeking_alpha_view,
    short_interest_view,
    simply_wallst_view,
    spachero_view,
    unusual_whales_view,
    yahoo_finance_view,
    marketbeat_view,
    finra_ats_view,
    finnhub_view,
    stockgrid_view,
)


class DiscoveryController:
    """Discovery Controller"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "ipo",
        "map",
        "rtp_sectors",
        "gainers",
        "losers",
        "orders",
        "ark_orders",
        "up_earnings",
        "high_short",
        "low_float",
        "simply_wallst",
        "spachero",
        "uwhales",
        "valuation",
        "performance",
        "spectrum",
        "ratings",
        "latest",
        "trending",
        "darkpool",
        "darkshort",
        "shortvol",
    ]

    def __init__(self):
        """Constructor"""
        self.spectrum_img_to_delete = ""
        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/discovery"
        )
        print("\nDiscovery Mode:")
        print("   cls            clear screen")
        print("   ?/help         show this discovery menu again")
        print("   q              quit this menu, and shows back to main menu")
        print("   quit           quit to abandon program")
        print("")
        print("   ipo            past and future IPOs [Finnhub]")
        print("   map            S&P500 index stocks map [Finviz]")
        print("   rtp_sectors    real-time performance sectors [Alpha Vantage]")
        print("   gainers        show latest top gainers [Yahoo Finance]")
        print("   losers         show latest top losers [Yahoo Finance]")
        print("   orders         orders by Fidelity Customers [Fidelity]")
        print(
            "   ark_orders     orders by ARK Investment Management LLC [www.cathiesark.com]"
        )
        print("   up_earnings    upcoming earnings release dates [Seeking Alpha]")
        print(
            "   high_short     show top high short interest stocks of over 20% ratio [www.highshortinterest.com]"
        )
        print(
            "   low_float      show low float stocks under 10M shares float [www.lowfloat.com]"
        )
        print("   simply_wallst  Simply Wall St. research data [Simply Wall St.]")
        print("   spachero       great website for SPACs research [SpacHero]")
        print("   uwhales        good website for SPACs research [UnusualWhales]")
        print("   valuation      valuation of sectors, industry, country [Finviz]")
        print("   performance    performance of sectors, industry, country [Finviz]")
        print("   spectrum       spectrum of sectors, industry, country [Finviz]")
        print("   latest         latest news [Seeking Alpha]")
        print("   trending       trending news [Seeking Alpha]")
        print("   ratings        top ratings updates [MarketBeat]")
        print(
            "   darkpool       promising tickers based on dark pool shares regression [FINRA]"
        )
        print("   darkshort      dark pool short position [Stockgrid.io]")
        print("   shortvol       short interest and days to cover [Stockgrid.io]")
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

        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

        # Due to Finviz implementation of Spectrum, we delete the generated spectrum figure
        # after saving it and displaying it to the user
        if self.spectrum_img_to_delete:
            # Confirm that file exists
            if os.path.isfile(self.spectrum_img_to_delete + ".jpg"):
                os.remove(self.spectrum_img_to_delete + ".jpg")
                self.spectrum_img_to_delete = ""

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

    def call_ipo(self, other_args: List[str]):
        """Process ipo command"""
        finnhub_view.ipo_calendar(other_args)

    def call_map(self, other_args: List[str]):
        """Process map command"""
        finviz_view.map_sp500_view(other_args)

    def call_rtp_sectors(self, other_args: List[str]):
        """Process rtp_sectors command"""
        alpha_vantage_view.sectors_view(other_args)

    def call_gainers(self, other_args: List[str]):
        """Process gainers command"""
        yahoo_finance_view.gainers_view(other_args)

    def call_losers(self, other_args: List[str]):
        """Process losers command"""
        yahoo_finance_view.losers_view(other_args)

    def call_orders(self, other_args: List[str]):
        """Process orders command"""
        fidelity_view.orders_view(other_args)

    def call_ark_orders(self, other_args: List[str]):
        """Process ark_orders command"""
        ark_view.ark_orders_view(other_args)

    def call_up_earnings(self, other_args: List[str]):
        """Process up_earnings command"""
        seeking_alpha_view.earnings_release_dates_view(other_args)

    def call_high_short(self, other_args: List[str]):
        """Process high_short command"""
        short_interest_view.high_short_interest_view(other_args)

    def call_low_float(self, other_args: List[str]):
        """Process low_float command"""
        short_interest_view.low_float_view(other_args)

    def call_simply_wallst(self, other_args: List[str]):
        """Process simply_wallst command"""
        simply_wallst_view.simply_wallst_view(other_args)

    def call_spachero(self, other_args: List[str]):
        """Process spachero command"""
        spachero_view.spachero_view(other_args)

    def call_uwhales(self, other_args: List[str]):
        """Process uwhales command"""
        unusual_whales_view.unusual_whales_view(other_args)

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        finviz_view.view_group_data(other_args, "valuation")

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        finviz_view.view_group_data(other_args, "performance")

    def call_spectrum(self, other_args: List[str]):
        """Process spectrum command"""
        self.spectrum_img_to_delete = finviz_view.view_group_data(
            other_args, "spectrum"
        )

    def call_latest(self, other_args: List[str]):
        """Process latest command"""
        seeking_alpha_view.latest_news_view(other_args)

    def call_trending(self, other_args: List[str]):
        """Process trending command"""
        seeking_alpha_view.trending_news_view(other_args)

    def call_ratings(self, other_args: List[str]):
        """Process ratings command"""
        marketbeat_view.ratings_view(other_args)

    def call_darkpool(self, other_args: List[str]):
        """Process darkpool command"""
        finra_ats_view.dark_pool(other_args)

    def call_darkshort(self, other_args: List[str]):
        """Process darkshort command"""
        stockgrid_view.darkshort(other_args)

    def call_shortvol(self, other_args: List[str]):
        """Process shortvol command"""
        stockgrid_view.shortvol(other_args)


def menu():
    """Discovery Menu"""

    disc_controller = DiscoveryController()
    disc_controller.call_help(None)

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in disc_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (disc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (disc)> ")

        try:
            plt.close("all")

            process_input = disc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
