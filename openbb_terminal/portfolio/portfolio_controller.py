"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import date
from typing import List, Optional

import pandas as pd

from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio import (
    attribution_model,
    portfolio_helper,
    portfolio_view,
    statics,
)
from openbb_terminal.portfolio.portfolio_model import generate_portfolio
from openbb_terminal.rich_config import MenuText, console

try:
    from openbb_terminal.portfolio.portfolio_optimization import po_controller

    OPTIMIZATION_TOOLKIT_ENABLED = True
except ModuleNotFoundError:
    OPTIMIZATION_TOOLKIT_ENABLED = False
    console.print(
        "[yellow]"
        "Portfolio Optimization Toolkit is disabled. "
        "To use the Optimization features please install the toolkit following the "
        "instructions here: https://github.com/OpenBB-finance/OpenBBTerminal/"
        "blob/main/openbb_terminal/README.md#anaconda--python"
        "\n"
        "[/yellow]"
    )

# pylint: disable=R1710,E1101,C0415,W0212,too-many-function-args,C0302,too-many-instance-attributes

logger = logging.getLogger(__name__)


class PortfolioController(BaseController):
    """Portfolio Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "show",
        "bench",
        "alloc",
        "attrib",
        "perf",
        "yret",
        "mret",
        "dret",
        "distr",
        "holdv",
        "holdp",
        "maxdd",
        "var",
        "es",
        "om",
        "rvol",
        "rsharpe",
        "rsort",
        "rbeta",
        "metric",
        "summary",
    ]
    CHOICES_MENUS = [
        "bro",
        "po",
    ]
    VALID_DISTRIBUTIONS = ["laplace", "student_t", "logistic", "normal"]
    AGGREGATION_METRICS = ["assets", "sectors", "countries", "regions"]
    VALID_METRICS = [
        "volatility",
        "sharpe",
        "sortino",
        "maxdrawdown",
        "rsquare",
        "skew",
        "kurtosis",
        "gaintopain",
        "trackerr",
        "information",
        "tail",
        "commonsense",
        "jensens",
        "calmar",
        "kelly",
        "payoff",
        "profitfactor",
    ]
    PERIODS = ["3y", "5y", "10y", "all"]
    PATH = "/portfolio/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)
        self.file_types = ["xlsx", "csv"]

        self.DEFAULT_HOLDINGS_PATH = portfolio_helper.DEFAULT_HOLDINGS_PATH

        self.DATA_HOLDINGS_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in self.DEFAULT_HOLDINGS_PATH.rglob(f"*.{file_type}")
        }

        self.portfolio_df = pd.DataFrame(
            columns=[
                "Date",
                "Name",
                "Type",
                "Sector",
                "Industry",
                "Country",
                "Price",
                "Quantity",
                "Fees",
                "Premium",
                "Investment",
                "Side",
                "Currency",
            ]
        )

        self.portfolio_name: str = ""
        self.benchmark_name: str = ""
        self.original_benchmark_ticker = ""
        self.recalculate_alloc = False
        self.risk_free_rate = 0
        self.portlist: List[str] = os.listdir(self.DEFAULT_HOLDINGS_PATH)
        self.portfolio = None

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.update_choices()
            choices: dict = self.choices_default
            self.choices = choices
            self.choices["bench"] = {
                "--benchmark": {c: None for c in statics.BENCHMARK_CHOICES},
                "-b": "--benchmark",
            }
            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_choices(self):
        self.DEFAULT_HOLDINGS_PATH = portfolio_helper.DEFAULT_HOLDINGS_PATH

        self.DATA_HOLDINGS_FILES.update(
            {
                filepath.name: filepath
                for file_type in self.file_types
                for filepath in self.DEFAULT_HOLDINGS_PATH.rglob(f"*.{file_type}")
            }
        )

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/")
        mt.add_menu("bro")
        mt.add_menu("po")
        mt.add_raw("\n")

        mt.add_cmd("load")
        mt.add_cmd("show")
        mt.add_cmd("bench")
        mt.add_raw("\n")
        mt.add_param("_loaded", self.portfolio_name)
        mt.add_param("_riskfreerate", f"{self.risk_free_rate}%")
        mt.add_param("_benchmark", self.benchmark_name)
        mt.add_raw("\n")

        mt.add_info("_graphs_")
        mt.add_cmd("holdv", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("holdp", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("yret", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("mret", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("dret", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("distr", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("maxdd", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("rvol", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("rsharpe", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("rsort", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("rbeta", self.portfolio_name and self.benchmark_name)

        mt.add_info("_metrics_")
        mt.add_cmd("summary", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("alloc", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("attrib", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("metric", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("perf", self.portfolio_name and self.benchmark_name)

        mt.add_info("_risk_")
        mt.add_cmd("var", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("es", self.portfolio_name and self.benchmark_name)
        mt.add_cmd("om", self.portfolio_name and self.benchmark_name)

        console.print(text=mt.menu_text, menu="Portfolio - Portfolio Optimization")
        self.update_choices()

    def custom_reset(self):
        """Class specific component of reset command"""
        objects_to_reload = ["portfolio"]
        if self.portfolio_name:
            objects_to_reload.append(f"load {self.portfolio_name}")
        if self.original_benchmark_ticker:
            objects_to_reload.append(f'bench "{self.original_benchmark_ticker}"')
        return objects_to_reload

    @log_start_end(log=logger)
    def call_bro(self, _):
        """Process bro command"""
        from openbb_terminal.portfolio.brokers.bro_controller import BrokersController

        self.queue = self.load_class(BrokersController, self.queue)

    @log_start_end(log=logger)
    def call_po(self, _):
        """Process po command"""
        if OPTIMIZATION_TOOLKIT_ENABLED:
            if self.portfolio is None:
                tickers = []
                categories = None
            else:
                tickers = self.portfolio.tickers_list
                transactions = self.portfolio.get_transactions()

                categories = {
                    "ASSET_CLASS": {},
                    "SECTOR": {},
                    "INDUSTRY": {},
                    "COUNTRY": {},
                    "CURRENT_INVESTED_AMOUNT": {},
                    "CURRENCY": {},
                }
                for _, transaction in transactions.iterrows():
                    if transaction["Ticker"] not in categories["ASSET_CLASS"]:
                        categories["ASSET_CLASS"][transaction["Ticker"]] = transaction[
                            "Type"
                        ]
                        categories["SECTOR"][transaction["Ticker"]] = transaction[
                            "Sector"
                        ]
                        categories["INDUSTRY"][transaction["Ticker"]] = transaction[
                            "Industry"
                        ]
                        categories["COUNTRY"][transaction["Ticker"]] = transaction[
                            "Country"
                        ]
                        categories["CURRENT_INVESTED_AMOUNT"][
                            transaction["Ticker"]
                        ] = transactions[
                            transactions["Ticker"] == transaction["Ticker"]
                        ][
                            "Investment"
                        ].sum()
                        categories["CURRENCY"][transaction["Ticker"]] = transaction[
                            "Currency"
                        ]

            self.queue = self.load_class(
                po_controller.PortfolioOptimizationController,
                tickers,
                None,
                categories,
                self.queue,
            )
        else:
            console.print("[yellow]Portfolio Optimization Toolkit is disabled[/yellow]")

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio transactions.",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="file",
            help="The file to be loaded",
            choices={c: {} for c in self.DATA_HOLDINGS_FILES},
            metavar="FILE",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="The name that you wish to give to your portfolio",
        )
        parser.add_argument(
            "-r",
            "--rfr",
            type=float,
            default=0,
            dest="risk_free_rate",
            help="Set the risk free rate.",
        )
        parser.add_argument(
            "-e",
            "--example",
            help="Run an example holdings file to understand how the portfolio menu can be used.",
            dest="example",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.file or ns_parser and ns_parser.example:
            if ns_parser.example:
                file_location = (
                    MISCELLANEOUS_DIRECTORY / "portfolio" / "holdings_example.xlsx"
                )
                console.print(
                    "[green]Loading an example, please type `about` "
                    "to learn how to create your own Portfolio Excel sheet.[/green]\n"
                )
            elif ns_parser.file in self.DATA_HOLDINGS_FILES:
                file_location = self.DATA_HOLDINGS_FILES[ns_parser.file]
            else:
                file_location = ns_parser.file  # type: ignore

            self.portfolio = generate_portfolio(
                transactions_file_path=str(file_location),
                benchmark_symbol="SPY",
                risk_free_rate=ns_parser.risk_free_rate / 100,
            )

            if ns_parser.name:
                self.portfolio_name = ns_parser.name
            elif ns_parser.example:
                self.portfolio_name = "OpenBB Example Portfolio"
            else:
                self.portfolio_name = ns_parser.file
            console.print(
                f"\n[bold][param]Portfolio:[/param][/bold] {self.portfolio_name}"
            )

            self.risk_free_rate = ns_parser.risk_free_rate
            console.print(
                f"[bold][param]Risk Free Rate:[/param][/bold] {self.risk_free_rate}%"
            )

            self.benchmark_name = "SPDR S&P 500 ETF Trust (SPY)"
            console.print(
                f"[bold][param]Benchmark:[/param][/bold] {self.benchmark_name}"
            )

    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]):
        """Process show command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Show transactions table",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            limit=10,
        )
        if ns_parser and self.portfolio is not None:
            portfolio_view.display_transactions(
                self.portfolio,
                show_index=False,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_bench(self, other_args: List[str]):
        """Process bench command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bench",
            description="Load in a benchmark from a selected list or set your own based on the ticker.",
        )
        parser.add_argument(
            "-b",
            "--benchmark",
            type=str,
            default="SPY",
            dest="benchmark",
            required="-h" not in other_args,
            help="Set the benchmark for the portfolio. By default, this is SPDR S&P 500 ETF Trust (SPY).",
            metavar="BENCHMARK",
        )
        parser.add_argument(
            "-s",
            "--full_shares",
            action="store_true",
            default=False,
            dest="full_shares",
            help="Whether to only make a trade with the benchmark when a full share can be bought (no partial shares).",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-b")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if self.portfolio is None:
                console.print(
                    "[red]Please first load transactions file using 'load'[/red]"
                )
            elif self.portfolio.set_benchmark(
                ns_parser.benchmark, ns_parser.full_shares
            ):
                self.benchmark_name = statics.BENCHMARK_CHOICES.get(
                    ns_parser.benchmark, ns_parser.benchmark
                )
                self.original_benchmark_ticker = ns_parser.benchmark
                self.recalculate_alloc = True

    @log_start_end(log=logger)
    def call_alloc(self, other_args: List[str]):
        """Process alloc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="alloc",
            description="""
                Show your allocation to each asset or sector compared to the benchmark.
            """,
        )
        parser.add_argument(
            "-a",
            "--agg",
            default="assets",
            choices=self.AGGREGATION_METRICS,
            dest="agg",
            help="The type of allocation aggregation you wish to do",
            metavar="AGG",
        )
        parser.add_argument(
            "-t",
            "--tables",
            action="store_true",
            default=False,
            dest="tables",
            help="Whether to also include the assets/sectors tables of both the benchmark and the portfolio.",
        )
        if other_args and other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-a")

        ns_parser = self.parse_known_args_and_warn(parser, other_args, limit=10)

        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            if ns_parser.agg == "assets":
                portfolio_view.display_assets_allocation(
                    portfolio_engine=self.portfolio,
                    limit=ns_parser.limit,
                    tables=ns_parser.tables,
                    recalculate=self.recalculate_alloc,
                )
            elif ns_parser.agg == "sectors":
                portfolio_view.display_sectors_allocation(
                    portfolio_engine=self.portfolio,
                    limit=ns_parser.limit,
                    tables=ns_parser.tables,
                    recalculate=self.recalculate_alloc,
                )
            elif ns_parser.agg == "countries":
                portfolio_view.display_countries_allocation(
                    portfolio_engine=self.portfolio,
                    limit=ns_parser.limit,
                    tables=ns_parser.tables,
                    recalculate=self.recalculate_alloc,
                )
            elif ns_parser.agg == "regions":
                portfolio_view.display_regions_allocation(
                    portfolio_engine=self.portfolio,
                    limit=ns_parser.limit,
                    tables=ns_parser.tables,
                    recalculate=self.recalculate_alloc,
                )
            else:
                console.print(
                    f"{ns_parser.agg} is not an available option. The options "
                    f"are: {', '.join(self.AGGREGATION_METRICS)}"
                )

    @log_start_end(log=logger)
    def call_attrib(self, other_args: List[str]):
        """Process attrib command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="attrib",
            description="""
                Displays sector attribution of the portfolio compared to the S&P 500
                """,
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            choices=statics.PERIODS,
            dest="period",
            default="all",
            help="Period in which to calculate attribution",
        )
        parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=["relative", "absolute"],
            dest="type",
            default="relative",
            help="Select between relative or absolute attribution values",
        )
        parser.add_argument(
            "--raw",
            type=bool,
            dest="raw",
            default=False,
            const=True,
            nargs="?",
            help="View raw attribution values in a table",
        )

        if other_args and other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-a")

        ns_parser = self.parse_known_args_and_warn(parser, other_args, limit=10)

        if ns_parser and self.portfolio is not None:
            if check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            ):
                if self.benchmark_name != "SPDR S&P 500 ETF Trust (SPY)":
                    console.print(
                        "This feature uses S&P 500 as benchmark and will disregard selected benchmark if different."
                    )
                # sector contribution
                end_date = date.today()
                # set correct time period
                if ns_parser.period == "all":
                    start_date = self.portfolio.inception_date
                else:
                    start_date = portfolio_helper.get_start_date_from_period(
                        ns_parser.period
                    )

                # calculate benchmark and portfolio contribution values
                bench_result = attribution_model.get_spy_sector_contributions(
                    start_date, end_date
                )
                if bench_result.empty:
                    return
                portfolio_result = attribution_model.get_portfolio_sector_contributions(
                    start_date, self.portfolio.portfolio_trades
                )
                if portfolio_result.empty:
                    return

                # relative results - the proportions of return attribution
                if ns_parser.type == "relative":
                    categorization_result = (
                        attribution_model.percentage_attrib_categorizer(
                            bench_result, portfolio_result
                        )
                    )

                    portfolio_view.display_attribution_categorization(
                        display=categorization_result,
                        time_period=ns_parser.period,
                        attrib_type="Contributions as % of PF",
                        plot_fields=["S&P500 [%]", "Portfolio [%]"],
                        show_table=ns_parser.raw,
                    )

                # absolute - the raw values of return attribution
                if ns_parser.type == "absolute":
                    categorization_result = attribution_model.raw_attrib_categorizer(
                        bench_result, portfolio_result
                    )

                    portfolio_view.display_attribution_categorization(
                        display=categorization_result,
                        time_period=ns_parser.period,
                        attrib_type="Raw contributions (Return x PF Weight)",
                        plot_fields=["S&P500", "Portfolio"],
                        show_table=ns_parser.raw,
                    )

            console.print()

    @log_start_end(log=logger)
    def call_perf(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="performance",
            description="""
                Shows performance of each trade and total performance of the portfolio versus the benchmark.
            """,
        )
        parser.add_argument(
            "-t",
            "--show_trades",
            action="store_true",
            default=False,
            dest="show_trades",
            help="Whether to show performance on all trades in comparison to the benchmark.",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_performance_vs_benchmark(
                self.portfolio,
                ns_parser.show_trades,
            )

    @log_start_end(log=logger)
    def call_holdv(self, other_args: List[str]):
        """Process holdv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holdv",
            description="Display holdings of assets (absolute value)",
        )
        parser.add_argument(
            "-u",
            "--unstack",
            action="store_true",
            default=False,
            dest="unstack",
            help="Sum all assets value over time",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser and check_portfolio_benchmark_defined(
            self.portfolio_name, self.benchmark_name
        ):
            portfolio_view.display_holdings_value(
                self.portfolio,
                ns_parser.unstack,
                ns_parser.raw,
                ns_parser.limit,
                ns_parser.export,
                ns_parser.sheet_name,
            )

    @log_start_end(log=logger)
    def call_holdp(self, other_args: List[str]):
        """Process holdp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holdp",
            description="Display holdings of assets (in percentage)",
        )
        parser.add_argument(
            "-u",
            "--unstack",
            action="store_true",
            default=False,
            dest="unstack",
            help="Sum all assets percentage over time",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser and check_portfolio_benchmark_defined(
            self.portfolio_name, self.benchmark_name
        ):
            portfolio_view.display_holdings_percentage(
                self.portfolio,
                ns_parser.unstack,
                ns_parser.raw,
                ns_parser.limit,
                ns_parser.export,
                ns_parser.sheet_name,
            )

    @log_start_end(log=logger)
    def call_var(self, other_args: List[str]):
        """Process var command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="var",
            description="""
                Provides value at risk (short: VaR) of the selected portfolio.
            """,
        )
        parser.add_argument(
            "-m",
            "--mean",
            action="store_true",
            default=True,
            dest="use_mean",
            help="If one should use the mean of the portfolio return",
        )
        parser.add_argument(
            "-a",
            "--adjusted",
            action="store_true",
            default=False,
            dest="adjusted",
            help="""
                If the VaR should be adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
            """,
        )
        parser.add_argument(
            "-s",
            "--student",
            action="store_true",
            default=False,
            dest="student_t",
            help="""
                If one should use the student-t distribution
            """,
        )
        parser.add_argument(
            "-p",
            "--percentile",
            action="store",
            dest="percentile",
            type=float,
            default=99.9,
            help="""
                Percentile used for VaR calculations, for example input 99.9 equals a 99.9 Percent VaR
            """,
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser and self.portfolio is not None:
            if self.portfolio_name:
                if ns_parser.adjusted and ns_parser.student_t:
                    console.print(
                        "Select either the adjusted or the student_t parameter.\n"
                    )
                else:
                    portfolio_view.display_var(
                        portfolio_engine=self.portfolio,
                        use_mean=ns_parser.use_mean,
                        adjusted_var=ns_parser.adjusted,
                        student_t=ns_parser.student_t,
                        percentile=ns_parser.percentile,
                    )
            else:
                console.print(
                    "[red]Please first define the portfolio using 'load'[/red]\n"
                )

    @log_start_end(log=logger)
    def call_es(self, other_args: List[str]):
        """Process es command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="es",
            description="""
                Provides Expected Shortfall (short: ES) of the selected portfolio.
            """,
        )
        parser.add_argument(
            "-m",
            "--mean",
            action="store_true",
            default=True,
            dest="use_mean",
            help="If one should use the mean of the portfolios return",
        )
        parser.add_argument(
            "-d",
            "--dist",
            dest="distribution",
            type=str,
            choices=self.VALID_DISTRIBUTIONS,
            default="normal",
            help="Distribution used for the calculations",
            metavar="DIST",
        )
        parser.add_argument(
            "-p",
            "--percentile",
            action="store",
            dest="percentile",
            type=float,
            default=99.9,
            help="""
                Percentile used for ES calculations, for example input 99.9 equals a 99.9 Percent Expected Shortfall
            """,
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if self.portfolio and self.portfolio_name:
                portfolio_view.display_es(
                    portfolio_engine=self.portfolio,
                    use_mean=ns_parser.use_mean,
                    distribution=ns_parser.distribution,
                    percentile=ns_parser.percentile,
                )
            else:
                console.print(
                    "[red]Please first define the portfolio using 'load'[/red]\n"
                )

    @log_start_end(log=logger)
    def call_om(self, other_args: List[str]):
        """Process om command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="om",
            description="""
                   Provides omega ratio of the selected portfolio.
               """,
        )
        parser.add_argument(
            "-s",
            "--start",
            action="store",
            dest="start",
            type=float,
            default=0,
            help="""
                   Start of the omega ratio threshold
               """,
        )
        parser.add_argument(
            "-e",
            "--end",
            action="store",
            dest="end",
            type=float,
            default=1.5,
            help="""
                   End of the omega ratio threshold
               """,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser and self.portfolio is not None:
            if self.portfolio_name:
                data = self.portfolio.portfolio_returns[1:]
                qa_view.display_omega(
                    data,
                    ns_parser.start,
                    ns_parser.end,
                )
            else:
                console.print(
                    "[red]Please define the portfolio first (via 'load')[/red]\n"
                )

    @log_start_end(log=logger)
    def call_yret(self, other_args: List[str]):
        """Process yret command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="yret",
            description="End of the year returns",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="all",
            choices=self.PERIODS,
            help="Period to select start end of the year returns",
            metavar="PERIOD",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            raw=True,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
        )

        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_yearly_returns(
                self.portfolio,
                ns_parser.period,
                ns_parser.raw,
                ns_parser.export,
                ns_parser.sheet_name,
            )

    @log_start_end(log=logger)
    def call_mret(self, other_args: List[str]):
        """Process mret command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mret",
            description="Monthly returns",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="all",
            choices=self.PERIODS,
            help="Period to select start end of the year returns",
            metavar="PERIOD",
        )
        parser.add_argument(
            "-i",
            "--instrument",
            type=str,
            dest="instrument",
            default="both",
            choices=["both", "portfolio", "benchmark"],
            help="Whether to show portfolio or benchmark monthly returns. By default both are shown in one table.",
        )
        parser.add_argument(
            "-g",
            "--graph",
            action="store_true",
            default=False,
            dest="graph",
            help="Plot the monthly returns on a heatmap",
        )
        parser.add_argument(
            "-s",
            "--show",
            action="store_true",
            default=False,
            dest="show_vals",
            help="Show monthly returns on heatmap",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            raw=True,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
        )

        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_monthly_returns(
                self.portfolio,
                ns_parser.period,
                ns_parser.instrument,
                ns_parser.graph,
                ns_parser.show_vals,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dret(self, other_args: List[str]):
        """Process dret command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dret",
            description="Daily returns",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="all",
            choices=self.PERIODS,
            help="Period to select start end of the year returns",
            metavar="PERIOD",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            raw=True,
            limit=10,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
        )

        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_daily_returns(
                self.portfolio,
                ns_parser.period,
                ns_parser.raw,
                ns_parser.limit,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_maxdd(self, other_args: List[str]):
        """Process maxdd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxdd",
            description="Show portfolio maximum drawdown",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_maximum_drawdown(
                self.portfolio,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_rvol(self, other_args: List[str]):
        """Process rolling volatility command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rvol",
            description="Show rolling volatility portfolio vs benchmark",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="1y",
            choices=statics.PERIODS,
            help="Period to apply rolling window",
            metavar="PERIOD",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_rolling_volatility(
                self.portfolio,
                window=ns_parser.period,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rsharpe(self, other_args: List[str]):
        """Process rolling sharpe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsharpe",
            description="Show rolling sharpe portfolio vs benchmark",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="1y",
            choices=statics.PERIODS,
            help="Period to apply rolling window",
            metavar="PERIOD",
        )
        parser.add_argument(
            "-r",
            "--rfr",
            type=float,
            dest="risk_free_rate",
            default=self.risk_free_rate,
            help="Set risk free rate for calculations.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_rolling_sharpe(
                self.portfolio,
                risk_free_rate=ns_parser.risk_free_rate / 100,
                window=ns_parser.period,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rsort(self, other_args: List[str]):
        """Process rolling sortino command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsort",
            description="Show rolling sortino portfolio vs benchmark",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="1y",
            choices=statics.PERIODS,
            help="Period to apply rolling window",
            metavar="PERIOD",
        )
        parser.add_argument(
            "-r",
            "--rfr",
            type=float,
            dest="risk_free_rate",
            default=self.risk_free_rate,
            help="Set risk free rate for calculations.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_rolling_sortino(
                portfolio_engine=self.portfolio,
                risk_free_rate=ns_parser.risk_free_rate / 100,
                window=ns_parser.period,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rbeta(self, other_args: List[str]):
        """Process rolling beta command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rbeta",
            description="Show rolling beta portfolio vs benchmark",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            dest="period",
            default="1y",
            choices=statics.PERIODS,
            help="Period to apply rolling window",
            metavar="PERIOD",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_rolling_beta(
                self.portfolio,
                window=ns_parser.period,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_metric(self, other_args: List[str]):
        """Process metric command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metric",
            description="Display metric of choice for different periods",
        )
        parser.add_argument(
            "-m",
            "--metric",
            type=str,
            dest="metric",
            default="-h" not in other_args,
            choices=self.VALID_METRICS,
            help="Set metric of choice",
            metavar="METRIC",
        )
        parser.add_argument(
            "-r",
            "--rfr",
            type=float,
            dest="risk_free_rate",
            default=self.risk_free_rate,
            help="Set risk free rate for calculations.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser and check_portfolio_benchmark_defined(
            self.portfolio_name, self.benchmark_name
        ):
            if ns_parser.metric == "skew":
                portfolio_view.display_skewness(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "kurtosis":
                portfolio_view.display_kurtosis(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "volatility":
                portfolio_view.display_volatility(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "sharpe":
                portfolio_view.display_sharpe_ratio(
                    self.portfolio,
                    ns_parser.risk_free_rate / 100,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "sortino":
                portfolio_view.display_sortino_ratio(
                    self.portfolio,
                    ns_parser.risk_free_rate / 100,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "maxdrawdown":
                portfolio_view.display_maximum_drawdown_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "rsquare":
                portfolio_view.display_rsquare(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "gaintopain":
                portfolio_view.display_gaintopain_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "trackerr":
                portfolio_view.display_tracking_error(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "information":
                portfolio_view.display_information_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "tail":
                portfolio_view.display_tail_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "commonsense":
                portfolio_view.display_common_sense_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "jensens":
                portfolio_view.display_jensens_alpha(
                    self.portfolio,
                    ns_parser.risk_free_rate / 100,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "calmar":
                portfolio_view.display_calmar_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "kelly":
                portfolio_view.display_kelly_criterion(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "payoff" and self.portfolio is not None:
                portfolio_view.display_payoff_ratio(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.metric == "profitfactor" and self.portfolio is not None:
                portfolio_view.display_profit_factor(
                    self.portfolio,
                    ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_distr(self, other_args: List[str]):
        """Process distr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="distr",
            description="Compute distribution of daily returns",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            choices=statics.PERIODS,
            dest="period",
            default="all",
            help="The file to be loaded",
            metavar="PERIOD",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            raw=True,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_distribution_returns(
                self.portfolio,
                ns_parser.period,
                ns_parser.raw,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="summary",
            description="Display summary of portfolio vs benchmark",
        )
        parser.add_argument(
            "-p",
            "--period",
            type=str,
            choices=statics.PERIODS,
            dest="period",
            default="all",
            help="The file to be loaded",
            metavar="PERIOD",
        )
        parser.add_argument(
            "-r",
            "--rfr",
            type=float,
            dest="risk_free_rate",
            default=self.risk_free_rate,
            help="Set risk free rate for calculations.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        if (
            ns_parser
            and self.portfolio is not None
            and check_portfolio_benchmark_defined(
                self.portfolio_name, self.benchmark_name
            )
        ):
            portfolio_view.display_summary(
                self.portfolio,
                ns_parser.period,
                ns_parser.risk_free_rate / 100,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )


def check_portfolio_benchmark_defined(portfolio_name: str, benchmark_name: str) -> bool:
    """Check that portfolio and benchmark have been defined

    Parameters
    ----------
    portfolio_name: str
        Portfolio name, will be empty if not defined
    benchmark_name: str
        Benchmark name, will be empty if not defined

    Returns
    -------
    bool
        If both portfolio and benchmark have been defined
    """

    if not portfolio_name:
        console.print("[red]Please first define the portfolio (via 'load')[/red]\n")
        return False

    if not benchmark_name:
        console.print("[red]Please first define the benchmark (via 'bench')[/red]\n")
        return False

    return True
