""" Options Controller Module """
__docformat__ = "numpy"

import argparse
import os
from datetime import datetime, timedelta
from typing import List
from colorama import Style
import pandas as pd

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    valid_date,
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
    screener_controller,
)

# pylint: disable=R1710,C0302,R0916


class OptionsController(BaseController):
    """Options Controller class"""

    CHOICES_COMMANDS = [
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
        "binom",
        "vsurf",
    ]
    CHOICES_MENUS = [
        "payoff",
        "pricing",
        "screen",
    ]

    PRESET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

    presets = [f.split(".")[0] for f in os.listdir(PRESET_PATH) if f.endswith(".ini")]

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

    load_source_choices = ["tr", "yf"]
    hist_source_choices = ["td", "ce"]
    voi_source_choices = ["tr", "yf"]
    oi_source_choices = ["tr", "yf"]
    plot_vars_choices = ["ltd", "s", "lp", "b", "a", "c", "pc", "v", "oi", "iv"]
    plot_custom_choices = ["smile"]

    def __init__(self, ticker: str, queue: List[str] = None):
        """Constructor"""
        super().__init__("/stocks/options/", queue)

        self.ticker = ticker
        self.prices = pd.DataFrame(columns=["Price", "Chance"])
        self.selected_date = ""
        self.chain = None

        if ticker:
            if TRADIER_TOKEN == "REPLACE_ME":
                print("Loaded expiry dates from Yahoo Finance")
                self.expiry_dates = yfinance_model.option_expirations(self.ticker)
            else:
                print("Loaded expiry dates from Tradier")
                self.expiry_dates = tradier_model.option_expirations(self.ticker)
        else:
            self.expiry_dates = []

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["unu"]["-s"] = {c: {} for c in self.unu_sortby_choices}
            choices["pcr"] = {c: {} for c in self.pcr_length_choices}
            choices["disp"] = {c: {} for c in self.presets}
            choices["scr"] = {c: {} for c in self.presets}
            choices["grhist"]["-g"] = {c: {} for c in self.grhist_greeks_choices}
            choices["load"]["-s"] = {c: {} for c in self.load_source_choices}
            choices["load"]["--source"] = {c: {} for c in self.hist_source_choices}
            choices["load"]["-s"] = {c: {} for c in self.voi_source_choices}
            choices["plot"]["-x"] = {c: {} for c in self.plot_vars_choices}
            choices["plot"]["-y"] = {c: {} for c in self.plot_vars_choices}
            choices["plot"]["-c"] = {c: {} for c in self.plot_custom_choices}
            # This menu contains dynamic choices that may change during runtime
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        """Update runtime choices"""
        if self.expiry_dates and session and gtff.USE_PROMPT_TOOLKIT:
            self.choices["exp"] = {str(c): {} for c in range(len(self.expiry_dates))}
            self.choices["exp"]["-d"] = {c: {} for c in self.expiry_dates + [""]}
            if self.chain:
                self.choices["hist"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }
                self.choices["grhist"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }
                self.choices["binom"] = {
                    str(c): {}
                    for c in self.chain.puts["strike"] + self.chain.calls["strike"]
                }

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help."""
        colored = self.ticker and self.selected_date
        help_text = f"""
    unu           show unusual options activity [fdscanner.com]
    calc          basic call/put PnL calculator

    load          load new ticker
    exp           see and set expiration dates

Ticker: {self.ticker or None}
Expiry: {self.selected_date or None}
{"" if self.ticker else Style.DIM}
    pcr           display put call ratio for ticker [AlphaQuery.com]{Style.DIM if not colored else ''}
    info          display option information (volatility, IV rank etc) [Barchart.com]
    chains        display option chains with greeks [Tradier]
    oi            plot open interest [Tradier/YF]
    vol           plot volume [Tradier/YF]
    voi           plot volume and open interest [Tradier/YF]
    hist          plot option history [Tradier]
    vsurf         show 3D volatility surface [Yfinance]
    grhist        plot option greek history [Syncretism.io]
    plot          plot variables provided by the user [Yfinance]
    parity        shows whether options are above or below expected price [Yfinance]
    binom         shows the value of an option using binomial options pricing [Yfinance]
{Style.RESET_ALL if not colored else ''}
>   screen        screens tickers based on preset [Syncretism.io]{"" if colored else Style.DIM}
>   payoff        shows payoff diagram for a selection of options [Yfinance]
>   pricing       shows options pricing and risk neutral valuation [Yfinance]
{Style.RESET_ALL if not colored else ''}"""
        print(help_text)

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

    def call_unu(self, other_args: List[str]):
        """Process act command"""
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.calls_only and ns_parser.puts_only:
                print(
                    "Cannot return puts only and calls only. Either use one or neither\n."
                )
            else:
                fdscanner_view.display_options(
                    num=ns_parser.limit,
                    sort_column=ns_parser.sortby,
                    export=ns_parser.export,
                    ascending=ns_parser.ascend,
                    calls_only=ns_parser.calls_only,
                    puts_only=ns_parser.puts_only,
                )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                alphaquery_view.display_put_call_ratio(
                    ticker=self.ticker,
                    window=ns_parser.length,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    export=ns_parser.export,
                )
            else:
                print("No ticker loaded.\n")

    def call_info(self, other_args: List[str]):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Display option data [Source: Barchart.com]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                barchart_view.print_options_data(
                    ticker=self.ticker, export=ns_parser.export
                )
            else:
                print("No ticker loaded.\n")

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
            help="Limit of raw data rows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(
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
                            ticker=self.ticker,
                            expiry=self.selected_date,
                            strike=ns_parser.strike,
                            greek=ns_parser.greek,
                            chain_id=ns_parser.chain_id,
                            put=ns_parser.put,
                            raw=ns_parser.raw,
                            n_show=ns_parser.limit,
                            export=ns_parser.export,
                        )
                    else:
                        print("No correct strike input\n")
                else:
                    print("No expiry loaded. First use `exp <expiry date>`\n")
            else:
                print("No ticker loaded. First use `load <ticker>` \n")

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
            "-s",
            "--source",
            choices=self.load_source_choices,
            dest="source",
            default=None,
            help="Source to get option expirations from",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.ticker = ns_parser.ticker.upper()
            self.update_runtime_choices()

            if TRADIER_TOKEN == "REPLACE_ME" or ns_parser.source == "yf":
                self.expiry_dates = yfinance_model.option_expirations(self.ticker)
            else:
                self.expiry_dates = tradier_model.option_expirations(self.ticker)
            print("")

            if self.ticker and self.selected_date:
                self.chain = yfinance_model.get_option_chain(
                    self.ticker, self.selected_date
                )

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
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
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
                        self.update_runtime_choices()
                    else:
                        print("Expiration not an option")
                else:
                    expiry_date = self.expiry_dates[ns_parser.index]
                    print(f"Expiration set to {expiry_date} \n")
                    self.selected_date = expiry_date
                    self.update_runtime_choices()

                if self.selected_date:
                    self.chain = yfinance_model.get_option_chain(
                        self.ticker, self.selected_date
                    )
                    self.update_runtime_choices()
            else:
                print("Please load a ticker using `load <ticker>`.\n")

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
            required="--chain" not in other_args and "-c" not in other_args,
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
        parser.add_argument(
            "-r",
            "--raw",
            dest="raw",
            action="store_true",
            default=False,
            help="Display raw data",
        )
        parser.add_argument(
            "--source",
            dest="source",
            type=str,
            choices=self.hist_source_choices,
            default="ce",
            help="Choose Tradier(TD) or ChartExchange (CE), only affects raw data",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="Limit of data rows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(
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
                        if ns_parser.source.lower() == "ce":
                            chartexchange_view.display_raw(
                                self.ticker,
                                self.selected_date,
                                not ns_parser.put,
                                ns_parser.strike,
                                ns_parser.limit,
                                ns_parser.export,
                            )

                        else:
                            if TRADIER_TOKEN != "REPLACE_ME":
                                tradier_view.display_historical(
                                    ticker=self.ticker,
                                    expiry=self.selected_date,
                                    strike=ns_parser.strike,
                                    put=ns_parser.put,
                                    raw=ns_parser.raw,
                                    chain_id=ns_parser.chain_id,
                                    export=ns_parser.export,
                                )
                            else:
                                print("TRADIER TOKEN not supplied. \n")
                    else:
                        print("No correct strike input\n")
                else:
                    print("No expiry loaded. First use `exp <expiry date>` \n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if TRADIER_TOKEN != "REPLACE_ME":
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
                    else:
                        print("TRADIER TOKEN not supplied. \n")
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
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
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="tr",
            choices=self.voi_source_choices,
            dest="source",
            help="Source to get data from",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
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
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
            choices=self.oi_source_choices,
            dest="source",
            help="Source to get data from",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
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
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
            default=None,
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
            default=None,
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if (
                        ns_parser.x is None or ns_parser.y is None
                    ) and ns_parser.custom is None:
                        print("Please submit an X and Y value, or select a preset.\n")
                    else:
                        yfinance_view.plot_plot(
                            self.ticker,
                            self.selected_date,
                            ns_parser.put,
                            ns_parser.x,
                            ns_parser.y,
                            ns_parser.custom,
                            ns_parser.export,
                        )
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

    def call_vsurf(self, other_args: List[str]):
        """Process vol command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vsurf",
            description="Plot 3D volatility surface.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            yfinance_view.display_vol_surface(self.ticker, export=ns_parser.export)

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
        ns_parser = parse_known_args_and_warn(
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
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

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
            help="Underlying asset annualized volatility",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")

    def call_payoff(self, _):
        """Process payoff command"""
        if self.ticker:
            if self.selected_date:
                self.queue = payoff_controller.PayoffController(
                    self.ticker, self.selected_date, self.queue
                ).menu()
            else:
                print("No expiry loaded. First use `exp {expiry date}`\n")

        else:
            print("No ticker loaded. First use `load <ticker>`\n")

    def call_pricing(self, _):
        """Process pricing command"""
        if self.ticker:
            if self.selected_date:
                self.queue = pricing_controller.PricingController(
                    self.ticker, self.selected_date, self.prices, self.queue
                ).menu()
            else:
                print("No expiry loaded. First use `exp {expiry date}`\n")

        else:
            print("No ticker loaded. First use `load <ticker>`\n")

    def call_screen(self, _):
        """Process screen command"""
        self.queue = screener_controller.ScreenerController(self.queue).menu()
