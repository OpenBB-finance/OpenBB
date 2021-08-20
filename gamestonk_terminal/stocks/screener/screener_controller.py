"""Screener Controller Module"""
__docformat__ = "numpy"

import argparse
import configparser
import os
from typing import List

import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_int_range,
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.stocks.screener import finviz_view, yahoofinance_view

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

# pylint: disable=E1121


class ScreenerController:
    """Screener Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "shorted",
        "under",
        "view",
        "set",
        "historical",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "signals",
        "po",
    ]

    def __init__(self):
        """Constructor"""
        self.preset = "template"
        self.screen_tickers = []
        self.scr_parser = argparse.ArgumentParser(add_help=False, prog="scr")
        self.scr_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks/screener"
        )
        print("\nScreener:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("Yahoo Finance:")
        print("   shorted       most shorted stocks")
        print("   under         most undervalued growth stocks")
        print("")
        print("Finviz:")
        print("   view          view available presets")
        print("   set           set one of the available presets")
        print("")
        print(f"PRESET: {self.preset}")
        print("")
        print("   historical     view historical price")
        print("   overview       overview (e.g. Sector, Industry, Market Cap, Volume)")
        print("   valuation      valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y)")
        print("   financial      financial (e.g. Dividend, ROA, ROE, ROI, Earnings)")
        print("   ownership      ownership (e.g. Float, Insider Own, Short Ratio)")
        print("   performance    performance (e.g. Perf Week, Perf YTD, Volatility M)")
        print("   technical      technical (e.g. Beta, SMA50, 52W Low, RSI, Change)")
        print("")
        print("   signals        view filter signals (e.g. -s top_gainers)")
        print("")
        if self.screen_tickers:
            print(f"Last screened tickers: {', '.join(self.screen_tickers)}")
            print("")
            print("   > po           portfolio optimization for last screened tickers")
            print("")

    @staticmethod
    def view_available_presets(other_args: List[str]):
        """View available presets."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="view",
            description="""View available presets under presets folder.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            help="View specific preset",
            default="",
            choices=[
                preset.split(".")[0]
                for preset in os.listdir(presets_path)
                if preset[-4:] == ".ini"
            ],
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-p")
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.preset:
                preset_filter = configparser.RawConfigParser()
                preset_filter.optionxform = str  # type: ignore
                preset_filter.read(presets_path + ns_parser.preset + ".ini")

                filters_headers = ["General", "Descriptive", "Fundamental", "Technical"]

                print("")
                for filter_header in filters_headers:
                    print(f" - {filter_header} -")
                    d_filters = {**preset_filter[filter_header]}
                    d_filters = {k: v for k, v in d_filters.items() if v}
                    if d_filters:
                        max_len = len(max(d_filters, key=len))
                        for key, value in d_filters.items():
                            print(f"{key}{(max_len-len(key))*' '}: {value}")
                    print("")

            else:
                presets = [
                    preset.split(".")[0]
                    for preset in os.listdir(presets_path)
                    if preset[-4:] == ".ini"
                ]

                for preset in presets:
                    with open(
                        presets_path + preset + ".ini",
                        encoding="utf8",
                    ) as f:
                        description = ""
                        for line in f:
                            if line.strip() == "[General]":
                                break
                            description += line.strip()
                    print(f"\nPRESET: {preset}")
                    print(description.split("Description: ")[1].replace("#", ""))
                print("")

        except Exception as e:
            print(e)

    def set_preset(self, other_args: List[str]):
        """Set preset"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset from under presets folder.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default="template",
            help="Filter presets",
            choices=[
                preset.split(".")[0]
                for preset in os.listdir(presets_path)
                if preset[-4:] == ".ini"
            ],
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-p")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.preset = ns_parser.preset

        except Exception as e:
            print(e)

        print("")
        return

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

        (known_args, other_args) = self.scr_parser.parse_known_args(an_input.split())

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

    def call_view(self, other_args: List[str]):
        """Process view command"""
        self.view_available_presets(other_args)

    def call_set(self, other_args: List[str]):
        """Process set command"""
        self.set_preset(other_args)

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        self.screen_tickers = yahoofinance_view.historical(other_args, self.preset)

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        self.screen_tickers = finviz_view.screener(other_args, self.preset, "overview")

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        self.screen_tickers = finviz_view.screener(other_args, self.preset, "valuation")

    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        self.screen_tickers = finviz_view.screener(other_args, self.preset, "financial")

    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        self.screen_tickers = finviz_view.screener(other_args, self.preset, "ownership")

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        self.screen_tickers = finviz_view.screener(
            other_args, self.preset, "performance"
        )

    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        self.screen_tickers = finviz_view.screener(other_args, self.preset, "technical")

    def call_signals(self, other_args: List[str]):
        """Process signals command"""
        finviz_view.view_signals(other_args)

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        return po_controller.menu(self.screen_tickers)

    def call_shorted(self, other_args: List[str]):
        """Process shorted command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shorted",
            description="Print up to 25 top ticker most shorted. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the most shorted stocks to retrieve.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            yahoofinance_view.display_most_shorted(
                num_stocks=ns_parser.num,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_under(self, other_args: List[str]):
        """Process under command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="under",
            description="Print up to 25 top ticker losers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the undervalued stocks to retrieve.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            yahoofinance_view.display_undervalued(
                num_stocks=ns_parser.num,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")


def menu():
    """Screener Menu"""

    scr_controller = ScreenerController()
    scr_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in scr_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(scr)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(scr)> ")

        try:
            plt.close("all")

            process_input = scr_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
