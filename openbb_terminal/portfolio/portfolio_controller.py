"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from os import listdir
from os.path import isfile, join
from typing import Dict, List, Union

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
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio import portfolio_model, portfolio_view
from openbb_terminal.portfolio.portfolio_optimization import po_controller
from openbb_terminal.rich_config import console

# pylint: disable=R1710,E1101,C0415,W0212

logger = logging.getLogger(__name__)

portfolios_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "portfolios")


class PortfolioController(BaseController):
    """Portfolio Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "save",
        "init",
        "show",
        "add",
        "build",
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
    PATH = "/portfolio/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.portfolio = pd.DataFrame(
            columns=[
                "Name",
                "Type",
                "Quantity",
                "Date",
                "Price",
                "Fees",
                "Premium",
                "Side",
            ]
        )

        self.portfolio_name = ""
        self.portlist: List[str] = os.listdir(portfolios_path)
        self.portfolio = portfolio_model.Portfolio()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.portlist}
            choices["save"] = {c: None for c in self.portlist}
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
    save        save your portfolio for future use
    show        show existing transactions
    add         add a security to your portfolio
    init        initialize empty portfolio
    build       build portfolio from list of tickers and weights[/cmds]
[info]
Loaded:[/info] {self.portfolio_name or None}

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
    def call_init(self, other_args: List[str]):
        """Process reset command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="init",
            description="Re-initialize with empty portfolio.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio = portfolio_model.Portfolio()
        console.print()

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load command"""
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(path, "portfolios"))
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=[f for f in listdir(path) if isfile(join(path, f))],
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio = portfolio_model.Portfolio.from_csv(
                os.path.join(portfolios_path, ns_parser.name)
            )
            self.portfolio_name = ns_parser.name
            console.print()

    @log_start_end(log=logger)
    def call_save(self, other_args: List[str]):
        """Process save command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="save",
            description="Save your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args and "-n" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if (
                ".csv" in ns_parser.name
                or ".xlsx" in ns_parser.name
                or ".json" in ns_parser.name
            ):
                portfolio_model.save_df(self.portfolio.trades, ns_parser.name)
            else:
                console.print(
                    "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
                )

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
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds an item to your portfolio",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        console.print()
        inputs: Dict[str, Union[str, float, int]] = {}
        type_ = input("Type (stock, cash): \n")
        if type_ not in ["stock", "cash"]:
            logger.warning("Currently only stocks or cash supported.")
            console.print("[red]Currently only stocks or cash supported.[/red]\n")
            type_ = input("Type (stock, cash): \n")
            if type_ not in ["stock", "cash"]:
                logger.error("Two unsuccessful attempts.  Exiting add")
                console.print("[red]Two unsuccessful attempts.  Exiting add.[/red]\n")
                return

        inputs["Type"] = type_.lower()
        action = input("Action: (buy, sell, deposit, withdraw): \n").lower()

        if type_ == "cash":
            if action not in ["deposit", "withdraw"]:
                console.print("Cash can only be deposit or withdraw\n")
                action = input("Action: (buy, sell, deposit, withdraw): \n").lower()
                if action not in ["deposit", "withdraw"]:
                    logger.error("Two unsuccessful attempts.  Exiting add")
                    console.print(
                        "[red]Two unsuccessful attempts.  Exiting add.[/red]\n"
                    )
                    return

        elif type_ == "stock":
            if action not in ["buy", "sell"]:
                console.print("Stock can only be buy or sell\n")
                if action not in ["buy", "sell"]:
                    logger.error("Two unsuccessful attempts.  Exiting add")
                    console.print(
                        "[red]Two unsuccessful attempts.  Exiting add.[/red]\n"
                    )
                    return

        inputs["Side"] = action.lower()
        inputs["Name"] = input("Name (ticker or cash [if depositing cash]):\n")
        inputs["Date"] = valid_date(input("Purchase date (YYYY-MM-DD): \n")).strftime(
            "%Y-%m-%d"
        )
        inputs["Quantity"] = float(input("Quantity: \n"))
        inputs["Price"] = float(input("Price per share: \n"))
        inputs["Fees"] = float(input("Fees: \n"))
        inputs["Premium"] = ""
        if self.portfolio.empty:
            self.portfolio = portfolio_model.Portfolio(
                pd.DataFrame.from_dict(inputs, orient="index").T
            )
            console.print(
                f"Portfolio successfully initialized with {inputs['Name']}.\n"
            )
            return
        inputs["Value"] = float(inputs["Price"] * inputs["Quantity"])  # type: ignore
        self.portfolio.add_trade(inputs)

        console.print(f"{inputs['Name']} successfully added\n")

    @log_start_end(log=logger)
    def call_build(self, other_args: List[str]):
        """Process build command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="build",
            description="Build portfolio from list of tickers and weights",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start date.",
            dest="start",
            default="2021-01-04",
            type=valid_date,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-t",
            "--tickers",
            type=str,
            help="List of symbols separated by commas (i.e AAPL,BTC,DOGE,SPY....)",
            dest="tickers",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-c",
            "--class",
            help="Asset class (stock, crypto, etf), separated by commas.",
            dest="classes",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-w",
            "--weights",
            help="List of weights, separated by comma",
            type=str,
            dest="weights",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-a",
            "--amount",
            help="Amount to allocate initially.",
            dest="amount",
            default=100_000,
            type=check_positive,
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            list_of_tickers = ns_parser.tickers.split(",")
            types = ns_parser.classes.split(",")
            weights = [float(w) for w in ns_parser.weights.split(",")]
            self.portfolio = portfolio_model.Portfolio.from_custom_inputs_and_weights(
                start_date=ns_parser.start.strftime("%Y-%m-%d"),
                list_of_symbols=list_of_tickers,
                list_of_weights=weights,
                list_of_types=types,
                amount=ns_parser.amount,
            )
        console.print()

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
            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            portfolio_view.display_allocation(self.portfolio, ns_parser.export)

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
            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            if ns_parser.adjusted and ns_parser.student_t:
                console.print("Select the adjusted or the student_t parameter.\n")
            else:
                from openbb_terminal.common.quantitative_analysis import qa_view

                self.portfolio.generate_holdings_from_trades()
                qa_view.display_var(
                    self.portfolio.returns,
                    "Portfolio",
                    ns_parser.use_mean,
                    ns_parser.adjusted,
                    ns_parser.student_t,
                    ns_parser.percentile / 100,
                    True,
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
            from openbb_terminal.common.quantitative_analysis import qa_view

            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            self.portfolio.generate_holdings_from_trades()
            qa_view.display_es(
                self.portfolio.returns,
                "Portfolio",
                ns_parser.use_mean,
                ns_parser.distributions,
                ns_parser.percentile / 100,
                True,
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
            from openbb_terminal.common.quantitative_analysis import qa_view

            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            self.portfolio.generate_holdings_from_trades()
            data = self.portfolio.portfolio_value[1:]
            qa_view.display_sharpe(data, ns_parser.rfr, ns_parser.window)

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
            from openbb_terminal.common.quantitative_analysis import qa_view

            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            self.portfolio.generate_holdings_from_trades()
            data = self.portfolio.returns[1:]
            qa_view.display_sortino(
                data, ns_parser.target_return, ns_parser.window, ns_parser.adjusted
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
            from openbb_terminal.common.quantitative_analysis import qa_view

            if self.portfolio.empty:
                console.print("[red]No portfolio loaded.[/red]\n")
                return
            self.portfolio.generate_holdings_from_trades()
            data = self.portfolio.returns[1:]
            qa_view.display_omega(
                data,
                ns_parser.start,
                ns_parser.end,
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
        parser.add_argument(
            "-m",
            "--market",
            type=str,
            dest="market",
            default="SPY",
            help="Choose a ticker to be the market asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.portfolio.empty:
                portfolio_view.display_returns_vs_bench(
                    self.portfolio, ns_parser.market
                )
            else:
                logger.warning("No portfolio loaded")
                console.print("[red]No portfolio loaded.[/red]")

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
            if not self.portfolio.empty:
                self.portfolio.generate_holdings_from_trades()
                self.portfolio.add_benchmark("SPY")
                portfolio_view.display_drawdown(self.portfolio.portfolio_value)
            else:
                logger.warning("No portfolio loaded")
                console.print("[red]No portfolio loaded.\n[/red]")

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
            "-b",
            "--benchmark",
            type=str,
            dest="benchmark",
            default="SPY",
            help="Choose a ticker to be the benchmark",
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
            default=0.001,
            help="Set risk free rate for calculations.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.portfolio.empty:
                logger.warning("No portfolio loaded")
                console.print("[red]No portfolio loaded[/red].\n")
                return
            portfolio_view.display_rolling_stats(
                self.portfolio,
                length=ns_parser.length,
                benchmark=ns_parser.benchmark,
                risk_free_rate=ns_parser.rf,
            )
