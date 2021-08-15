"""Options Controller Module."""
__docformat__ = "numpy"
# pylint:disable=too-many-lines


import argparse
import os
from typing import List
import matplotlib.pyplot as plt
from colorama import Style

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options import (
    barchart_view,
    syncretism_view,
    calculator_view,
    yfinance_view,
    yfinance_model,
    tradier_view,
    tradier_model,
    fdscanner_view,
)
from gamestonk_terminal.stocks import stocks_controller

from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.menu import session


class OptionsController:
    """Options Controller class."""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_MENUS = [
        "disp",
        "scr",
        "calc",
        "yf",
        "tr",
        "info",
        "load",
        "exp",
        "vol",
        "voi",
        "oi",
        "hist",
        "chains",
        "grhist",
        "unu",
        "stocks",
    ]

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

        self.op_parser = argparse.ArgumentParser(add_help=False, prog="options")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help."""
        colored = self.ticker and self.selected_date
        help_text = """https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/options

>> OPTIONS <<

What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

"""
        help_text += ">>  stocks        go into stocks context"
        if self.ticker:
            help_text += f" with {self.ticker}"

        help_text += f"""

Explore:
    disp          display all preset screeners filters
    scr           output screener options [Syncretism.io]
    unu           show unusual options activity [fdscanner.com]
    calc          basic call/put PnL calculator

Current Ticker: {self.ticker or None}
Current Expiry: {self.selected_date or None}

    load          load new ticker
    exp           see and set expiration dates
{Style.DIM if not colored else ''}
    info          display option information (volatility, IV rank etc) [Barchart.com]
    chains        display option chains with greeks [Tradier]
    oi            plot open interest [Tradier/YF]
    vol           plot volume [Tradier/YF]
    voi           plot volume and open interest [Tradier/YF]
    hist          plot option history [Tradier]
    grhist        plot option greek history [Syncretism.io]
{Style.RESET_ALL if not colored else ''}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input.

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

        (known_args, other_args) = self.op_parser.parse_known_args(an_input.split())

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
        """Process Help command."""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

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

        try:
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
        except Exception as e:
            print(e, "\n")

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
            "--sortby",
            dest="sortby",
            default="Vol/OI",
            choices=["Option", "Vol/OI", "Vol", "OI", "Bid", "Ask"],
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
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            fdscanner_view.display_options(
                num=ns_parser.num,
                sort_column=ns_parser.sortby,
                export=ns_parser.export,
                ascending=ns_parser.ascend,
            )
        except Exception as e:
            print(e, "\n")

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

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            barchart_view.print_options_data(
                ticker=self.ticker, export=ns_parser.export
            )
        except Exception as e:
            print(e, "\n")

    def call_disp(self, other_args: List[str]):
        """Process disp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="disp",
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
                for preset in os.listdir(self.PRESET_PATH)
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
            syncretism_view.view_available_presets(
                preset=ns_parser.preset, presets_path=self.PRESET_PATH
            )
        except Exception as e:
            print(e, "\n")

    def call_scr(self, other_args: List[str]):
        """Process scr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="scr",
            description="""Sreener filter output from https://ops.syncretism.io/index.html.
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

        try:
            if other_args:
                if "-" not in other_args[0]:
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
        except Exception as e:
            print(e, "\n")

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
            "-n," "--num",
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

        try:
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

        except Exception as e:
            print(e, "\n")

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
        try:
            if other_args:
                if "-t" not in other_args and "-h" not in other_args:
                    other_args.insert(0, "-t")
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            self.ticker = ns_parser.ticker.upper()

        except Exception as e:
            print(e, "\n")
            return

        except SystemExit:
            print("")
            return

        if TRADIER_TOKEN == "REPLACE_ME" or ns_parser.source == "yf":
            self.expiry_dates = yfinance_model.option_expirations(self.ticker)
        else:
            self.expiry_dates = tradier_model.option_expirations(self.ticker)
        print("")

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

        try:
            if other_args:
                if "-" not in other_args[0]:
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
            # It means an expiry date was correctly selected
            else:
                if ns_parser.date:
                    if ns_parser.date in self.expiry_dates:
                        print(f"Expiraration set to {ns_parser.date} \n")
                        self.selected_date = ns_parser.date
                    else:
                        print("Expiration not an option")
                else:
                    expiry_date = self.expiry_dates[ns_parser.index]
                    print(f"Expiraration set to {expiry_date} \n")
                    self.selected_date = expiry_date
        except Exception as e:
            print(e, "\n")

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
            "--chain", dest="chain_id", type=str, help="OCC option symbol"
        )
        parser.add_argument(
            "-r," "--raw",
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

        try:
            if other_args:
                if (
                    "-s" not in other_args or "--strike" not in other_args
                ) and "-h" not in other_args:
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
        except Exception as e:
            print(e, "\n")
        except SystemExit:
            print("")

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
            dest="calls_only",
            help="Flag to show calls only",
        )
        parser.add_argument(
            "-p",
            "--puts",
            action="store_true",
            default=False,
            dest="puts_only",
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
        try:
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
        except Exception as e:
            print(e, "\n")
        except SystemExit:
            print("")

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
        try:
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
        except Exception as e:
            print(e, "\n")

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
        try:
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
        except Exception as e:
            print(e, "\n")
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.")
            return

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
        try:
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
        except Exception as e:
            print(e, "\n")

    def call_stocks(self, _):
        """Process stocks command"""
        return stocks_controller.menu(self.ticker)


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
                f"{get_flair()} (options)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (options)> ")

        try:
            plt.close("all")

            process_input = op_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
