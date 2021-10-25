"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"
# pylint:disable=too-many-lines
import argparse
import os
import random
from typing import List

from colorama import Style
import pandas as pd
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    get_flair,
    parse_known_args_and_warn,
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
from gamestonk_terminal.stocks.stocks_helper import load

# pylint: disable=E1121


class ComparisonAnalysisController:
    """Comparison Analysis Controller class"""

    # Command choices
    CHOICES = ["?", "cls", "help", "q", "quit"]

    CHOICES_COMMANDS = [
        "load",
        "getpoly",
        "getfinnhub",
        "getfinviz",
        "select",
        "add",
        "historical",
        "hcorr",
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
    CHOICES_MENUS = ["po"]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor

        Parameters
        ----------
        ticker : str
            Stock ticker
        start : str
            Start time
        interval : str
            Time interval
        stock : pd.DataFrame
            Stock data
        """
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.similar: List[str] = []
        self.user = ""

        self.ca_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.ca_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        all_loaded = bool(not self.ticker or not self.similar)
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            stock_str = f"{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
        else:
            stock_str = f"{s_intraday} Stock: {self.ticker}"
        help_str = f"""
{stock_str}
Similar Companies: {', '.join(self.similar) or None}

Comparison Analysis:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

    load          load new base ticker
    add           add more companies to current selected (max 10 total)
    select        reset and select similar companies

Get Similar:
    tsne          run TSNE on all SP500 stocks and returns 10 closest tickers
    getpoly       get similar stocks from polygon API
    getfinnhub    get similar stocks from finnhub API
    getfinviz     get similar stocks from finviz API
{Style.DIM if all_loaded else Style.NORMAL}Yahoo Finance:
    historical    historical price data comparison
    hcorr         historical price correlation {Style.RESET_ALL}
Market Watch:
    income        income financials comparison
    balance       balance financials comparison
    cashflow      cashflow comparison
Finbrain:
    sentiment     sentiment analysis comparison {Style.DIM if all_loaded else Style.NORMAL}
    scorr         sentiment correlation{Style.RESET_ALL}
Finviz:
    overview      brief overview comparison
    valuation     brief valuation comparison
    financial     brief financial comparison
    ownership     brief ownership comparison
    performance   brief performance comparison
    technical     brief technical comparison

>   po            portfolio optimization for selected tickers
        """
        print(help_str)

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, self.start, self.interval, self.stock = load(
            other_args, self.ticker, self.start, self.interval, self.stock
        )
        if "." in self.ticker:
            self.ticker = self.ticker.split(".")[0]

    def call_tsne(self, other_args: List[str]):
        """Process tsne command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tsne",
            description="""Get similar companies to compare with using sklearn TSNE.""",
        )
        parser.add_argument(
            "-l",
            "--learnrate",
            default=200,
            dest="lr",
            type=check_non_negative,
            help="TSNE Learning rate.  Typical values are between 50 and 200",
        )
        parser.add_argument(
            "-p", "--no_plot", action="store_true", default=False, dest="no_plot"
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            self.similar = yahoo_finance_model.get_sp500_comps_tsne(
                self.ticker, lr=ns_parser.lr, no_plot=ns_parser.no_plot
            )
            print(f"[ML] Similar Companies: {', '.join(self.similar)}", "\n")
        except Exception as e:
            print(e, "\n")

    def call_getfinviz(self, other_args: List[str]):
        """Process getfinviz command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinviz",
            description="""Get similar companies from finviz to compare with.""",
        )
        parser.add_argument(
            "--nocountry",
            action="store_true",
            default=False,
            dest="b_no_country",
            help="Similar stocks from finviz using only Industry and Sector.",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            if ns_parser.b_no_country:
                compare_list = ["Sector", "Industry"]
            else:
                compare_list = ["Sector", "Industry", "Country"]

            self.similar, self.user = finviz_compare_model.get_similar_companies(
                self.ticker, compare_list
            )

            if self.ticker.upper() in self.similar:
                self.similar.remove(self.ticker.upper())

            if len(self.similar) > 10:
                random.shuffle(self.similar)
                self.similar = sorted(self.similar[:10])
                print(
                    "The limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.\n",
                )

            if self.similar:
                print(
                    f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n"
                )
        except Exception as e:
            print(e, "\n")

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

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            self.similar, self.user = polygon_model.get_similar_companies(
                self.ticker, ns_parser.us_only
            )

            if self.ticker.upper() in self.similar:
                self.similar.remove(self.ticker.upper())

            if len(self.similar) > 10:
                random.shuffle(self.similar)
                self.similar = sorted(self.similar[:10])
                print(
                    "The limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.\n",
                )

            if self.similar:
                print(
                    f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n"
                )

        except Exception as e:
            print(e, "\n")

    def call_getfinnhub(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinnhub",
            description="""Get similar companies from finnhubto compare with.""",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.similar, self.user = finnhub_model.get_similar_companies(self.ticker)

            if self.ticker.upper() in self.similar:
                self.similar.remove(self.ticker.upper())

            if len(self.similar) > 10:
                random.shuffle(self.similar)
                self.similar = sorted(self.similar[:10])
                print(
                    "The limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.\n",
                )

            if self.similar:
                print(
                    f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n"
                )

        except Exception as e:
            print(e, "\n")

    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="""Add similar companies to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="similar companies to compare with.",
        )

        try:
            # For the case where a user uses: 'add NIO,XPEV,LI'
            if other_args and "-" not in other_args[0]:
                other_args.insert(0, "-s")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            # Add sets to avoid duplicates
            self.similar = list(set(self.similar + ns_parser.l_similar))
            if len(self.similar) > 10:
                self.similar = list(random.sample(set(self.similar), 10))
            self.user = "Custom"
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")
        except Exception as e:
            print(e, "\n")

    def call_select(self, other_args: List[str]):
        """Process select command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="select",
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

        try:
            # For the case where a user uses: 'select NIO,XPEV,LI'
            if other_args and "-" not in other_args[0]:
                other_args.insert(0, "-s")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.similar = ns_parser.l_similar
            self.user = "Custom"
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

        except Exception as e:
            print(e, "\n")

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

        (known_args, other_args) = self.ca_parser.parse_known_args(an_input.split())

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

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="historical",
            description="""Historical price comparison between similar companies.
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
            "--no-scale",
            action="store_false",
            dest="no_scale",
            default=True,
            help="Flag to not put all prices on same 0-1 scale",
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
            if self.interval != "1440min":
                print(
                    "Intraday historical data analysis comparison is not yet available."
                )
                # Alpha Vantage only supports 5 calls per minute, we need another API to get intraday data
            else:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                if not self.similar or not self.ticker:
                    print(
                        "Please make sure there are both a loaded ticker and similar tickers selected. \n"
                    )
                    return

                yahoo_finance_view.display_historical(
                    ticker=self.ticker,
                    similar_tickers=self.similar,
                    start=self.start,
                    candle_type=ns_parser.type_candle,
                    normalize=ns_parser.no_scale,
                    export=ns_parser.export,
                )

        except Exception as e:
            print(e, "\n")

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

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if not self.similar or not self.ticker:
                print(
                    "Please make sure there are both a loaded ticker and similar tickers selected. \n"
                )
                return

            yahoo_finance_view.display_correlation(
                ticker=self.ticker,
                similar_tickers=self.similar,
                start=self.start,
                candle_type=ns_parser.type_candle,
            )
        except Exception as e:
            print(e, "\n")

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

            marketwatch_view.display_income_comparison(
                ticker=self.ticker,
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )
        except Exception as e:
            print(e, "\n")

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

            marketwatch_view.display_balance_comparison(
                ticker=self.ticker,
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

        except Exception as e:
            print(e, "\n")

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

            marketwatch_view.display_cashflow_comparison(
                ticker=self.ticker,
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

        except Exception as e:
            print(e, "\n")

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

            finbrain_view.display_sentiment_compare(
                ticker=self.ticker,
                similar=self.similar,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

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

            if not self.similar or not self.ticker:
                print(
                    "Please make sure there are both a loaded ticker and similar tickers selected. \n"
                )
                return
            finbrain_view.display_sentiment_correlation(
                ticker=self.ticker,
                similar=self.similar,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="overview",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="valuation",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="financial",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="ownership",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="performance",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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

            finviz_compare_view.screener(
                ticker=self.ticker,
                similar=self.similar,
                data_type="technical",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        return po_controller.menu([self.ticker] + self.similar)


def menu(ticker: str, start: str, interval: str, stock: pd.DataFrame):
    """Comparison Analysis Menu

    Parameters
    ----------
    ticker : str
        Stock ticker
    start : str
        Time start
    interval : str
        Time interval
    stock : pd.DataFrame
        Stock data
    """

    ca_controller = ComparisonAnalysisController(ticker, start, interval, stock)
    ca_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ca_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(ca)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(ca)> ")

        try:
            plt.close("all")

            process_input = ca_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
