"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"
# pylint:disable=too-many-lines
import argparse
import difflib
import random
from typing import List

from datetime import datetime, timedelta
import yfinance as yf
from colorama import Style
from matplotlib import pyplot as plt
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

# pylint: disable=E1121


class ComparisonAnalysisController:
    """Comparison Analysis Controller class"""

    # Command choices
    CHOICES = ["?", "cls", "help", "q", "quit"]

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
    CHOICES_MENUS = ["po"]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

    def __init__(
        self,
        similar: List[str] = None,
    ):
        """Constructor

        Parameters
        ----------
        similar : List
            Similar tickers
        """
        if similar:
            self.similar = similar
        else:
            self.similar = []

        if similar and len(similar) == 1:
            self.ticker = self.similar[0].upper()
        else:
            self.ticker = ""

        self.user = ""

        self.ca_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.ca_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_str = f"""
Comparison Analysis:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

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
        print(help_str)

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

        # For the case where a user uses: 'add NIO,XPEV,LI'
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("You need to 'set' a ticker to get similar companies from first!")
            return

        self.similar = yahoo_finance_model.get_sp500_comps_tsne(
            self.ticker,
            lr=ns_parser.lr,
            no_plot=ns_parser.no_plot,
            num_tickers=ns_parser.limit,
        )

        self.similar = [self.ticker] + self.similar

        print(f"[ML] Similar Companies: {', '.join(self.similar)}", "\n")

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
            "--nocountry",
            action="store_true",
            default=False,
            dest="b_no_country",
            help="Similar stocks from finviz using only Industry and Sector.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("You need to 'set' a ticker to get similar companies from first!")
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
            self.similar = [self.ticker] + self.similar

            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("You need to 'set' a ticker to get similar companies from first!")
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

        self.similar = [self.ticker] + self.similar

        if self.similar:
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

    @try_except
    def call_getfinnhub(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinnhub",
            description="""Get similar companies from finnhub to compare with.""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.ticker:
            print("You need to 'set' a ticker to get similar companies from first!")
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

        self.similar = [self.ticker] + self.similar

        if self.similar:
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

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

        # For the case where a user uses: 'add NIO,XPEV,LI'
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        # Add sets to avoid duplicates
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

        # For the case where a user uses: 'add NIO,XPEV,LI'
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.l_similar:
            # Add sets to avoid duplicates
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

        # For the case where a user uses: 'select NIO,XPEV,LI'
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        self.similar = list(set(ns_parser.l_similar))
        self.user = "Custom"
        print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n")

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
            system_clear()
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

    @try_except
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        yahoo_finance_view.display_historical(
            similar_tickers=self.similar,
            start=ns_parser.start,
            candle_type=ns_parser.type_candle,
            normalize=not ns_parser.no_scale,
            export=ns_parser.export,
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are similar tickers selected. \n")
            return

        yahoo_finance_view.display_correlation(
            similar_tickers=self.similar,
            start=ns_parser.start,
            candle_type=ns_parser.type_candle,
        )

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are similar tickers selected. \n")
            return

        yahoo_finance_view.display_volume(
            similar_tickers=self.similar,
            start=ns_parser.start,
            export=ns_parser.export,
        )

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finbrain_view.display_sentiment_compare(
            similar=self.similar,
            raw=ns_parser.raw,
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are similar tickers selected. \n")
            return

        finbrain_view.display_sentiment_correlation(
            similar=self.similar,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="overview",
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="valuation",
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="financial",
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="ownership",
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="performance",
            export=ns_parser.export,
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return

        finviz_compare_view.screener(
            similar=self.similar,
            data_type="technical",
            export=ns_parser.export,
        )

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if not self.similar or len(self.similar) == 1:
            print("Please make sure there are more than 1 similar tickers selected. \n")
            return None

        return po_controller.menu(self.similar)


def menu(similar: List):
    """Comparison Analysis Menu

    Parameters
    ----------
    similar : List
        Similar tickers
    """

    ca_controller = ComparisonAnalysisController(similar)
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
            similar_cmd = difflib.get_close_matches(
                an_input, ca_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
