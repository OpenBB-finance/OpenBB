"""Screener Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import configparser
import os
from typing import List

from colorama import Style
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.stocks.comparison_analysis import ca_controller
from gamestonk_terminal.stocks.screener import (
    finviz_view,
    yahoofinance_view,
    finviz_model,
)

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
        "view",
        "set",
        "historical",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "po",
        "ca",
    ]

    def __init__(self):
        """Constructor"""
        self.preset = "top_gainers"
        self.screen_tickers = []
        self.scr_parser = argparse.ArgumentParser(add_help=False, prog="scr")
        self.scr_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_text = f"""
Screener:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

    view          view available presets (defaults and customs)
    set           set one of the available presets

    PRESET: {self.preset}

    historical     view historical price
    overview       overview (e.g. Sector, Industry, Market Cap, Volume)
    valuation      valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y)
    financial      financial (e.g. Dividend, ROA, ROE, ROI, Earnings)
    ownership      ownership (e.g. Float, Insider Own, Short Ratio)
    performance    performance (e.g. Perf Week, Perf YTD, Volatility M)
    technical      technical (e.g. Beta, SMA50, 52W Low, RSI, Change)
    {Style.NORMAL if self.screen_tickers else Style.DIM}
Last screened tickers: {', '.join(self.screen_tickers)}
>   ca             take these to comparison analysis menu
>   po             take these to portoflio optimization menu{Style.RESET_ALL}
        """
        print(help_text)

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

                print("\nCustom Presets:")
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
                    print(
                        f"   {preset}{(50-len(preset)) * ' '}{description.split('Description: ')[1].replace('#', '')}"
                    )

                print("\nDefault Presets:")
                for signame, sigdesc in finviz_model.d_signals_desc.items():
                    print(f"   {signame}{(50-len(signame)) * ' '}{sigdesc}")
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
            ]
            + list(finviz_model.d_signals.keys()),
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
            system_clear()
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

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if not self.screen_tickers:
            print("Some tickers must be screened first through one of the presets!\n")
            return None

        return po_controller.menu(self.screen_tickers)

    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if not self.screen_tickers:
            print("Some tickers must be screened first through one of the presets!\n")
            return None

        return ca_controller.menu(self.screen_tickers)


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
            similar_cmd = difflib.get_close_matches(
                an_input, scr_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
