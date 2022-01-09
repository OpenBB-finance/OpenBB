"""Quantitative Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from rich.console import Console
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.common.quantitative_analysis import (
    qa_view,
    rolling_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_ONLY_FIGURES_ALLOWED,
    check_positive,
    check_proportion_range,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.quantitative_analysis.factors_view import capm_view

t_console = Console()


class QaController(BaseController):
    """Quantitative Analysis Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "pick",
        "raw",
        "summary",
        "line",
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
        "kurtosis",
        "normality",
        "qqplot",
        "unitroot",
        "goodness",
        "unitroot",
        "capm",
    ]

    stock_interval = [1, 5, 15, 30, 60]
    stock_sources = ["yf", "av", "iex"]

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__("/stocks/qa/", queue)

        stock["Returns"] = stock["Adj Close"].pct_change()
        stock["LogRet"] = np.log(stock["Adj Close"]) - np.log(
            stock["Adj Close"].shift(1)
        )
        stock["LogPrice"] = np.log(stock["Adj Close"])
        stock = stock.rename(columns={"Adj Close": "AdjClose"})
        stock = stock.dropna()
        stock.columns = [x.lower() for x in stock.columns]

        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.target = "returns"

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["pick"] = {c: None for c in list(stock.columns)}
            choices["load"]["-i"] = {c: None for c in self.stock_interval}
            choices["load"]["--interval"] = {c: None for c in self.stock_interval}
            choices["load"]["--source"] = {c: None for c in self.stock_sources}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            stock_str = f"{s_intraday} Stock: [cyan]{self.ticker}[/cyan] (from {self.start.strftime('%Y-%m-%d')})"
        else:
            stock_str = f"{s_intraday} Stock: [cyan]{self.ticker}[/cyan]"
        help_str = f"""
   load        load new ticker
   pick        pick target column for analysis

{stock_str}
Target Column: [green]{self.target}[/green]

Statistics:
    summary     brief summary statistics of loaded stock.
    normality   normality statistics and tests
    unitroot    unit root test for stationarity (ADF, KPSS)
Plots:
    line        line plot of selected target
    hist        histogram with density plot
    cdf         cumulative distribution function
    bw          box and whisker plot
    acf         (partial) auto-correlation function differentials of prices
    qqplot      residuals against standard normal curve
Rolling Metrics:
    rolling     rolling mean and std deviation of prices
    spread      rolling variance and std deviation of prices
    quantile    rolling median and quantile of prices
    skew        rolling skewness of distribution of prices
    kurtosis    rolling kurtosis of distribution of prices
Other:
    raw         print raw data
    decompose   decomposition in cyclic-trend, season, and residuals of prices
    cusum       detects abrupt changes using cumulative sum algorithm of prices
    capm        capital asset pricing model
        """
        t_console.print(help_str)

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.target:
                return ["stocks", f"load {self.ticker}", "qa", f"pick {self.target}"]
            return ["stocks", f"load {self.ticker}", "qa"]
        return []

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
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=self.stock_interval,
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=self.stock_sources,
            default="yf",
            help="Source of historical data.",
        )
        parser.add_argument(
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only works for 'yf' source, and intraday data",
        )

        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:

            df_stock_candidate = stocks_helper.load(
                ns_parser.ticker,
                ns_parser.start,
                ns_parser.interval,
                ns_parser.end,
                ns_parser.prepost,
                ns_parser.source,
            )

            if not df_stock_candidate.empty:
                self.stock = df_stock_candidate
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()

                self.start = ns_parser.start
                self.interval = str(ns_parser.interval) + "min"

                self.stock["Returns"] = self.stock["Adj Close"].pct_change()
                self.stock["LogRet"] = np.log(self.stock["Adj Close"]) - np.log(
                    self.stock["Adj Close"].shift(1)
                )
                self.stock["LogPrice"] = np.log(self.stock["Adj Close"])
                self.stock = self.stock.rename(columns={"Adj Close": "AdjClose"})
                self.stock = self.stock.dropna()
                self.stock.columns = [x.lower() for x in self.stock.columns]
                print("")

    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="pick",
            description="""
                Change target variable
            """,
        )
        parser.add_argument(
            "-t",
            "--target",
            dest="target",
            type=lambda x: x.lower(),
            choices=list(self.stock.columns),
            help="Select variable to analyze",
        )
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.target = ns_parser.target
        t_console.print("")

    def call_raw(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="raw",
            description="""
                Print raw data to console
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Number to show",
            type=check_positive,
            default=20,
            dest="limit",
        )
        parser.add_argument(
            "-d",
            "--descend",
            action="store_true",
            default=False,
            dest="descend",
            help="Sort in descending order",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_raw(
                self.stock[self.target],
                num=ns_parser.limit,
                sort="",
                des=ns_parser.descend,
                export=ns_parser.export,
            )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_summary(df=self.stock, export=ns_parser.export)

    def call_line(self, other_args: List[str]):
        """Process line command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="line",
            description="Show line plot of selected data",
        )
        parser.add_argument(
            "--log",
            help="Plot with y on log scale",
            dest="log",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-d",
            "--draw",
            help="Draw lines and annotate on the plot",
            dest="draw",
            action="store_true",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            qa_view.display_line(
                self.stock[self.target],
                title=f"{self.ticker} {self.target}",
                log_y=ns_parser.log,
                draw=ns_parser.draw,
            )

    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="hist",
            description="""
                Histogram with density and rug
            """,
        )
        parser.add_argument(
            "-b", "--bins", type=check_positive, default=15, dest="n_bins"
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_hist(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                bins=ns_parser.n_bins,
            )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_cdf(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                export=ns_parser.export,
            )

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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_bw(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                yearly=ns_parser.year,
            )

    def call_decompose(self, other_args: List[str]):
        """Process decompose command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_seasonal(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                multiplicative=ns_parser.multiplicative,
                export=ns_parser.export,
            )

    def call_cusum(self, other_args: List[str]):
        """Process cusum command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
                max(self.stock[self.target].values)
                - min(self.stock[self.target].values)
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
                max(self.stock[self.target].values)
                - min(self.stock[self.target].values)
            )
            / 80,
            help="drift",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_cusum(
                df=self.stock,
                target=self.target,
                threshold=ns_parser.threshold,
                drift=ns_parser.drift,
            )

    def call_acf(self, other_args: List[str]):
        """Process acf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.target != "AdjClose":
                t_console.print(
                    "Target not AdjClose.  For best results, use `pick AdjClose` first."
                )

            qa_view.display_acf(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                lags=ns_parser.lags,
            )

    def call_rolling(self, other_args: List[str]):
        """Process rolling command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_mean_std(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )

    def call_spread(self, other_args: List[str]):
        """Process spread command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spread",
            description="""Shows rolling spread measurement
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_spread(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_quantile(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                length=ns_parser.n_length,
                quantile=ns_parser.f_quantile,
                export=ns_parser.export,
            )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_skew(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )

    def call_kurtosis(self, other_args: List[str]):
        """Process kurtosis command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="kurtosis",
            description="""
                Kurtosis is a measure of the "tailedness" of the probability distribution
                of a real-valued random variable. Like skewness, kurtosis describes the shape
                of a probability distribution and there are different ways of quantifying it
                for a theoretical distribution and corresponding ways of estimating it from
                a sample from a population. Different measures of kurtosis may have different
                interpretations.
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_kurtosis(
                name=self.ticker,
                df=self.stock,
                target=self.target,
                length=ns_parser.n_length,
                export=ns_parser.export,
            )

    def call_normality(self, other_args: List[str]):
        """Process normality command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="normality",
            description="""
                Normality tests
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_normality(
                df=self.stock, target=self.target, export=ns_parser.export
            )

    def call_qqplot(self, other_args: List[str]):
        """Process qqplot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="qqplot",
            description="""
                Display QQ plot vs normal quantiles
            """,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_qqplot(name=self.ticker, df=self.stock, target=self.target)

    def call_unitroot(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="unitroot",
            description="""
                Unit root test / stationarity (ADF, KPSS)
            """,
        )
        parser.add_argument(
            "-r",
            "--fuller_reg",
            help="Type of regression.  Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order",
            choices=["c", "ct", "ctt", "nc"],
            default="c",
            type=str,
            dest="fuller_reg",
        )
        parser.add_argument(
            "-k",
            "--kps_reg",
            help="Type of regression.  Can be ‘c’,’ct'",
            choices=["c", "ct"],
            type=str,
            dest="kpss_reg",
            default="c",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_unitroot(
                df=self.stock,
                target=self.target,
                fuller_reg=ns_parser.fuller_reg,
                kpss_reg=ns_parser.kpss_reg,
                export=ns_parser.export,
            )

    def call_capm(self, other_args: List[str]):
        """Process capm command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="capm",
            description="""
                Provides detailed information about a stock's risk compared to the market risk.
            """,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            capm_view(self.ticker)
