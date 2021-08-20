"""Exploratory Data Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.common.quantitative_analysis import (
    qa_view,
    rolling_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    check_positive,
    check_proportion_range,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session


class QaController:
    """Quantitative Analysis Controller class"""

    # Command choices
    CHOICES = ["?", "cls", "help", "q", "quit"]

    CHOICES_COMMANDS = [
        "summary",
        "hist",
        "cdf",
        "bw",
        "rolling",
        "decompose",
        "cusum",
        "acf",
        "spread",
        "quantile",
        "skew",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor"""
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.qa_parser = argparse.ArgumentParser(add_help=False, prog="qa")
        self.qa_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            stock_str = f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
        else:
            stock_str = f"\n{s_intraday} Stock: {self.ticker}"

        help_str = f"""https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks/quantitative_analysis
{stock_str}

Quantitative Analysis:
    cls         clear screen
    help        show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon program

    summary       brief summary statistics
    hist          histogram with density plot
    cdf           cumulative distribution function
    bw           box and whisker plot

Rolling Metrics:
    rolling       rolling mean and std deviation
    spread        variance and std deviation
    quantile      median and quantile
    skew          skewness of distribution

    decompose     decomposition in cyclic-trend, season, and residuals
    cusum         detects abrupt changes using cumulative sum algorithm
    acf           (partial) auto-correlation function differentials
        """
        print(help_str)

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

        (known_args, other_args) = self.qa_parser.parse_known_args(an_input.split())

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

    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="summary",
            description="""
                Summary statistics
            """,
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            qa_view.view_summary(df_stock=self.stock, export=ns_parser.export)

        except Exception as e:
            print(e, "\n")

    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="hist",
            description="""
                Histogram (default returns) with depicted density and rug
            """,
        )
        parser.add_argument(
            "-p",
            "--prices",
            action="store_true",
            help="Flag to show prices not returns",
            default=False,
            dest="prices",
        )
        parser.add_argument(
            "-b", "--bins", type=check_positive, default=15, dest="n_bins"
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            qa_view.show_hist(
                s_ticker=self.ticker,
                df_stock=self.stock,
                start=self.start,
                prices=ns_parser.prices,
                bins=ns_parser.n_bins,
            )

        except Exception as e:
            print(e, "\n")

    def call_cdf(self, other_args: List[str]):
        """Process cdf command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="cdf",
            description="""
                Cumulative distribution function
            """,
        )
        parser.add_argument(
            "-p",
            "--prices",
            action="store_true",
            help="Flag to show prices not returns",
            default=False,
            dest="prices",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            qa_view.show_cdf(
                s_ticker=self.ticker,
                df_stock=self.stock,
                start=self.start,
                prices=ns_parser.prices,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_bw(self, other_args: List[str]):
        """Process bwy command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="bw",
            description="""
                Box and Whisker plot
            """,
        )
        parser.add_argument(
            "-y",
            "--yearly",
            action="store_true",
            default=False,
            dest="year",
            help="Flag to show yearly bw plot",
        )
        parser.add_argument(
            "-p",
            "--prices",
            action="store_true",
            default=False,
            dest="prices",
            help="Flag to show prices on plot",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            qa_view.show_bw(
                s_ticker=self.ticker,
                start=self.start,
                df_stock=self.stock,
                yearly=ns_parser.year,
                prices=ns_parser.prices,
            )

        except Exception as e:
            print(e, "\n")

    def call_decompose(self, other_args: List[str]):
        """Process decompose command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="decompose",
            description="""
                Decompose time series as:
                - Additive Time Series = Level + CyclicTrend + Residual + Seasonality
                - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality
            """,
        )
        parser.add_argument(
            "-m",
            "--multiplicative",
            action="store_true",
            default=False,
            dest="multiplicative",
            help="decompose using multiplicative model instead of additive",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            qa_view.show_seasonal(
                s_ticker=self.ticker,
                df_stock=self.stock,
                multiplicative=ns_parser.multiplicative,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

    def call_cusum(self, other_args: List[str]):
        """Process cusum command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="cusum",
            description="""
                Cumulative sum algorithm (CUSUM) to detect abrupt changes in data
            """,
        )
        parser.add_argument(
            "-t",
            "--threshold",
            dest="threshold",
            type=float,
            default=(
                max(self.stock["Adj Close"].values)
                - min(self.stock["Adj Close"].values)
            )
            / 40,
            help="threshold",
        )
        parser.add_argument(
            "-d",
            "--drift",
            dest="drift",
            type=float,
            default=(
                max(self.stock["Adj Close"].values)
                - min(self.stock["Adj Close"].values)
            )
            / 80,
            help="drift",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            qa_view.show_cusum(
                df_stock=self.stock,
                threshold=ns_parser.threshold,
                drift=ns_parser.drift,
            )
        except Exception as e:
            print(e, "\n")

    def call_acf(self, other_args: List[str]):
        """Process acf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="acf",
            description="""
                Auto-Correlation and Partial Auto-Correlation Functions for diff and diff diff stock data
            """,
        )
        parser.add_argument(
            "-l",
            "--lags",
            dest="lags",
            type=check_positive,
            default=15,
            help="maximum lags to display in plots",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            qa_view.show_acf(
                s_ticker=self.ticker,
                start=self.start,
                df_stock=self.stock,
                lags=ns_parser.lags,
            )

        except Exception as e:
            print(e, "\n")

    def call_rolling(self, other_args: List[str]):
        """Process rolling command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rolling",
            description="""
                Rolling mean and std deviation
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="Window length",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            rolling_view.view_mean_std(
                s_ticker=self.ticker,
                df_stock=self.stock,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_spread(self, other_args: List[str]):
        """Process spread command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spread",
            description="""

            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="Window length",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            rolling_view.view_spread(
                s_ticker=self.ticker,
                s_interval=self.interval,
                df_stock=self.stock,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

    def call_quantile(self, other_args: List[str]):
        """Process quantile command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quantile",
            description="""
                The quantiles are values which divide the distribution such that
                there is a given proportion of observations below the quantile.
                For example, the median is a quantile. The median is the central
                value of the distribution, such that half the points are less than
                or equal to it and half are greater than or equal to it.

                By default, q is set at 0.5, which effectively is median. Change q to
                get the desired quantile (0<q<1).
            """,
        )

        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
        )

        parser.add_argument(
            "-q",
            "--quantile",
            action="store",
            dest="f_quantile",
            type=check_proportion_range,
            default=0.5,
            help="quantile",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            rolling_view.view_quantile(
                s_ticker=self.ticker,
                s_interval=self.interval,
                df_stock=self.stock,
                length=ns_parser.n_length,
                quantile=ns_parser.f_quantile,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_skew(self, other_args: List[str]):
        """Process skew command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="skew",
            description="""
                Skewness is a measure of asymmetry or distortion of symmetric
                distribution. It measures the deviation of the given distribution
                of a random variable from a symmetric distribution, such as normal
                distribution. A normal distribution is without any skewness, as it is
                symmetrical on both sides. Hence, a curve is regarded as skewed if
                it is shifted towards the right or the left.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
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
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            rolling_view.view_skew(
                s_ticker=self.ticker,
                s_interval=self.interval,
                df_stock=self.stock,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")


def menu(ticker: str, start: datetime, interval: str, stock: pd.DataFrame):
    """Statistics Menu"""

    qa_controller = QaController(ticker, start, interval, stock)
    qa_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in qa_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(qa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(qa)> ")

        try:
            plt.close("all")

            process_input = qa_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
