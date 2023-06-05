"""Discovery Controller Module."""
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_int_range,
    check_non_negative,
    check_positive,
    valid_date,
    valid_date_in_past,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.discovery import (
    ark_view,
    finnhub_view,
    finviz_view,
    fmp_view,
    nasdaq_view,
    seeking_alpha_view,
    shortinterest_view,
    yahoofinance_view,
)

# pylint:disable=C0302


logger = logging.getLogger(__name__)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "filings",
        "pipo",
        "fipo",
        "gainers",
        "losers",
        "ugs",
        "gtech",
        "active",
        "ulc",
        "asc",
        "arkord",
        "upcoming",
        "trending",
        "lowfloat",
        "hotpenny",
        "rtat",
        "divcal",
        "heatmap",
    ]

    arkord_sortby_choices = [
        "date",
        "volume",
        "open",
        "high",
        "close",
        "low",
        "total",
        "weight",
        "shares",
    ]
    arkord_fund_choices = ["ARKK", "ARKF", "ARKW", "ARKQ", "ARKG", "ARKX", ""]

    PATH = "/stocks/disc/"
    dividend_columns = [
        "Name",
        "Symbol",
        "Ex-Dividend Date",
        "Payment Date",
        "Record Date",
        "Dividend",
        "Annual Dividend",
        "Announcement Date",
    ]
    heatmap_timeframes = ["day", "week", "month", "3month", "6month", "year", "ytd"]
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/disc/")
        mt.add_cmd("filings", "FinancialModelingPrep")
        mt.add_cmd("pipo", "Finnhub")
        mt.add_cmd("fipo", "Finnhub")
        mt.add_cmd("gainers", "Yahoo Finance")
        mt.add_cmd("losers", "Yahoo Finance")
        mt.add_cmd("ugs", "Yahoo Finance")
        mt.add_cmd("gtech", "Yahoo Finance")
        mt.add_cmd("active", "Yahoo Finance")
        mt.add_cmd("ulc", "Yahoo Finance")
        mt.add_cmd("asc", "Yahoo Finance")
        mt.add_cmd("arkord", "Cathies Ark")
        mt.add_cmd("upcoming", "Seeking Alpha")
        mt.add_cmd("trending", "Seeking Alpha")
        mt.add_cmd("lowfloat", "Fidelity")
        mt.add_cmd("hotpenny", "Shortinterest")
        mt.add_cmd("rtat", "NASDAQ Data Link")
        mt.add_cmd("divcal", "NASDAQ Data Link")
        mt.add_cmd("heatmap", "Finviz")
        console.print(text=mt.menu_text, menu="Stocks - Discovery")

    # TODO Add flag for adding last price to the following table
    @log_start_end(log=logger)
    def call_divcal(self, other_args: List[str]):
        """Process divcal command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="divcal",
            description="""Get dividend calendar for selected date""",
        )
        parser.add_argument(
            "-d",
            "--date",
            default=datetime.now(),
            type=valid_date,
            dest="date",
            help="Date to get format for",
        )
        parser.add_argument(
            "-s",
            "--sort",
            default="dividend",
            type=str.lower,
            choices=stocks_helper.format_parse_choices(self.dividend_columns),
            help="Column to sort by",
            dest="sort",
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            # Map fixes

            sort_col = stocks_helper.map_parse_choices(self.dividend_columns)[
                ns_parser.sort
            ]
            nasdaq_view.display_dividend_calendar(
                date=ns_parser.date.strftime("%Y-%m-%d"),
                sortby=sort_col,
                ascend=ns_parser.reverse,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_pipo(self, other_args: List[str]):
        """Process pipo command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pipo",
            description="""
                Past IPOs dates. [Source: https://finnhub.io]
            """,
        )
        parser.add_argument(
            "-d",
            "--days",
            action="store",
            dest="days",
            type=check_non_negative,
            default=5,
            help="Number of past days to look for IPOs.",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date_in_past,
            default=None,
            dest="start",
            help="""The starting date (format YYYY-MM-DD) to look for IPOs.
            When set, start date will override --days argument""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_non_negative,
            default=20,
            help="Limit number of IPOs to display.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finnhub_view.past_ipo(
                num_days_behind=ns_parser.days,
                limit=ns_parser.limit,
                start_date=ns_parser.start,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_fipo(self, other_args: List[str]):
        """Process fipo command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fipo",
            description="""
                Future IPOs dates. [Source: https://finnhub.io]
            """,
        )

        parser.add_argument(
            "-d",
            "--days",
            action="store",
            dest="days",
            type=check_non_negative,
            default=5,
            help="Number of days in the future to look for IPOs.",
        )

        parser.add_argument(
            "-s",
            "--end",
            type=valid_date,
            default=None,
            dest="end",
            help="""The end date (format YYYY-MM-DD) to look for IPOs, starting from today.
            When set, end date will override --days argument""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_non_negative,
            default=20,
            help="Limit number of IPOs to display.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            finnhub_view.future_ipo(
                num_days_ahead=ns_parser.days,
                limit=ns_parser.limit,
                end_date=ns_parser.end,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_gainers(self, other_args: List[str]):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gainers",
            description="Print up to 25 top gainers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_gainers(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_losers(self, other_args: List[str]):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="losers",
            description="Print up to 25 top losers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_losers(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ugs(self, other_args: List[str]):
        """Process ugs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ugs",
            description="""
                Print up to 25 undervalued stocks with revenue and earnings growth in excess of 25%.
                [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_ugs(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_gtech(self, other_args: List[str]):
        """Process gtech command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gtech",
            description="Print up to 25 top tech stocks with revenue and earnings"
            + " growth in excess of 25%. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_gtech(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_active(self, other_args: List[str]):
        """Process active command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="active",
            description="""
                Print up to 25 top most actively traded intraday tickers. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_active(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ulc(self, other_args: List[str]):
        """Process ulc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ulc",
            description="""
                Print up to 25 potentially undervalued large cap stocks. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_ulc(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_asc(self, other_args: List[str]):
        """Process asc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="asc",
            description="""
                Print up to 25 small cap stocks with earnings growth rates better than 25%. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_asc(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_arkord(self, other_args: List[str]):
        """Process arkord command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="arkord",
            description="""
                Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of stocks to display.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            choices=self.arkord_sortby_choices,
            type=str,
            help="Column to sort by",
            default="",
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
            "-b",
            "--buy_only",
            dest="buys_only",
            help="Flag to look at buys only",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--sell_only",
            dest="sells_only",
            help="Flag to look at sells only",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--fund",
            type=str,
            default="",
            help="Filter by fund",
            dest="fund",
            choices=self.arkord_fund_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.ark_orders_view(
                limit=ns_parser.limit,
                sortby=ns_parser.sort_col,
                ascend=ns_parser.reverse,
                buys_only=ns_parser.buys_only,
                sells_only=ns_parser.sells_only,
                fund=ns_parser.fund,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_upcoming(self, other_args: List[str]):
        # TODO: switch to nasdaq
        """Process upcoming command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="upcoming",
            description="""Upcoming earnings release dates. [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of upcoming earnings release dates to look ahead.",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start  date of data, in YYYY-MM-DD format. Defaults to today.",
            dest="start_date",
            default=datetime.today().strftime("%Y-%m-%d"),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            seeking_alpha_view.upcoming_earning_release_dates(
                limit=ns_parser.limit,
                start_date=ns_parser.start_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_trending(self, other_args: List[str]):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trending",
            description="""Trending news articles. [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-i",
            "--id",
            action="store",
            dest="n_id",
            type=check_positive,
            default=-1,
            help="article ID",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of articles being printed",
        )
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="s_date",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            help="starting date of articles",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            seeking_alpha_view.news(
                article_id=ns_parser.n_id,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_lowfloat(self, other_args: List[str]):
        """Process lowfloat command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lowfloat",
            description="""
                Print top stocks with lowest float. LowFloat.com provides a convenient
                sorted database of stocks which have a float of under 10 million shares. Additional key
                data such as the number of outstanding shares, short interest, and company industry is
                displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange,
                the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of stocks to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.low_float(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_hotpenny(self, other_args: List[str]):
        """Process hotpenny command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hotpenny",
            description="Provides top penny stocks from various websites. [Source: Yfinance]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of stocks to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.hot_penny_stocks(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                source=ns_parser.source,
            )

    @log_start_end(log=logger)
    def call_rtat(self, other_args: List[str]):
        """Process rtat command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rtat",
            description="""
                Tracking over $30B USD/day of individual investors trades,
                RTAT gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
                ADRs, and ETPs
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=3,
            help="limit of days to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nasdaq_view.display_top_retail(
                limit=ns_parser.limit, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_filings(self, other_args: List[str]) -> None:
        """Process Filings command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="filings",
            description="The most-recent filings submitted to the SEC",
        )
        parser.add_argument(
            "-p",
            "--pages",
            dest="pages",
            metavar="pages",
            type=int,
            default=1,
            help="The number of pages to get data from (1000 entries/page; maximum 30 pages)",
        )
        parser.add_argument(
            "-t",
            "--today",
            dest="today",
            action="store_true",
            default=False,
            help="Show all filings from today",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=5,
        )
        if ns_parser:
            fmp_view.display_filings(
                ns_parser.pages, ns_parser.limit, ns_parser.today, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_heatmap(self, other_args: List[str]):
        """Process heatmap command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="heatmap",
            description="""
                    Get the SP 500 heatmap from finviz and display in interactive treemap
                """,
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            default="day",
            choices=self.heatmap_timeframes,
            help="Timeframe to get heatmap data for",
            dest="timeframe",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_heatmap(
                ns_parser.timeframe,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
