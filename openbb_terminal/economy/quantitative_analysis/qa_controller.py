"""Quantitative Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from openbb_terminal.common.quantitative_analysis import qa_view, rolling_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_list_dates,
    check_positive,
    check_proportion_range,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class QaController(StockBaseController):
    """Quantitative Analysis Controller class"""

    CHOICES_COMMANDS = [
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
    ]
    FULLER_REG = ["c", "ct", "ctt", "nc"]
    KPS_REG = ["c", "ct"]

    PATH = "/economy/qa/"

    def __init__(
        self,
        all_economy_data: Dict,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.datasets = all_economy_data
        self.options = []
        for _, sub_df in all_economy_data.items():
            self.options.extend(list(sub_df.columns))
        self.sources = list(self.datasets.keys())
        self.current_source = self.sources[0]
        # The common functions take in a df and a 'target' column.  In order to replicate this,
        # the following code uses the dictionary of dataframes and finds which source the selected column comes from.
        self.current_source_dataframe = self.datasets[self.current_source].copy()
        self.current_source_dataframe.index.name = "date"
        self.data = self.current_source_dataframe.iloc[:, 0].copy()
        if np.any(pd.isna(self.data)):
            self.current_source_dataframe = self.current_source_dataframe.dropna(axis=0)
            self.data = self.data.dropna(axis=0)
        self.current_id = self.current_source_dataframe.columns[0]
        self.start_date = self.data.index[0]
        self.resolution = ""  # For the views

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["pick"] = {c: {} for c in self.options}
            choices["unitroot"] = {
                "--fuller_reg": {c: {} for c in self.FULLER_REG},
                "-r": "--fuller_reg",
                "--kps_reg": {c: {} for c in self.KPS_REG},
                "-k": "--kps_reg",
            }
            choices["line"] = {
                "--log": {},
                "--ml": None,
                "--ms": None,
            }
            choices["hist"] = {
                "--bins": {str(c): {} for c in range(10, 100)},
                "-b": "--bins",
            }
            choices["bw"] = {
                "--yearly": {},
                "-y": {},
            }
            choices["acf"] = {
                "--lags": {str(c): {} for c in range(5, 100)},
                "-l": "--lags",
            }
            choices["rolling"] = {
                "--window": {str(c): {} for c in range(5, 100)},
                "-w": "--window",
            }
            choices["spread"] = {
                "--window": {str(c): {} for c in range(5, 100)},
                "-w": "--window",
            }
            choices["quantile"] = {
                "--window": {str(c): {} for c in range(5, 100)},
                "-w": "--window",
                "--quantile": {str(c): {} for c in np.arange(0.0, 1.0, 0.01)},
                "-q": "--quantile",
            }
            choices["skew"] = {
                "--window": {str(c): {} for c in range(5, 100)},
                "-w": "--window",
            }
            choices["kurtosis"] = {
                "--window": {str(c): {} for c in range(5, 100)},
                "-w": "--window",
            }
            choices["raw"] = {
                "--limit": None,
                "-l": "--limit",
                "--sortby": {},
                "-s": "--sortby",
                "--reverse": {},
                "-r": "--reverse",
            }
            choices["decompose"] = {
                "--multiplicative": None,
                "-m": "--multiplicative",
            }
            choices["cusum"] = {
                "--threshold": None,
                "-t": "--threshold",
                "--drift": None,
                "-d": "--drift",
            }

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("economy/qa/")
        mt.add_cmd("pick")
        mt.add_raw("\n")
        mt.add_param("_series", self.current_id)
        mt.add_raw("\n")
        mt.add_info("_statistics_")
        mt.add_cmd("summary")
        mt.add_cmd("normality")
        mt.add_cmd("unitroot")
        mt.add_info("_plots_")
        mt.add_cmd("line")
        mt.add_cmd("hist")
        mt.add_cmd("cdf")
        mt.add_cmd("bw")
        mt.add_cmd("acf")
        mt.add_cmd("qqplot")
        mt.add_info("_rolling_metrics_")
        mt.add_cmd("rolling")
        mt.add_cmd("spread")
        mt.add_cmd("quantile")
        mt.add_cmd("skew")
        mt.add_cmd("kurtosis")
        mt.add_info("_other_")
        mt.add_cmd("raw")
        mt.add_cmd("decompose")
        mt.add_cmd("cusum")
        console.print(text=mt.menu_text, menu="Economy - Quantitative Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        return ["economy"]

    @log_start_end(log=logger)
    def call_pick(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="load",
            description="Load a FRED series to current selection",
        )
        parser.add_argument(
            "-c",
            "--column",
            dest="column",
            type=str,
            help="Which loaded source to get data from",
            choices=self.options,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            for source, sub_df in self.datasets.items():
                if ns_parser.column in sub_df.columns:
                    self.current_source = source
                    self.current_source_dataframe = sub_df.copy()
                    self.current_source_dataframe.index.name = "date"
                    # This menu throws errors if there are nans, so lets manipulate them here
                    self.data = sub_df[ns_parser.column].copy()
                    if np.any(pd.isna(self.data)):
                        self.current_source_dataframe = (
                            self.current_source_dataframe.dropna(axis=0)
                        )
                        self.data = self.data.dropna(axis=0)
                    self.current_id = ns_parser.column
                    self.start_date = self.data.index[0]
                    console.print(f"{ns_parser.column} loaded from {source}.\n")
                    return
        console.print(f"[red]{ns_parser.column} not found in data.[/red]\n")

    @log_start_end(log=logger)
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
            "-s",
            "--sortby",
            help="The column to sort by",
            type=str.lower,
            dest="sortby",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        data = self.data.to_frame() if isinstance(self.data, pd.Series) else self.data
        if ns_parser:
            qa_view.display_raw(
                data=data,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_summary(
                data=self.current_source_dataframe,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_line(self, other_args: List[str]):
        """Process line command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="line",
            description="Show line plot of selected data or highlight specific datetimes.",
        )
        parser.add_argument(
            "--log",
            help="Plot with y on log scale",
            dest="log",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--ml",
            help="Draw vertical line markers to highlight certain events",
            dest="ml",
            type=check_list_dates,
            default="",
        )
        parser.add_argument(
            "--ms",
            help="Draw scatter markers to highlight certain events",
            dest="ms",
            type=check_list_dates,
            default="",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            qa_view.display_line(
                self.data,
                title=f"{self.current_id.upper()}",
                log_y=ns_parser.log,
                markers_lines=ns_parser.ml,
                markers_scatter=ns_parser.ms,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_hist(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                bins=ns_parser.n_bins,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_cdf(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_bw(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                yearly=ns_parser.year,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_seasonal(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                multiplicative=ns_parser.multiplicative,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            default=(max(self.data.values) - min(self.data.values)) / 40,
            help="threshold",
        )
        parser.add_argument(
            "-d",
            "--drift",
            dest="drift",
            type=float,
            default=(max(self.data.values) - min(self.data.values)) / 80,
            help="drift",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_cusum(
                data=self.current_source_dataframe,
                target=self.current_id,
                threshold=ns_parser.threshold,
                drift=ns_parser.drift,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_acf(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                lags=ns_parser.lags,
            )

    @log_start_end(log=logger)
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
            "-w",
            "--window",
            action="store",
            dest="n_window",
            type=check_positive,
            default=14,
            help="Window length",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_mean_std(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                window=ns_parser.n_window,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-w",
            "--window",
            action="store",
            dest="n_window",
            type=check_positive,
            default=14,
            help="Window length",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_spread(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                window=ns_parser.n_window,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-w",
            "--window",
            action="store",
            dest="n_window",
            type=check_positive,
            default=14,
            help="window length",
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_quantile(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                window=ns_parser.n_window,
                quantile=ns_parser.f_quantile,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-w",
            "--window",
            action="store",
            dest="n_window",
            type=check_positive,
            default=14,
            help="window length",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_skew(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                window=ns_parser.n_window,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-w",
            "--window",
            action="store",
            dest="n_window",
            type=check_positive,
            default=14,
            help="window length",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rolling_view.display_kurtosis(
                symbol="",
                data=self.current_source_dataframe,
                target=self.current_id,
                window=ns_parser.n_window,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_normality(
                data=self.current_source_dataframe,
                target=self.current_id,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            qa_view.display_qqplot(
                symbol="", data=self.current_source_dataframe, target=self.current_id
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            qa_view.display_unitroot(
                data=self.current_source_dataframe,
                target=self.current_id,
                fuller_reg=ns_parser.fuller_reg,
                kpss_reg=ns_parser.kpss_reg,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
