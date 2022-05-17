"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from pathlib import Path
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    check_positive,
    check_positive_float,
    parse_known_args_and_warn,
    print_rich_table,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio import portfolio_model
from openbb_terminal.portfolio import portfolio_view
from openbb_terminal.portfolio import portfolio_helper
from openbb_terminal.portfolio.portfolio_optimization import po_controller
from openbb_terminal.rich_config import console
from openbb_terminal.common.quantitative_analysis import qa_view

# pylint: disable=R1710,E1101,C0415,W0212,too-many-function-args

logger = logging.getLogger(__name__)

portfolios_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "portfolios")


class PortfolioController(BaseController):
    """Portfolio Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "show",
        "bench",
        "alloc",
        "perf",
        "ar",
        "rmr",
        "al",
        "dd",
        "rolling",
        "var",
        "es",
        "sh",
        "so",
        "om",
    ]
    CHOICES_MENUS = [
        "bro",
        "po",
        "pa",
    ]
    distributions = ["laplace", "student_t", "logistic", "normal"]
    aggregation_methods = ["assets", "sectors", "countries", "regions"]
    PATH = "/portfolio/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.file_types = ["xlsx", "csv"]

        self.DEFAULT_HOLDINGS_PATH = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "portfolio", "holdings")
        )

        self.DATA_HOLDINGS_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in Path(self.DEFAULT_HOLDINGS_PATH).rglob(f"*.{file_type}")
            if filepath.is_file()
        }

        self.portfolio = pd.DataFrame(
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

        self.portfolio_name = ""
        self.benchmark_name = ""
        self.portlist: List[str] = os.listdir(self.DEFAULT_HOLDINGS_PATH)
        self.portfolio = portfolio_model.Portfolio()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_HOLDINGS_FILES}
            choices["bench"] = {c: None for c in portfolio_helper.BENCHMARK_LIST}
            choices["alloc"] = {c: None for c in self.aggregation_methods}
            self.choices = choices

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        # NOTE: See comment at `call_pa` definition
        # >   pa          portfolio analysis, \t\t analyse portfolios
        help_text = f"""[menu]
>   bro         brokers holdings, \t\t supports: robinhood, ally, degiro, coinbase
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt[/menu]

[info]Portfolio:[/info][cmds]
    load        load data into the portfolio
    show        show existing transactions
    bench       define the benchmark[/cmds]

[param]Loaded orderbook:[/param] {self.portfolio_name or None}
[param]Benchmark:[/param] {self.benchmark_name or None}
[param]Risk Free Rate:[/param] {self.portfolio.rf:.2%}

[info]Performance:[/info][cmds]
    alloc       show allocation on an asset or sector basis
    perf        show (total) performance of the portfolio versus benchmark

[info]Graphs:[/info][cmds]
    rolling     display rolling metrics of portfolio and benchmark
    rmr         graph your returns versus the market's returns
    dd          display portfolio drawdown
    al          display allocation to given assets over period[/cmds]

[info]Risk Metrics:[/info][cmds]
    var         display value at risk
    es          display expected shortfall
    sh          display sharpe ratio
    so          display sortino ratio
    om          display omega ratio[/cmds]
        """
        # TODO: Clean up the reports inputs
        # TODO: Edit the allocation to allow the different asset classes
        # [info]Reports:[/info]
        #    ar          annual report for performance of a given portfolio
        console.print(text=help_text, menu="Portfolio")

    @log_start_end(log=logger)
    def call_bro(self, _):
        """Process bro command"""
        from openbb_terminal.portfolio.brokers.bro_controller import (
            BrokersController,
        )

        self.queue = self.load_class(BrokersController, self.queue)

    @log_start_end(log=logger)
    def call_po(self, _):
        """Process po command"""
        if self.portfolio.empty:
            tickers = []
        else:
            tickers = (
                self.portfolio._stock_tickers
                + self.portfolio._etf_tickers
                + self.portfolio._crypto_tickers
            )
        self.queue = self.load_class(
            po_controller.PortfolioOptimizationController,
            tickers,
            None,
            None,
            self.queue,
        )

    # BUG: The commands in pa menu throw errors. First one says that it's related to
    #      string formatting and the second one has something to do with None being used
    #      instead of [] in the queue (assumption) what throws errors on the logger.
    # TODO: This submenu is disabled until the bug is fixed.
    # def call_pa(self, _):
    #     """Process pa command"""
    #     from openbb_terminal.portfolio.portfolio_analysis import pa_controller
    #
    #     self.queue = self.queue = self.load_class(
    #         pa_controller.PortfolioAnalysisController, self.queue
    #     )

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            choices=self.DATA_HOLDINGS_FILES,
            dest="file",
            required="-h" not in other_args,
            help="The file to be loaded",
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
            "--risk_free_rate",
            type=str,
            default=0,
            dest="risk_free_rate",
            help="Set the risk free rate.",
        )

        if other_args:
            if "-f" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-f")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.file:
            if ns_parser.file in self.DATA_HOLDINGS_FILES:
                file_location = self.DATA_HOLDINGS_FILES[ns_parser.file]
            else:
                file_location = ns_parser.file  # type: ignore

            if str(file_location).endswith(".csv"):
                self.portfolio = portfolio_model.Portfolio.from_csv(file_location)
            elif str(file_location).endswith(".xlsx"):
                self.portfolio = portfolio_model.Portfolio.from_xlsx(file_location)

            if ns_parser.name:
                self.portfolio_name = ns_parser.name
            else:
                self.portfolio_name = ns_parser.file

            # Generate holdings from trades
            self.portfolio.generate_holdings_from_trades()

            # Add in the Risk-free rate
            self.portfolio.add_rf(ns_parser.risk_free_rate)

            console.print(f"\n[bold]Portfolio:[/bold] {self.portfolio_name}")
            console.print(f"[bold]Risk Free Rate:[/bold] {self.portfolio.rf}")

            console.print()

    @log_start_end(log=logger)
    def call_show(self, _):
        """Process show command"""
        if self.portfolio.empty:
            logger.warning("No portfolio loaded")
            console.print("[red]No portfolio loaded.[/red]\n")
            return

        print_rich_table(self.portfolio.trades, show_index=False)
        console.print()

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
            nargs="+",
            dest="benchmark",
            required="-h" not in other_args,
            help="Set the benchmark for the portfolio. By default, this is SPDR S&P 500 ETF Trust (SPY).",
        )

        if "-b" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-b")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.benchmark:
            chosen_benchmark = " ".join(ns_parser.benchmark)

            if chosen_benchmark in portfolio_helper.BENCHMARK_LIST:
                benchmark_ticker = portfolio_helper.BENCHMARK_LIST[chosen_benchmark]
            else:
                benchmark_ticker = chosen_benchmark

            self.portfolio.add_benchmark(benchmark_ticker)
            self.benchmark_name = self.portfolio.benchmark_info["longName"]

            console.print(
                f"[bold]\nBenchmark:[/bold] {self.benchmark_name} ({benchmark_ticker})"
            )

            console.print()

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
            choices=self.aggregation_methods,
            dest="agg",
            help="The type of allocation aggregation you wish to do",
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            type=int,
            dest="limit",
            help="The amount of assets or sectors you wish to see",
        )

        parser.add_argument(
            "-t",
            "--tables",
            action="store_true",
            default=False,
            dest="tables",
            help="Whether to also include the assets/sectors tables of both the benchmark and the portfolio.",
        )

        if other_args:
            if "-a" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-a")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.agg:
            if self.portfolio_name and self.benchmark_name:
                if self.portfolio.portfolio_assets_allocation.empty:
                    self.portfolio.calculate_allocations()

                if ns_parser.agg == "assets":
                    portfolio_view.display_assets_allocation(
                        self.portfolio.portfolio_assets_allocation,
                        self.portfolio.benchmark_assets_allocation,
                        ns_parser.limit,
                        ns_parser.tables,
                    )
                elif ns_parser.agg == "sectors":
                    portfolio_view.display_category_allocation(
                        ns_parser.agg,
                        self.portfolio.portfolio_sectors_allocation,
                        self.portfolio.benchmark_sectors_allocation,
                        ns_parser.limit,
                        ns_parser.tables,
                    )
                elif ns_parser.agg == "countries":
                    portfolio_view.display_category_allocation(
                        ns_parser.agg,
                        self.portfolio.portfolio_country_allocation,
                        self.portfolio.benchmark_country_allocation,
                        ns_parser.limit,
                        ns_parser.tables,
                    )
                elif ns_parser.agg == "regions":
                    portfolio_view.display_category_allocation(
                        ns_parser.agg,
                        self.portfolio.portfolio_regional_allocation,
                        self.portfolio.benchmark_regional_allocation,
                        ns_parser.limit,
                        ns_parser.tables,
                    )
                else:
                    console.print(
                        f"{ns_parser.agg} is not an available option. The options "
                        f"are: {', '.join(self.aggregation_methods)}"
                    )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

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
            "-s",
            "--full_shares",
            action="store_true",
            default=False,
            dest="full_shares",
            help="Whether to only make a trade with the benchmark when a full share can be bought (no partial shares).",
        )

        parser.add_argument(
            "-t",
            "--show_trades",
            action="store_true",
            default=False,
            dest="show_trades",
            help="Whether to show performance on all trades in comparison to the benchmark.",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                self.portfolio.mimic_portfolio_trades_for_benchmark(
                    full_shares=ns_parser.full_shares
                )

                portfolio_view.display_performance_vs_benchmark(
                    self.portfolio.portfolio_trades,
                    self.portfolio.benchmark_trades,
                    ns_parser.show_trades,
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_al(self, other_args: List[str]):
        """Process al command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="al",
            description="Display allocation",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                portfolio_view.display_allocation(self.portfolio, ns_parser.export)
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    # def call_ar(self, other_args: List[str]):
    #     """Process ar command"""
    #     parser = argparse.ArgumentParser(
    #         add_help=False,
    #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    #         prog="ar",
    #         description="Create an annual report based on given portfolio",
    #     )
    #     parser.add_argument(
    #         "-m",
    #         "--market",
    #         type=str,
    #         dest="market",
    #         default="SPY",
    #         help="Choose a ticker to be the market asset",
    #     )
    #     ns_parser = parse_known_args_and_warn(parser, other_args)
    #     if ns_parser:
    #         if not self.portfolio.empty:
    #             self.portfolio.generate_holdings_from_trades()
    #             self.portfolio.add_benchmark(ns_parser.market)
    #             portfolio_view.Report(
    #                 val, hist, ns_parser.market, 365
    #             ).generate_report()
    #         else:
    #             console.print("Please add items to the portfolio\n")

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
            default=False,
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                if ns_parser.adjusted and ns_parser.student_t:
                    console.print(
                        "Select either the adjusted or the student_t parameter.\n"
                    )
                else:
                    qa_view.display_var(
                        self.portfolio.returns,
                        "Portfolio",
                        ns_parser.use_mean,
                        ns_parser.adjusted,
                        ns_parser.student_t,
                        ns_parser.percentile / 100,
                        True,
                    )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
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
            default=False,
            dest="use_mean",
            help="If one should use the mean of the portfolios return",
        )
        parser.add_argument(
            "-d",
            "--dist",
            "--distributions",
            dest="distributions",
            type=str,
            choices=self.distributions,
            default="normal",
            help="Distribution used for the calculations",
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                qa_view.display_es(
                    self.portfolio.returns,
                    "Portfolio",
                    ns_parser.use_mean,
                    ns_parser.distributions,
                    ns_parser.percentile / 100,
                    True,
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_sh(self, other_args: List[str]):
        """Process sh command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sh",
            description="""
                        Provides the sharpe ratio of the selected portfolio.
                    """,
        )
        parser.add_argument(
            "-r",
            "--rfr",
            action="store",
            dest="rfr",
            type=float,
            default=0,
            help="Risk free return",
        )
        parser.add_argument(
            "-w",
            "--window",
            action="store",
            dest="window",
            type=int,
            default=252,
            help="Rolling window length",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                data = self.portfolio.portfolio_value[1:]
                qa_view.display_sharpe(data, ns_parser.rfr, ns_parser.window)
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_so(self, other_args: List[str]):
        """Process so command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="so",
            description="""
                    Provides the sortino ratio of the selected portfolio.
                """,
        )
        parser.add_argument(
            "-t",
            "--target",
            action="store",
            dest="target_return",
            type=float,
            default=0,
            help="Target return",
        )
        parser.add_argument(
            "-a",
            "--adjusted",
            action="store_true",
            default=False,
            dest="adjusted",
            help="If one should adjust the sortino ratio inorder to make it comparable to the sharpe ratio",
        )
        parser.add_argument(
            "-w",
            "--window",
            action="store",
            dest="window",
            type=int,
            default=252,
            help="Rolling window length",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                data = self.portfolio.returns[1:]
                qa_view.display_sortino(
                    data, ns_parser.target_return, ns_parser.window, ns_parser.adjusted
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                data = self.portfolio.returns[1:]
                qa_view.display_omega(
                    data,
                    ns_parser.start,
                    ns_parser.end,
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_rmr(self, other_args: List[str]):
        """Process rmr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmr",
            description="Graph of portfolio returns versus market returns",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                portfolio_view.display_returns_vs_bench(
                    self.portfolio.returns, self.portfolio.benchmark_returns
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_dd(self, other_args: List[str]):
        """Process dd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dd",
            description="Show portfolio drawdown",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                portfolio_view.display_drawdown(self.portfolio.portfolio_value)
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )

    @log_start_end(log=logger)
    def call_rolling(self, other_args: List[str]):
        """Process rolling command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rolling",
            description="Show rolling portfolio metrics vs benchmark",
        )

        parser.add_argument(
            "-l",
            "--length",
            type=check_positive,
            dest="length",
            default=60,
            help="Length of rolling window",
        )
        parser.add_argument(
            "-r",
            "--rf",
            type=check_positive_float,
            dest="rf",
            default=self.portfolio.rf,
            help="Set risk free rate for calculations.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.portfolio_name and self.benchmark_name:
                portfolio_view.display_rolling_stats(
                    self.portfolio.benchmark_returns,
                    self.portfolio.returns,
                    length=ns_parser.length,
                    risk_free_rate=ns_parser.rf,
                )
            else:
                console.print(
                    "[red]Please first define the portfolio (via 'load') "
                    "and the benchmark (via 'bench').[/red]\n"
                )
