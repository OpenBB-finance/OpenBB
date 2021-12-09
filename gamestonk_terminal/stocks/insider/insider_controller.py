"""Insider Controller Module"""
__docformat__ = "numpy"

import os
import argparse
import difflib
import configparser
from typing import List
import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.stocks.insider import (
    openinsider_view,
    businessinsider_view,
    finviz_view,
)

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

# pylint: disable=inconsistent-return-statements,too-many-public-methods


class InsiderController:
    """Screener Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "load",
    ]

    CHOICES_COMMANDS = [
        "view",
        "set",
        "filter",
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

    CHOICES_COMMANDS_WITH_TICKER = [
        "act",
        "lins",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_COMMANDS_WITH_TICKER

    def __init__(self, ticker: str, start: str, interval: str, stock: pd.DataFrame):
        """Constructor

        Parameters
        ----------
        stock : DataFrame
            Due diligence stock dataframe
        ticker : str
            Due diligence ticker symbol
        start : str
            Start date of the stock data
        interval : str
            Stock data interval
        """
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.preset = "template"
        self.insider_parser = argparse.ArgumentParser(add_help=False, prog="ins")
        self.insider_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_text = f"""
Insider Trading:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    load          load a specific stock ticker for analysis

PRESET: {self.preset}
    view          view available presets
    set           set one of the available presets
    filter        filter insiders based on preset

Latest:
    lcb           latest cluster boys
    lpsb          latest penny stock buys
    lit           latest insider trading (all filings)
    lip           latest insider purchases
    blip          big latest insider purchases ($25k+)
    blop          big latest officer purchases ($25k+)
    blcp          big latest CEO/CFO purchases ($25k+)
    lis           latest insider sales
    blis          big latest insider sales ($100k+)
    blos          big latest officer sales ($100k+)
    blcs          big latest CEO/CFO sales ($100k+)
Top:
    topt          top officer purchases today
    toppw         top officer purchases past week
    toppm         top officer purchases past month
    tipt          top insider purchases today
    tippw         top insider purchases past week
    tippm         top insider purchases past month
    tist          top insider sales today
    tispw         top insider sales past week
    tispm         top insider sales past month
{Style.DIM if not self.ticker else ''}
Ticker: {self.ticker}

    act           insider activity over time [Business Insider]
    lins          last insider trading of the company [Finviz]
{Style.RESET_ALL if not self.ticker else ''}"""
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

                filters_headers = [
                    "General",
                    "Date",
                    "TransactionFiling",
                    "Industry",
                    "InsiderTitle",
                    "Others",
                    "CompanyTotals",
                ]

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

        (known_args, other_args) = self.insider_parser.parse_known_args(
            an_input.split()
        )

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

    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
            " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_stock_candidate = stocks_helper.load(
            ns_parser.ticker,
        )

        if not df_stock_candidate.empty:
            if "." in ns_parser.ticker:
                self.ticker = ns_parser.ticker.upper().split(".")[0]
            else:
                self.ticker = ns_parser.ticker.upper()

    def call_view(self, other_args: List[str]):
        """Process view command"""
        self.view_available_presets(other_args)

    def call_set(self, other_args: List[str]):
        """Process set command"""
        self.set_preset(other_args)

    def call_filter(self, other_args: List[str]):
        """Process filter command"""
        return openinsider_view.print_insider_filter(other_args, self.preset)

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

    @try_except
    def call_act(self, other_args: List[str]):
        """Process act command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="act",
            description="""Prints insider activity over time [Source: Business Insider]""",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="number of latest insider activity.",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("No ticker loaded.  First use `load {ticker}` \n")
            return

        businessinsider_view.insider_activity(
            stock=self.stock,
            ticker=self.ticker,
            start=self.start,
            interval=self.interval,
            num=ns_parser.n_num,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
    def call_lins(self, other_args: List[str]):
        """Process lins command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lins",
            description="""
                Prints information about inside traders. The following fields are expected: Date, Relationship,
                Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="number of latest inside traders.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("No ticker loaded.  First use `load {ticker}` \n")
            return

        finviz_view.last_insider_activity(
            ticker=self.ticker,
            num=ns_parser.n_num,
            export=ns_parser.export,
        )


def menu(ticker: str, start: str, interval: str, stock: pd.DataFrame):
    """Insider Menu"""
    ins_controller = InsiderController(ticker, start, interval, stock)
    ins_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ins_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(ins)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(ins)> ")

        try:
            process_input = ins_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, ins_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
