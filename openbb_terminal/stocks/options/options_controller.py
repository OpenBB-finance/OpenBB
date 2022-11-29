""" Options Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime, timedelta
from typing import Any, List

import pandas as pd

from openbb_terminal import feature_flags as obbff
from openbb_terminal.config_terminal import API_TRADIER_TOKEN
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_and_split_input,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console, get_ordered_list_sources
from openbb_terminal.stocks.options import (
    alphaquery_view,
    barchart_view,
    calculator_view,
    chartexchange_view,
    fdscanner_view,
    nasdaq_model,
    nasdaq_view,
    op_helpers,
    tradier_model,
    tradier_view,
    yfinance_model,
    yfinance_view,
)
from openbb_terminal.stocks.options.hedge import hedge_controller
from openbb_terminal.stocks.options.pricing import pricing_controller
from openbb_terminal.stocks.options.screen import (
    screener_controller,
    syncretism_model,
    syncretism_view,
)

# pylint: disable=R1710,C0302,R0916

# TODO: HELP WANTED! This controller requires some MVC style refactoring
#       - At the moment there's too much logic in the controller to implement an
#         API wrapper. Please refactor functions like 'call_exp'

# TODO: Additional refactoring -- load should bring in a df from the sdk_helpers functions and we can get expirations
# from there.  Additionally each view function should be made a function that takes the df and plots it instead of
# getting the new chain

logger = logging.getLogger(__name__)


class OptionsController(BaseController):
    """Options Controller class"""

    CHOICES_COMMANDS = [
        "calc",
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
        "binom",
        "vsurf",
        "greeks",
    ]
    CHOICES_MENUS = [
        "pricing",
        "screen",
        "hedge",
    ]

    preset_choices = syncretism_model.get_preset_choices()

    grhist_greeks_choices = [
        "iv",
        "gamma",
        "theta",
        "vega",
        "delta",
        "rho",
        "premium",
    ]

    unu_sortby_choices = [
        "Strike",
        "Vol/OI",
        "Vol",
        "OI",
        "Bid",
        "Ask",
        "Exp",
        "Ticker",
    ]
    pcr_length_choices = ["10", "20", "30", "60", "90", "120", "150", "180"]

    plot_vars_choices = ["ltd", "s", "lp", "b", "a", "c", "pc", "v", "oi", "iv"]
    plot_custom_choices = ["smile"]
    PATH = "/stocks/options/"
    CHOICES_GENERATION = True

    def __init__(self, ticker: str, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.prices = pd.DataFrame(columns=["Price", "Chance"])
        self.selected_date = ""
        self.chain: Any = None
        # Keeps track of initial source of load so we can use correct commands later
        self.source = ""

        if ticker:
            if API_TRADIER_TOKEN == "REPLACE_ME":  # nosec
                console.print("Loaded expiry dates from Yahoo Finance\n")
                self.expiry_dates = yfinance_model.option_expirations(self.ticker)
            else:
                console.print("Loaded expiry dates from Tradier\n")
                self.expiry_dates = tradier_model.option_expirations(self.ticker)
        else:
            self.expiry_dates = []

        self.default_chain = get_ordered_list_sources(f"{self.PATH}chains")[0]

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            # This menu contains dynamic choices that may change during runtime
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        # Filtering out sorting parameters with forward slashes like P/E
        sort_filter = r"((\ -s |\ --sortby ).*?(Vol\/OI)*)"

        custom_filters = [sort_filter]

        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def update_runtime_choices(self):
        """Update runtime choices"""
        if self.expiry_dates and session and obbff.USE_PROMPT_TOOLKIT:
            self.choices["exp"] = {str(c): {} for c in range(len(self.expiry_dates))}
            self.choices["exp"]["--date"] = {c: {} for c in self.expiry_dates + [""]}
            self.choices["exp"]["-d"] = "--date"
            self.choices["exp"]["--source"] = {
                c: {} for c in get_ordered_list_sources(f"{self.PATH}exp")
            }

            if isinstance(self.chain, pd.DataFrame):
                return
            if self.chain and self.source != "Nasdaq":

                self.choices["hist"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }
                self.choices["hist"]["--put"] = {}
                self.choices["hist"]["-p"] = "--put"
                self.choices["hist"]["--chain"] = None
                self.choices["hist"]["-c"] = "--chain"
                self.choices["hist"]["--raw"] = {}
                self.choices["hist"]["--limit"] = None
                self.choices["hist"]["-l"] = "--limit"
                self.choices["grhist"]["--strike"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }
                self.choices["grhist"]["-s"] = "--strike"
                self.choices["binom"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }
                self.choices["binom"]["--put"] = {}
                self.choices["binom"]["-p"] = "--put"
                self.choices["binom"]["--european"] = {}
                self.choices["binom"]["-e"] = "--european"
                self.choices["binom"]["--xlsx"] = {}
                self.choices["binom"]["-x"] = "--xlsx"
                self.choices["binom"]["--plot"] = {}
                self.choices["binom"]["--volatility"] = None
                self.choices["binom"]["-v"] = "--volatility"

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("stocks/options/")
        mt.add_cmd("unu")
        mt.add_cmd("calc")
        mt.add_raw("\n")
        mt.add_menu("screen")
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_cmd("exp", self.ticker)
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker or "")
        mt.add_param("_expiry", self.selected_date or "")
        mt.add_raw("\n")
        mt.add_cmd("pcr", self.ticker and self.selected_date)
        mt.add_cmd("info", self.ticker and self.selected_date)
        mt.add_cmd("chains", self.ticker and self.selected_date)
        mt.add_cmd("oi", self.ticker and self.selected_date)
        mt.add_cmd("vol", self.ticker and self.selected_date)
        mt.add_cmd("voi", self.ticker and self.selected_date)
        mt.add_cmd("hist", self.ticker and self.selected_date)
        mt.add_cmd("vsurf", self.ticker and self.selected_date)
        mt.add_cmd("grhist", self.ticker and self.selected_date)
        mt.add_cmd("plot", self.ticker and self.selected_date)
        mt.add_cmd("parity", self.ticker and self.selected_date)
        mt.add_cmd("binom", self.ticker and self.selected_date)
        mt.add_cmd("greeks", self.ticker and self.selected_date)
        mt.add_raw("\n")
        mt.add_menu("pricing", self.ticker and self.selected_date)
        mt.add_menu("hedge", self.ticker and self.selected_date)
        console.print(text=mt.menu_text, menu="Stocks - Options")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.selected_date:
                return [
                    "stocks",
                    f"load {self.ticker}",
                    "options",
                    f"exp -d {self.selected_date}",
                ]
            return ["stocks", f"load {self.ticker}", "options"]
        return []

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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

    @log_start_end(log=logger)
    def call_unu(self, other_args: List[str]):
        """Process unu command"""
        parser = argparse.ArgumentParser(
            prog="unu",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="This command gets unusual options from fdscanner.com",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            default=20,
            help="Limit of options to show. Each scraped page gives 20 results.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            nargs="+",
            default="Vol/OI",
            choices=self.unu_sortby_choices,
            help="Column to sort by.  Vol/OI is the default and typical variable to be considered unusual.",
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.calls_only and ns_parser.puts_only:
                console.print(
                    "Cannot return puts only and calls only. Either use one or neither\n."
                )
            else:
                fdscanner_view.display_options(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    export=ns_parser.export,
                    ascend=ns_parser.reverse,
                    calls_only=ns_parser.calls_only,
                    puts_only=ns_parser.puts_only,
                )

    @log_start_end(log=logger)
    def call_pcr(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pcr",
            description="Display put to call ratio for ticker [AlphaQuery.com]",
        )
        parser.add_argument(
            "-l",
            "--length",
            help="Window length to get",
            dest="length",
            choices=self.pcr_length_choices,
            default=30,
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start date for plot",
            type=valid_date,
            default=datetime.now() - timedelta(days=366),
            dest="start",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                alphaquery_view.display_put_call_ratio(
                    symbol=self.ticker,
                    window=ns_parser.length,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded.\n")

    @log_start_end(log=logger)
    def call_info(self, other_args: List[str]):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Display option data [Source: Barchart.com]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                barchart_view.print_options_data(
                    symbol=self.ticker, export=ns_parser.export
                )
            else:
                console.print("No ticker loaded.\n")

    @log_start_end(log=logger)
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
            "-p",
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
            choices=self.grhist_greeks_choices,
            default="delta",
            help="Greek column to select",
        )
        parser.add_argument(
            "-c",
            "--chain",
            dest="chain_id",
            default="",
            type=str,
            help="OCC option symbol",
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
            "-l",
            "--limit",
            dest="limit",
            default=20,
            type=int,
            help="Limit of raw data rows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if self.chain and (
                        (
                            ns_parser.put
                            and ns_parser.strike
                            in [float(strike) for strike in self.chain.puts["strike"]]
                        )
                        or (
                            not ns_parser.put
                            and ns_parser.strike
                            in [float(strike) for strike in self.chain.calls["strike"]]
                        )
                    ):
                        syncretism_view.view_historical_greeks(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            strike=ns_parser.strike,
                            greek=ns_parser.greek,
                            chain_id=ns_parser.chain_id,
                            put=ns_parser.put,
                            raw=ns_parser.raw,
                            limit=ns_parser.limit,
                            export=ns_parser.export,
                        )
                    else:
                        console.print("No correct strike input\n")
                else:
                    console.print("No expiry loaded. First use `exp <expiry date>`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>` \n")

    @log_start_end(log=logger)
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
        )
        if ns_parser:
            self.ticker = ns_parser.ticker.upper()
            self.update_runtime_choices()

            self.source = ns_parser.source
            if ns_parser.source == "YahooFinance":
                self.expiry_dates = yfinance_model.option_expirations(self.ticker)
            elif ns_parser.source == "Nasdaq":
                self.expiry_dates = nasdaq_model.get_expirations(self.ticker)
            else:
                self.expiry_dates = tradier_model.option_expirations(self.ticker)

            if self.ticker and self.selected_date:
                try:
                    self.chain = yfinance_model.get_option_chain(
                        self.ticker, self.selected_date
                    )
                except ValueError:
                    console.print(
                        f"[red]{self.ticker} does not have expiration"
                        f" {self.selected_date}.[/red]"
                    )

    @log_start_end(log=logger)
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

        if other_args and "-" not in other_args[0][0]:
            first_int = int(other_args[0].split("-")[0])
            if first_int > 2000:
                other_args.insert(0, "-d")
            else:
                other_args.insert(0, "-i")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                # Print possible expiry dates
                if ns_parser.index == -1 and not ns_parser.date:
                    tradier_view.display_expiry_dates(self.expiry_dates)
                elif ns_parser.date:
                    if ns_parser.date in self.expiry_dates:
                        console.print(f"Expiration set to {ns_parser.date} \n")
                        self.selected_date = ns_parser.date
                        self.update_runtime_choices()
                    else:
                        console.print("Expiration not an option")
                else:
                    expiry_date = self.expiry_dates[ns_parser.index]
                    console.print(f"Expiration set to {expiry_date} \n")
                    self.selected_date = expiry_date
                    self.update_runtime_choices()

                if self.selected_date:
                    if self.source == "Tradier":
                        df = tradier_model.get_option_chains(
                            self.ticker, self.selected_date
                        )
                        self.chain = op_helpers.Chain(df)
                    elif self.source == "Nasdaq":
                        df = nasdaq_model.get_chain_given_expiration(
                            self.ticker, self.selected_date
                        )
                        self.chain = op_helpers.Chain(df, self.source)
                    else:
                        self.chain = yfinance_model.get_option_chain(
                            self.ticker, self.selected_date
                        )
                    self.update_runtime_choices()
            else:
                console.print("Please load a ticker using `load <ticker>`.\n")

    @log_start_end(log=logger)
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
            required="--chain" not in other_args
            and "-c" not in other_args
            and "-h" not in other_args,
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
            "-c", "--chain", dest="chain_id", type=str, help="OCC option symbol"
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            if not self.ticker:
                console.print("No ticker loaded. First use `load <ticker>`\n")
                return
            if not self.selected_date:
                console.print("No expiry loaded. First use `exp <expiry date>` \n")
                return
            if self.chain and (
                (
                    ns_parser.put
                    and ns_parser.strike
                    not in [float(strike) for strike in self.chain.puts["strike"]]
                )
                or (
                    not ns_parser.put
                    and ns_parser.strike
                    not in [float(strike) for strike in self.chain.calls["strike"]]
                )
            ):
                console.print("No correct strike input\n")
                return
            if ns_parser.source == "ChartExchange":
                chartexchange_view.display_raw(
                    self.ticker,
                    self.selected_date,
                    not ns_parser.put,
                    ns_parser.strike,
                    ns_parser.limit,
                    ns_parser.export,
                )

            elif (
                ns_parser.source == "Tradier" and API_TRADIER_TOKEN != "REPLACE_ME"
            ):  # nosec
                tradier_view.display_historical(
                    symbol=self.ticker,
                    expiry=self.selected_date,
                    strike=ns_parser.strike,
                    put=ns_parser.put,
                    raw=ns_parser.raw,
                    chain_id=ns_parser.chain_id,
                    export=ns_parser.export,
                )
            else:
                console.print("TRADIER TOKEN not supplied. \n")

    @log_start_end(log=logger)
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
            help="(tradier only) Columns to look at.  Columns can be: bid, ask, strike, bidsize, asksize, "
            "volume, open_interest, delta, gamma, theta, vega, ask_iv, bid_iv, mid_iv. E.g. 'bid,ask,strike' ",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if ns_parser.source == "Tradier" or self.source == "Tradier":
                        if API_TRADIER_TOKEN != "REPLACE_ME":  # nosec
                            tradier_view.display_chains(
                                symbol=self.ticker,
                                expiry=self.selected_date,
                                to_display=ns_parser.to_display,
                                min_sp=ns_parser.min_sp,
                                max_sp=ns_parser.max_sp,
                                calls_only=ns_parser.calls,
                                puts_only=ns_parser.puts,
                                export=ns_parser.export,
                            )
                        else:
                            console.print("TRADIER TOKEN not supplied. \n")
                    elif ns_parser.source == "YahooFinance":
                        yfinance_view.display_chains(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min_sp,
                            max_sp=ns_parser.max_sp,
                            calls_only=ns_parser.calls,
                            puts_only=ns_parser.puts,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "Nasdaq":
                        nasdaq_view.display_chains(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            export=ns_parser.export,
                        )
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_vol(self, other_args: List[str]):
        """Process vol command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vol",
            description="Plot volume. Volume refers to the number of contracts traded today.",
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
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if (
                        ns_parser.source == "Tradier"
                        and API_TRADIER_TOKEN != "REPLACE_ME"  # nosec
                    ) or self.source == "Tradier":
                        tradier_view.plot_vol(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            calls_only=ns_parser.calls,
                            puts_only=ns_parser.puts,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "YahooFinance":
                        yfinance_view.plot_vol(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            calls_only=ns_parser.calls,
                            puts_only=ns_parser.puts,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "Nasdaq":
                        nasdaq_view.display_volume(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            export=ns_parser.export,
                            raw=ns_parser.raw,
                        )
                    else:
                        return
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_voi(self, other_args: List[str]):
        """Process voi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="voi",
            description="""Plots Volume + Open Interest of calls vs puts.""",
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if (
                        ns_parser.source == "Tradier"
                        and API_TRADIER_TOKEN != "REPLACE_ME"  # nosec
                    ) or self.source == "Tradier":
                        tradier_view.plot_volume_open_interest(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min_sp,
                            max_sp=ns_parser.max_sp,
                            min_vol=ns_parser.min_vol,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "YahooFinance":
                        yfinance_view.plot_volume_open_interest(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min_sp,
                            max_sp=ns_parser.max_sp,
                            min_vol=ns_parser.min_vol,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "Nasdaq":
                        nasdaq_view.display_volume_and_oi(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min_sp,
                            max_sp=ns_parser.max_sp,
                            raw=ns_parser.raw,
                            export=ns_parser.export,
                        )
                    else:
                        pass
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_oi(self, other_args: List[str]):
        """Process oi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oi",
            description="""Plot open interest. Open interest represents the number of
            contracts that exist.""",
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
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            raw=True,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if (
                        ns_parser.source == "Tradier"
                        and API_TRADIER_TOKEN != "REPLACE_ME"  # nosec
                    ) or self.source == "Tradier":
                        tradier_view.plot_oi(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            calls_only=ns_parser.calls,
                            puts_only=ns_parser.puts,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "YahooFinance":
                        yfinance_view.plot_oi(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            calls_only=ns_parser.calls,
                            puts_only=ns_parser.puts,
                            export=ns_parser.export,
                        )
                    elif ns_parser.source == "Nasdaq":
                        nasdaq_view.display_oi(
                            self.ticker,
                            expiry=self.selected_date,
                            min_sp=ns_parser.min,
                            max_sp=ns_parser.max,
                            export=ns_parser.export,
                            raw=ns_parser.raw,
                        )
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
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
            "--x_axis",
            type=str,
            dest="x",
            default="s",
            choices=self.plot_vars_choices,
            help=(
                "ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,"
                "c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility"
            ),
        )
        parser.add_argument(
            "-y",
            "--y_axis",
            type=str,
            dest="y",
            default="iv",
            choices=self.plot_vars_choices,
            help=(
                "ltd- last trade date, s- strike, lp- last price, b- bid, a- ask,"
                "c- change, pc- percent change, v- volume, oi- open interest, iv- implied volatility"
            ),
        )
        parser.add_argument(
            "-c",
            "--custom",
            type=str,
            choices=self.plot_custom_choices,
            dest="custom",
            default=None,
            help="Choose from already created graphs",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if (
                        ns_parser.x is None or ns_parser.y is None
                    ) and ns_parser.custom is None:
                        console.print(
                            "Please submit an X and Y value, or select a preset.\n"
                        )
                    else:
                        yfinance_view.plot_plot(
                            symbol=self.ticker,
                            expiry=self.selected_date,
                            put=ns_parser.put,
                            x=ns_parser.x,
                            y=ns_parser.y,
                            custom=ns_parser.custom,
                            export=ns_parser.export,
                        )
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_vsurf(self, other_args: List[str]):
        """Process vsurf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vsurf",
            description="Plot 3D volatility surface.",
        )
        parser.add_argument(
            "-z",
            "--z-axis",
            default="IV",
            dest="z",
            choices=["IV", "OI", "LP"],
            type=str,
            help="The data for the Z axis",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            yfinance_view.display_vol_surface(
                self.ticker, export=ns_parser.export, z=ns_parser.z
            )

    @log_start_end(log=logger)
    def call_greeks(self, other_args: List[str]):
        """Process greeks command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="greeks",
            description="The greeks for a given option.",
        )
        parser.add_argument(
            "-d",
            "--div",
            dest="dividend",
            type=float,
            default=0,
            help="The dividend continuous rate",
        )
        parser.add_argument(
            "-r",
            "--risk-free",
            dest="risk_free",
            default=None,
            type=float,
            help="The risk free rate",
        )
        parser.add_argument(
            "-p",
            "--put",
            dest="put",
            action="store_true",
            default=False,
            help="Whether the option is a put.",
        )
        parser.add_argument(
            "-m",
            "--min",
            dest="min",
            type=float,
            default=None,
            help="Minimum strike price to show.",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max",
            type=float,
            default=None,
            help="Maximum strike price to show.",
        )
        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            default=False,
            help="Whether to show all greeks.",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if not self.ticker:
                console.print("No ticker loaded. First use `load <ticker>`\n")
            elif not self.selected_date:
                console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                opt_type = -1 if ns_parser.put else 1
                yfinance_view.show_greeks(
                    symbol=self.ticker,
                    div_cont=ns_parser.dividend,
                    expiry=self.selected_date,
                    rf=ns_parser.risk_free,
                    opt_type=opt_type,
                    mini=ns_parser.min,
                    maxi=ns_parser.max,
                    show_all=ns_parser.all,
                )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    yfinance_view.show_parity(
                        self.ticker,
                        self.selected_date,
                        ns_parser.put,
                        ns_parser.ask,
                        ns_parser.mini,
                        ns_parser.maxi,
                        ns_parser.export,
                    )
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_binom(self, other_args: List[str]):
        """Process binom command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="binom",
            description="Gives the option value using binomial option valuation",
        )
        parser.add_argument(
            "-s",
            "--strike",
            type=float,
            default=0,
            dest="strike",
            help="Strike price for option shown",
        )
        parser.add_argument(
            "-p",
            "--put",
            action="store_true",
            default=False,
            dest="put",
            help="Value a put instead of a call",
        )
        parser.add_argument(
            "-e",
            "--european",
            action="store_true",
            default=False,
            dest="europe",
            help="Value a European option instead of an American one",
        )
        parser.add_argument(
            "-x",
            "--xlsx",
            action="store_true",
            default=False,
            dest="export",
            help="Export an excel spreadsheet with binomial pricing data",
        )
        parser.add_argument(
            "--plot",
            action="store_true",
            default=False,
            dest="plot",
            help="Plot expected ending values",
        )
        parser.add_argument(
            "-v",
            "--volatility",
            type=float,
            default=None,
            dest="volatility",
            help="Underlying asset annualized volatility.  Historical volatility used if not supplied.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    yfinance_view.show_binom(
                        self.ticker,
                        self.selected_date,
                        ns_parser.strike,
                        ns_parser.put,
                        ns_parser.europe,
                        ns_parser.export,
                        ns_parser.plot,
                        ns_parser.volatility,
                    )
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_pricing(self, _):
        """Process pricing command"""
        if self.ticker:
            if self.selected_date:
                self.queue = self.load_class(
                    pricing_controller.PricingController,
                    self.ticker,
                    self.selected_date,
                    self.prices,
                    self.queue,
                )
            else:
                console.print("No expiry loaded. First use `exp {expiry date}`\n")

        else:
            console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_hedge(self, _):
        """Process hedge command"""
        if self.ticker:
            if self.selected_date:
                self.queue = self.load_class(
                    hedge_controller.HedgeController,
                    self.ticker,
                    self.selected_date,
                    self.queue,
                )
            else:
                console.print("No expiry loaded. First use `exp {expiry date}`\n")

        else:
            console.print("No ticker loaded. First use `load <ticker>`\n")

    @log_start_end(log=logger)
    def call_screen(self, _):
        """Process screen command"""
        self.queue = screener_controller.ScreenerController(self.queue).menu()
