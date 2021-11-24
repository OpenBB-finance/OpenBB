"""Options Controller Module."""
__docformat__ = "numpy"
# pylint:disable=too-many-lines


import argparse
import os
from datetime import datetime, timedelta
from typing import List

import matplotlib.pyplot as plt
from colorama import Style
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    valid_date,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.options import (
    barchart_view,
    calculator_view,
    fdscanner_view,
    syncretism_view,
    tradier_model,
    tradier_view,
    yfinance_model,
    yfinance_view,
    alphaquery_view,
    chartexchange_view,
    payoff_controller,
    pricing_controller,
)

# pylint: disable=R1710


class OptionsController:
    """Options Controller class."""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "pres",
        "disp",
        "scr",
        "calc",
        "yf",
        "tr",
        "info",
        "pcr",
        "load",
        "exp",
        "vol",
        "voi",
        "oi",
        "hist",
        "chains",
        "grhist",
        "unu",
        "plot",
        "parity",
    ]

    CHOICES_MENUS = [
        "payoff",
        "pricing",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    PRESET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

    POSSIBLE_GREEKS = [
        "iv",
        "gamma",
        "theta",
        "vega",
        "delta",
        "rho",
        "premium",
    ]

    def __init__(self, ticker):
        """Constructor"""
        self.ticker = ticker

        if ticker:
            if TRADIER_TOKEN == "REPLACE_ME":
                print("Loaded expiry dates from Yahoo Finance")
                self.expiry_dates = yfinance_model.option_expirations(self.ticker)
            else:
                print("Loaded expiry dates from Tradier")
                self.expiry_dates = tradier_model.option_expirations(self.ticker)

        self.selected_date = ""

        self.op_parser = argparse.ArgumentParser(add_help=False, prog="payoff")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.prices = pd.DataFrame(columns=["Price", "Chance"])

    def print_help(self):
        """Print help."""
        colored = self.ticker and self.selected_date
        help_text = f"""
What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

Explore:
    pres          display available preset templates
    disp          display filters for selected preset
    scr           output screener options [Syncretism.io]
    unu           show unusual options activity [fdscanner.com]
    calc          basic call/put PnL calculator

Current Ticker: {self.ticker or None}
Current Expiry: {self.selected_date or None}

    load          load new ticker
    exp           see and set expiration dates
{"" if self.ticker else Style.DIM}
    pcr           display put call ratio for ticker [AlphaQuery.com]{Style.DIM if not colored else ''}
    info          display option information (volatility, IV rank etc) [Barchart.com]
    chains        display option chains with greeks [Tradier]
    oi            plot open interest [Tradier/YF]
    vol           plot volume [Tradier/YF]
    voi           plot volume and open interest [Tradier/YF]
    hist          plot option history [Tradier]
    grhist        plot option greek history [Syncretism.io]
    plot          plot variables provided by the user [Yfinance]
    parity        shows whether options are above or below expected price [Yfinance]

>   payoff        shows payoff diagram for a selection of options [Yfinance]
>   pricing       shows options pricing and risk neutral valuation [Yfinance]
{Style.RESET_ALL if not colored else ''}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input.

        Returns
        -------
        MENU_GO_BACK, MENU_QUIT, MENU_RESET
            MENU_GO_BACK - Show main context menu again
            MENU_QUIT - Quit terminal
            MENU_RESET - Reset terminal and go back to same previous menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.op_parser.parse_known_args(an_input.split())

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
        """Process Help command."""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    @try_except
    def call_calc(self, other_args: List[str]):
        """Process calc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="calc",
            description="Calculate profit or loss for given option settings.",
        )
        parser.add_argument(
            "--put",
            action="store_true",
            default=False,
            dest="put",
            help="Flag to calculate put option",
        )
        parser.add_argument(
            "--sell",
            action="store_true",
            default=False,
            dest="sell",
            help="Flag to get profit chart of selling contract",
        )
        parser.add_argument(
            "-s",
            "--strike",
            type=float,
            dest="strike",
            help="Option strike price",
            default=10,
        )
        parser.add_argument(
            "-p",
            "--premium",
            type=float,
            dest="premium",
            help="Premium price",
            default=1,
        )
        parser.add_argument(
            "-m",
            "--min",
            type=float,
            dest="min",
            help="Min price to look at",
            default=-1,
            required="-M" in other_args,
        )
        parser.add_argument(
            "-M",
            "--max",
            type=float,
            dest="max",
            help="Max price to look at",
            default=-1,
            required="-m" in other_args,
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.min > 0 and ns_parser.max > 0:
            pars = {"x_min": ns_parser.min, "x_max": ns_parser.max}
        else:
            pars = {}
        calculator_view.view_calculator(
            strike=ns_parser.strike,
            premium=ns_parser.premium,
            put=ns_parser.put,
            sell=ns_parser.sell,
            **pars,
        )

    @try_except
    def call_unu(self, other_args: List[str]):
        """Process act command"""
        parser = argparse.ArgumentParser(
            prog="unu",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="This command gets unusual options from fdscanner.com",
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="num",
            type=int,
            default=20,
            help="Number of options to show.  Each scraped page gives 20 results.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            nargs="+",
            default="Vol/OI",
            choices=["Strike", "Vol/OI", "Vol", "OI", "Bid", "Ask", "Exp", "Ticker"],
            help="Column to sort by.  Vol/OI is the default and typical variable to be considered unusual.",
        )
        parser.add_argument(
            "-a",
            "--ascending",
            dest="ascend",
            default=False,
            action="store_true",
            help="Flag to sort in ascending order",
        )
        parser.add_argument(
            "-p",
            "--puts_only",
            dest="puts_only",
            help="Flag to show puts only",
            default=False,
            action="store_true",
        )
        parser.add_argument(
            "-c",
            "--calls_only",
            dest="calls_only",
            help="Flag to show calls only",
            default=False,
            action="store_true",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.calls_only and ns_parser.puts_only:
            print(
                "Cannot return puts only and calls only.  Either use one or neither\n."
            )
            return
        fdscanner_view.display_options(
            num=ns_parser.num,
            sort_column=ns_parser.sortby,
            export=ns_parser.export,
            ascending=ns_parser.ascend,
            calls_only=ns_parser.calls_only,
            puts_only=ns_parser.puts_only,
        )

    @try_except
    def call_pcr(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pcr",
            description="Display put to call ratio for ticker [AlphaQuery.com]",
        )
        parser.add_argument(
            "-l",
            "-length",
            help="Window length to get",
            dest="length",
            choices=[10, 20, 30, 60, 90, 120, 150, 180],
            default=30,
            type=int,
        )
        parser.add_argument(
            "-s",
            "--start-date",
            help="Start date for plot",
            type=valid_date,
            default=datetime.now() - timedelta(days=366),
            dest="start",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        alphaquery_view.display_put_call_ratio(
            ticker=self.ticker,
            window=ns_parser.length,
            start_date=ns_parser.start.strftime("%Y-%m-%d"),
            export=ns_parser.export,
        )

    def call_info(self, other_args: List[str]):
        """Process info command"""
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Display option data [Source: Barchart.com]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        barchart_view.print_options_data(ticker=self.ticker, export=ns_parser.export)

    @try_except
    def call_pres(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pres",
            description="""View available presets under presets folder.""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        presets = [f for f in os.listdir(self.PRESET_PATH) if f.endswith(".ini")]

        for preset in presets:
            print(preset)
        print("")

    @try_except
    def call_disp(self, other_args: List[str]):
        """Process disp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="disp",
            description="""View filters for a selected preset.""",
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
                for preset in os.listdir(self.PRESET_PATH)
                if preset[-4:] == ".ini"
            ],
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        syncretism_view.view_available_presets(
            preset=ns_parser.preset, presets_path=self.PRESET_PATH
        )

    @try_except
    def call_scr(self, other_args: List[str]):
        """Process scr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="scr",
            description="""Screener filter output from https://ops.syncretism.io/index.html.
        Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration;
        IV: Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest;
        Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market Day Low;
        SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money;
        PC: Price Change; PB: Price-to-book. """,
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
                for preset in os.listdir(self.PRESET_PATH)
                if preset[-4:] == ".ini"
            ],
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        parser.add_argument(
            "-n",
            "--num",
            type=check_positive,
            default=-1,
            help="Number of random entries to show.  Default shows all",
            dest="n_show",
        )

        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        syncretism_view.view_screener_output(
            preset=ns_parser.preset,
            presets_path=self.PRESET_PATH,
            n_show=ns_parser.n_show,
            export=ns_parser.export,
        )

    @try_except
    def call_grhist(self, other_args: List[str]):
        """Process grhist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="grhist",
            description="Plot historical option greeks.",
        )
        parser.add_argument(
            "-s",
            "--strike",
            dest="strike",
            type=float,
            required="--chain" in other_args or "-h" not in other_args,
            help="Strike price to look at",
        )
        parser.add_argument(
            "--put",
            dest="put",
            action="store_true",
            default=False,
            help="Flag for showing put option",
        )
        parser.add_argument(
            "-g",
            "--greek",
            dest="greek",
            type=str,
            choices=self.POSSIBLE_GREEKS,
            default="delta",
            help="Greek column to select",
        )
        parser.add_argument(
            "--chain", dest="chain_id", default="", type=str, help="OCC option symbol"
        )
        parser.add_argument(
            "--raw",
            dest="raw",
            action="store_true",
            default=False,
            help="Display raw data",
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="num",
            default=20,
            help="Number of raw data rows to show",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.  First use `load {ticker}` \n")
            return
        if not self.selected_date:
            print("No expiry loaded.  First use `exp {expiry date}` \n")
            return
        syncretism_view.view_historical_greeks(
            ticker=self.ticker,
            expiry=self.selected_date,
            strike=ns_parser.strike,
            greek=ns_parser.greek,
            chain_id=ns_parser.chain_id,
            put=ns_parser.put,
            raw=ns_parser.raw,
            n_show=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load a ticker into option menu",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        parser.add_argument(
            "--source",
            choices=["tr", "yf"],
            dest="source",
            default=None,
            help="Source to get option expirations from",
        )
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        self.ticker = ns_parser.ticker.upper()

        if TRADIER_TOKEN == "REPLACE_ME" or ns_parser.source == "yf":
            self.expiry_dates = yfinance_model.option_expirations(self.ticker)
        else:
            self.expiry_dates = tradier_model.option_expirations(self.ticker)
        print("")

    @try_except
    def call_exp(self, other_args: List[str]):
        """Process exp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exp",
            description="See and set expiration date",
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            action="store",
            type=int,
            default=-1,
            choices=range(len(self.expiry_dates)),
            help="Select index for expiry date.",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=str,
            choices=self.expiry_dates + [""],
            help="Select date (YYYY-MM-DD)",
            default="",
        )

        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("Please load a ticker using `load {ticker}.\n")
            return
        # Print possible expiry dates
        if ns_parser.index == -1 and not ns_parser.date:
            print("\nAvailable expiry dates:")
            for i, d in enumerate(self.expiry_dates):
                print(f"   {(2 - len(str(i))) * ' '}{i}.  {d}")
            print("")
        elif ns_parser.date:
            if ns_parser.date in self.expiry_dates:
                print(f"Expiration set to {ns_parser.date} \n")
                self.selected_date = ns_parser.date
            else:
                print("Expiration not an option")
        else:
            expiry_date = self.expiry_dates[ns_parser.index]
            print(f"Expiration set to {expiry_date} \n")
            self.selected_date = expiry_date

    @try_except
    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hist",
            description="Gets historical quotes for given option chain",
        )
        parser.add_argument(
            "-s",
            "--strike",
            dest="strike",
            type=float,
            required="--chain" not in other_args and "-h" not in other_args,
            help="Strike price to look at",
        )
        parser.add_argument(
            "-p",
            "--put",
            dest="put",
            action="store_true",
            default=False,
            help="Flag for showing put option",
        )
        parser.add_argument(
            "--chain", dest="chain_id", type=str, help="OCC option symbol"
        )
        parser.add_argument(
            "-r",
            "--raw",
            dest="raw",
            action="store_true",
            default=False,
            help="Display raw data",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        parser.add_argument(
            "--source",
            dest="source",
            type=str,
            choices=["td", "ce"],
            default="ce" if TRADIER_TOKEN == "REPLACE_ME" else "td",
            help="Choose Tradier(TD) or ChartExchange (CE), only affects raw data",
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="num",
            type=int,
            help="Number of data rows to show",
        )

        if (
            other_args
            and ("-s" not in other_args and "--strike" not in other_args)
            and "-h" not in other_args
            and "--chain" not in other_args
        ):
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.  First use `load ` \n")
            return
        if not self.selected_date:
            print("No expiry loaded.  First use `exp ` \n")
            return
        if ns_parser.source.lower() == "ce":
            chartexchange_view.display_raw(
                ns_parser.export,
                self.ticker,
                self.selected_date,
                not ns_parser.put,
                ns_parser.strike,
                ns_parser.num,
            )
            return

        if TRADIER_TOKEN == "REPLACE_ME":
            print("TRADIER TOKEN not supplied. \n")
            return

        tradier_view.display_historical(
            ticker=self.ticker,
            expiry=self.selected_date,
            strike=ns_parser.strike,
            put=ns_parser.put,
            export=ns_parser.export,
            raw=ns_parser.raw,
            chain_id=ns_parser.chain_id,
        )

    @try_except
    def call_chains(self, other_args: List[str]):
        """Process chains command"""
        parser = argparse.ArgumentParser(
            prog="chains",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display option chains",
        )
        parser.add_argument(
            "-c",
            "--calls",
            action="store_true",
            default=False,
            dest="calls",
            help="Flag to show calls only",
        )
        parser.add_argument(
            "-p",
            "--puts",
            action="store_true",
            default=False,
            dest="puts",
            help="Flag to show puts only",
        )
        parser.add_argument(
            "-m",
            "--min",
            dest="min_sp",
            type=float,
            default=-1,
            help="minimum strike price to consider.",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_sp",
            type=float,
            default=-1,
            help="maximum strike price to consider.",
        )
        parser.add_argument(
            "-d",
            "--display",
            dest="to_display",
            default=tradier_model.default_columns,
            type=tradier_view.check_valid_option_chains_headers,
            help="columns to look at.  Columns can be:  {bid, ask, strike, bidsize, asksize, volume, open_interest, "
            "delta, gamma, theta, vega, ask_iv, bid_iv, mid_iv} ",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.  First use `load {ticker}` \n")
            return
        if not self.selected_date:
            print("No expiry loaded.  First use `exp {expiry date}` \n")
            return
        if TRADIER_TOKEN == "REPLACE_ME":
            print("TRADIER TOKEN not supplied. \n")
            return
        tradier_view.display_chains(
            ticker=self.ticker,
            expiry=self.selected_date,
            to_display=ns_parser.to_display,
            min_sp=ns_parser.min_sp,
            max_sp=ns_parser.max_sp,
            calls_only=ns_parser.calls,
            puts_only=ns_parser.puts,
            export=ns_parser.export,
        )

    @try_except
    def call_vol(self, other_args: List[str]):
        """Process vol command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vol",
            description="Plot volume.  Volume refers to the number of contracts traded today.",
        )
        parser.add_argument(
            "-m",
            "--min",
            default=-1,
            type=float,
            help="Min strike to plot",
            dest="min",
        )
        parser.add_argument(
            "-M",
            "--max",
            default=-1,
            type=float,
            help="Max strike to plot",
            dest="max",
        )
        parser.add_argument(
            "-c",
            "--calls",
            action="store_true",
            default=False,
            dest="calls",
            help="Flag to plot call options only",
        )
        parser.add_argument(
            "-p",
            "--puts",
            action="store_true",
            default=False,
            dest="puts",
            help="Flag to plot put options only",
        )
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="tr",
            choices=["tr", "yf"],
            dest="source",
            help="Source to get data from",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.\n")
            return
        if ns_parser.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            tradier_view.plot_vol(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min,
                max_sp=ns_parser.max,
                calls_only=ns_parser.calls,
                puts_only=ns_parser.puts,
                export=ns_parser.export,
            )
        else:
            yfinance_view.plot_vol(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min,
                max_sp=ns_parser.max,
                calls_only=ns_parser.calls,
                puts_only=ns_parser.puts,
                export=ns_parser.export,
            )

    @try_except
    def call_voi(self, other_args: List[str]):
        """Process voi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="voi",
            description="""
                        Plots Volume + Open Interest of calls vs puts.
                    """,
        )
        parser.add_argument(
            "-v",
            "--minv",
            dest="min_vol",
            type=float,
            default=-1,
            help="minimum volume (considering open interest) threshold of the plot.",
        )
        parser.add_argument(
            "-m",
            "--min",
            dest="min_sp",
            type=float,
            default=-1,
            help="minimum strike price to consider in the plot.",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_sp",
            type=float,
            default=-1,
            help="maximum strike price to consider in the plot.",
        )
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="tr",
            choices=["tr", "yf"],
            dest="source",
            help="Source to get data from",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.\n")
            return
        if ns_parser.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            tradier_view.plot_volume_open_interest(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min_sp,
                max_sp=ns_parser.max_sp,
                min_vol=ns_parser.min_vol,
                export=ns_parser.export,
            )
        else:
            yfinance_view.plot_volume_open_interest(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min_sp,
                max_sp=ns_parser.max_sp,
                min_vol=ns_parser.min_vol,
                export=ns_parser.export,
            )

        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.")
            return

    @try_except
    def call_payoff(self, _):
        """Process payoff command"""
        if not self.ticker or not self.selected_date:
            print("Ticker and expiration required.\n")
            return None
        ret = payoff_controller.menu(self.ticker, self.selected_date)
        if ret is False:
            self.print_help()
        else:
            return True

    @try_except
    def call_oi(self, other_args: List[str]):
        """Process oi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oi",
            description="Plot open interest.  Open interest represents the number of contracts that exist.",
        )
        parser.add_argument(
            "-m",
            "--min",
            default=-1,
            type=float,
            help="Min strike to plot",
            dest="min",
        )
        parser.add_argument(
            "-M",
            "--max",
            default=-1,
            type=float,
            help="Max strike to plot",
            dest="max",
        )
        parser.add_argument(
            "-c",
            "--calls",
            action="store_true",
            default=False,
            dest="calls",
            help="Flag to plot call options only",
        )
        parser.add_argument(
            "-p",
            "--puts",
            action="store_true",
            default=False,
            dest="puts",
            help="Flag to plot put options only",
        )
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="tr",
            choices=["tr", "yf"],
            dest="source",
            help="Source to get data from",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required. \n")
            return
        if ns_parser.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            tradier_view.plot_oi(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min,
                max_sp=ns_parser.max,
                calls_only=ns_parser.calls,
                puts_only=ns_parser.puts,
                export=ns_parser.export,
            )
        else:
            yfinance_view.plot_oi(
                ticker=self.ticker,
                expiry=self.selected_date,
                min_sp=ns_parser.min,
                max_sp=ns_parser.max,
                calls_only=ns_parser.calls,
                puts_only=ns_parser.puts,
                export=ns_parser.export,
            )

    @try_except
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Shows a plot for the given x and y variables",
        )

        parser.add_argument(
            "-p",
            "--put",
            action="store_true",
            default=False,
            dest="put",
            help="Shows puts instead of calls",
        )
        parser.add_argument(
            "-x",
            "--x",
            type=str,
            dest="x",
            default=None,
            choices=["ltd", "s", "lp", "b", "a", "c", "pc", "v", "oi", "iv"],
            help=(
                "ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,"
                "c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility"
            ),
        )
        parser.add_argument(
            "-y",
            "--y",
            type=str,
            dest="y",
            default=None,
            choices=["ltd", "s", "lp", "b", "a", "c", "pc", "v", "oi", "iv"],
            help=(
                "ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,"
                "c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility"
            ),
        )
        parser.add_argument(
            "-c",
            "--custom",
            type=str,
            choices=[
                "smile",
            ],
            dest="custom",
            default=None,
            help="Choose from already created graphs",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required. \n")
            return
        if (ns_parser.x is None or ns_parser.y is None) and ns_parser.custom is None:
            print("Please submit an X and Y value, or select a preset.\n")
            return
        yfinance_view.plot_plot(
            self.ticker,
            self.selected_date,
            ns_parser.put,
            ns_parser.x,
            ns_parser.y,
            ns_parser.custom,
        )
        print("")

    @try_except
    def call_parity(self, other_args: List[str]):
        """Process parity command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="parity",
            description="Shows whether options are over or under valued",
        )
        parser.add_argument(
            "-p",
            "--put",
            action="store_true",
            default=False,
            dest="put",
            help="Shows puts instead of calls",
        )
        parser.add_argument(
            "-a",
            "--ask",
            action="store_true",
            default=False,
            dest="ask",
            help="Use ask price instead of lastPrice",
        )
        parser.add_argument(
            "-m",
            "--min",
            type=float,
            default=None,
            dest="mini",
            help="Minimum strike price shown",
        )
        parser.add_argument(
            "-M",
            "--max",
            type=float,
            default=None,
            dest="maxi",
            help="Maximum strike price shown",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required. \n")
            return
        yfinance_view.show_parity(
            self.ticker,
            self.selected_date,
            ns_parser.put,
            ns_parser.ask,
            ns_parser.mini,
            ns_parser.maxi,
        )
        print("")

    @try_except
    def call_pricing(self, _):
        """Process pricing command"""
        if not self.ticker or not self.selected_date:
            print("Ticker and expiration required.\n")
            return None
        ret = pricing_controller.menu(self.ticker, self.selected_date, self.prices)
        if ret is False:
            self.print_help()
        else:
            return True


def menu(ticker: str = ""):
    """Options Menu."""
    op_controller = OptionsController(ticker)
    op_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in op_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(options)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(options)> ")

        try:
            plt.close("all")

            process_input = op_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
