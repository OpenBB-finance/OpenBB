"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import random
from typing import List, Union
from datetime import datetime, timedelta
import yfinance as yf
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    valid_date,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.stocks.comparison_analysis import (
    finbrain_view,
    finnhub_model,
    finviz_compare_model,
    finviz_compare_view,
    marketwatch_view,
    polygon_model,
    yahoo_finance_view,
    yahoo_finance_model,
)


# pylint: disable=E1121,C0302,R0904


class ComparisonAnalysisController:
    """Comparison Analysis Controller class"""

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]
    CHOICES_COMMANDS = [
        "ticker",
        "getpoly",
        "getfinnhub",
        "getfinviz",
        "set",
        "add",
        "rmv",
        "historical",
        "hcorr",
        "volume",
        "income",
        "balance",
        "cashflow",
        "sentiment",
        "scorr",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "tsne",
    ]
    CHOICES_MENUS = [
        "po",
    ]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

    def __init__(
        self,
        similar: List[str] = None,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.ca_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.ca_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:

            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.ticker = ""
        self.user = ""

        if similar:
            self.similar = similar
            if len(similar) == 1:
                self.ticker = self.similar[0].upper()
        else:
            self.similar = []

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = f"""
    ticker        set ticker to get similar companies from{Style.NORMAL if self.ticker else Style.DIM}

Ticker to get similar companies from: {self.ticker}

    tsne          run TSNE on all SP500 stocks and returns closest tickers
    getpoly       get similar stocks from polygon API
    getfinnhub    get similar stocks from finnhub API
    getfinviz     get similar stocks from finviz API{Style.RESET_ALL}

    set           reset and set similar companies
    add           add more similar companies
    rmv           remove similar companies individually or all
{Style.NORMAL if self.similar and len(self.similar)>1 else Style.DIM}
Similar Companies: {', '.join(self.similar) if self.similar else ''}

Yahoo Finance:
    historical    historical price data comparison
    hcorr         historical price correlation
    volume        historical volume data comparison
Market Watch:
    income        income financials comparison
    balance       balance financials comparison
    cashflow      cashflow comparison
Finbrain:
    sentiment     sentiment analysis comparison
    scorr         sentiment correlation
Finviz:
    overview      brief overview comparison
    valuation     brief valuation comparison
    financial     brief financial comparison
    ownership     brief ownership comparison
    performance   brief performance comparison
    technical     brief technical comparison

>   po            portfolio optimization for selected tickers{Style.RESET_ALL}
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.ca_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        # additional quit for when we come to this menu through a relative path
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        if self.similar:
            self.queue.insert(0, f"set {','.join(self.similar)}")
        self.queue.insert(0, "ca")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_ticker(self, other_args: List[str]):
        """Process ticker command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ticker",
            description="""Set ticker to extract similars from""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            required=True,
            help="Ticker get similar tickers from",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if "," in ns_parser.ticker:
                print("Only one ticker must be selected!")
            else:
                stock_data = yf.download(
                    ns_parser.ticker,
                    progress=False,
                )
                if stock_data.empty:
                    print(f"The ticker '{ns_parser.ticker}' provided does not exist!")
                else:
                    self.ticker = ns_parser.ticker.upper()
            print("")

    @try_except
    def call_tsne(self, other_args: List[str]):
        """Process tsne command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tsne",
            description="""Get similar companies to compare with using sklearn TSNE.""",
        )
        parser.add_argument(
            "-r",
            "--learnrate",
            default=200,
            dest="lr",
            type=check_non_negative,
            help="TSNE Learning rate.  Typical values are between 50 and 200",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve. The subsample will occur randomly.",
        )
        parser.add_argument(
            "-p", "--no_plot", action="store_true", default=False, dest="no_plot"
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar = yahoo_finance_model.get_sp500_comps_tsne(
                    self.ticker,
                    lr=ns_parser.lr,
                    no_plot=ns_parser.no_plot,
                    num_tickers=ns_parser.limit,
                )

                self.similar = [self.ticker] + self.similar
                print(f"[ML] Similar Companies: {', '.join(self.similar)}", "\n")

            else:
                print("You need to 'set' a ticker to get similar companies from first!")

    @try_except
    def call_getfinviz(self, other_args: List[str]):
        """Process getfinviz command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinviz",
            description="""Get similar companies from finviz to compare with.""",
        )
        parser.add_argument(
            "-n",
            "--nocountry",
            action="store_true",
            default=False,
            dest="b_no_country",
            help="Similar stocks from finviz using only Industry and Sector.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                if ns_parser.b_no_country:
                    compare_list = ["Sector", "Industry"]
                else:
                    compare_list = ["Sector", "Industry", "Country"]

                self.similar, self.user = finviz_compare_model.get_similar_companies(
                    self.ticker, compare_list
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                if self.similar:
                    self.similar = [self.ticker] + self.similar

                    print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )
            else:
                print("You need to 'set' a ticker to get similar companies from first!")

    @try_except
    def call_getpoly(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getpoly",
            description="""Get similar companies from polygon to compare with.""",
        )
        parser.add_argument(
            "-u",
            "--us_only",
            action="store_true",
            default=False,
            dest="us_only",
            help="Show only stocks from the US stock exchanges",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar, self.user = polygon_model.get_similar_companies(
                    self.ticker, ns_parser.us_only
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                self.similar = [self.ticker] + self.similar

                if self.similar:
                    print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )

            else:
                print("You need to 'set' a ticker to get similar companies from first!")

    @try_except
    def call_getfinnhub(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinnhub",
            description="""Get similar companies from finnhub to compare with.""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar, self.user = finnhub_model.get_similar_companies(
                    self.ticker
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                self.similar = [self.ticker] + self.similar

                if self.similar:
                    print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )

            else:
                print("You need to 'set' a ticker to get similar companies from first!")

    @try_except
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="""Add similar tickers to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Tickers to add to similar list",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.similar:
                self.similar = list(set(self.similar + ns_parser.l_similar))
            else:
                self.similar = ns_parser.l_similar
            self.user = "Custom"

            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

    @try_except
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmv",
            description="""Remove similar tickers to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Tickers to remove from similar list",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.l_similar:
                for symbol in ns_parser.l_similar:
                    if symbol in self.similar:
                        self.similar.remove(symbol)
                    else:
                        print(
                            f"Ticker {symbol} does not exist in similar list to be removed"
                        )

                print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}")

            else:
                self.similar = []

            print("")
            self.user = "Custom"

    @try_except
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="set",
            description="""Select similar companies to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="similar companies to compare with.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.similar = list(set(ns_parser.l_similar))
            self.user = "Custom"
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

    @try_except
    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="historical",
            description="""Historical price comparison between similar companies.""",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type_candle",
            type=str,
            choices=["o", "h", "l", "c", "a"],
            default="a",  # in case it's adjusted close
            help="Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close.",
        )
        parser.add_argument(
            "-n",
            "--no-scale",
            action="store_false",
            dest="no_scale",
            default=False,
            help="Flag to not put all prices on same 0-1 scale",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_historical(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                    normalize=not ns_parser.no_scale,
                    export=ns_parser.export,
                )

            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_hcorr(self, other_args: List[str]):
        """Process historical correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hcorr",
            description=""" Correlation heatmap based on historical price comparison between similar
            companies.
            """,
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type_candle",
            type=str,
            choices=["o", "h", "l", "c", "a"],
            default="a",  # in case it's adjusted close
            help="Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close.",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_correlation(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                )
            else:
                print("Please make sure there are similar tickers selected. \n")

    @try_except
    def call_income(self, other_args: List[str]):
        """Process income command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="income",
            description="""
                Prints either yearly or quarterly income statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_income_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @try_except
    def call_volume(self, other_args: List[str]):
        """Process volume command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="volume",
            description="""Historical volume comparison between similar companies.
            """,
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_volume(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    export=ns_parser.export,
                )

            else:
                print("Please make sure there are similar tickers selected. \n")

    @try_except
    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balance",
            description="""
                Prints either yearly or quarterly balance statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_balance_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @try_except
    def call_cashflow(self, other_args: List[str]):
        """Process cashflow command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cashflow",
            description="""
                Prints either yearly or quarterly cashflow statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_cashflow_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @try_except
    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sentiment_compare",
            description="""
                FinBrain's sentiment comparison across similar tickers.
            """,
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            default=False,
            help="Display raw sentiment data",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_compare(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_scorr(self, other_args: List[str]):
        """Process sentiment correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sentiment_compare",
            description="""
                FinBrain's sentiment correlation across similar tickers.
            """,
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            default=False,
            help="Display raw sentiment data",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_correlation(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                print("Please make sure there are similar tickers selected. \n")

    @try_except
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="overview",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="valuation",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="valuation",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="financial",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="financial",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ownership",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="ownership",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="performance",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="performance",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @try_except
    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="technical",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="technical",
                    export=ns_parser.export,
                )
            else:
                print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if self.similar and len(self.similar) > 1:
            self.queue = po_controller.menu(self.similar, self.queue, from_submenu=True)
        else:
            print("Please make sure there are more than 1 similar tickers selected. \n")


def menu(
    similar: List,
    queue: List[str] = None,
    from_submenu: bool = False,
):
    """Comparison Analysis Menu"""
    ca_controller = ComparisonAnalysisController(similar, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if ca_controller.queue and len(ca_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if ca_controller.queue[0] in ("q", "..", "quit"):
                print("")
                # Since we came from another menu we need to quit an additional time
                if from_submenu:
                    ca_controller.queue.insert(0, "quit")
                    from_submenu = False

                if len(ca_controller.queue) > 1:
                    return ca_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = ca_controller.queue[0]
            ca_controller.queue = ca_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in ca_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/ca/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                ca_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and ca_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/ca/ $ ",
                    completer=ca_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/ca/ $ ")

        try:
            # Process the input command
            ca_controller.queue = ca_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/ca menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                ca_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        ca_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                ca_controller.queue.insert(0, an_input)
            else:
                print("\n")
