"""ETF Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf

from openbb_terminal.common import newsapi_view
from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import (
    financedatabase_view,
    fmp_view,
    stockanalysis_model,
    stockanalysis_view,
)
from openbb_terminal.etf.discovery import disc_controller
from openbb_terminal.etf.technical_analysis import ta_controller
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    export_data,
    list_from_str,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.comparison_analysis import ca_controller

# pylint: disable=C0415,C0302


logger = logging.getLogger(__name__)


class ETFController(BaseController):
    """ETF Controller class"""

    CHOICES_COMMANDS = [
        "search",
        "load",
        "overview",
        "holdings",
        "holding_perf",
        "news",
        "candle",
        "weights",
        "compare",
        "resources",
    ]
    CHOICES_MENUS = [
        "ta",
        "ca",
        # "scr",
        "disc",
    ]
    CANDLE_COLUMNS = [
        "adjclose",
        "open",
        "close",
        "high",
        "low",
        "volume",
        "returns",
        "logret",
    ]

    PATH = "/etf/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.etf_name = ""
        self.etf_data = ""
        self.etf_holdings: List = list()
        self.TRY_RELOAD = True

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("etf/")
        mt.add_cmd("search")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_symbol", self.etf_name)
        mt.add_param("_major_holdings", ", ".join(self.etf_holdings))
        mt.add_raw("\n")
        mt.add_menu("ca", len(self.etf_holdings))
        mt.add_menu("disc")
        # mt.add_menu("scr")
        mt.add_raw("\n")
        mt.add_cmd("overview", self.etf_name)
        mt.add_cmd("holdings", self.etf_name)
        mt.add_cmd("holding_perf", self.etf_name)
        mt.add_cmd("weights", self.etf_name)
        mt.add_cmd("news", self.etf_name)
        mt.add_cmd("candle", self.etf_name)
        mt.add_raw("\n")
        mt.add_cmd("compare", self.etf_name)
        mt.add_raw("\n")
        mt.add_menu("ta", self.etf_name)
        console.print(text=mt.menu_text, menu="ETF")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.etf_name:
            return ["etf", f"load {self.etf_name}"]
        return []

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Search ETF by name [Source: FinanceDatabase/StockAnalysis.com]",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="Name to look for ETFs",
            default="",
            required="-h" not in other_args
            and "-d" not in other_args
            and "--description" not in other_args,
        )
        parser.add_argument(
            "-d",
            "--description",
            type=str,
            dest="description",
            nargs="+",
            help="Name to look for ETFs",
            default="",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=5,
        )
        if ns_parser:
            name_to_search = " ".join(ns_parser.name)

            if ns_parser.name:
                if ns_parser.source == "FinanceDatabase":
                    financedatabase_view.display_etf_by_name(
                        name=name_to_search,
                        limit=ns_parser.limit,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )
                elif ns_parser.source == "StockAnalysis":
                    stockanalysis_view.display_etf_by_name(
                        name=name_to_search,
                        limit=ns_parser.limit,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )
                else:
                    console.print("Wrong source choice!\n")
            else:
                description_to_search = " ".join(ns_parser.description)
                financedatabase_view.display_etf_by_description(
                    description=description_to_search,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load ETF ticker to perform analysis on.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="ETF ticker",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the ETF",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the ETF",
        )

        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            default=5,
            dest="limit",
            help="Limit of holdings to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            df_etf_candidate = yf.download(
                ns_parser.ticker,
                start=ns_parser.start,
                end=ns_parser.end,
                progress=False,
            )
            if df_etf_candidate.empty:
                console.print("ETF ticker provided does not exist!\n")
                return

            df_etf_candidate.index.name = "date"

            self.etf_name = ns_parser.ticker.upper()
            self.etf_data = df_etf_candidate

            console.print(
                f"Loading Daily data for {self.etf_name} with starting period {ns_parser.start.strftime('%Y-%m-%d')}.",
            )

            try:
                self.etf_holdings = list(
                    stockanalysis_model.get_etf_holdings(self.etf_name)[
                        : ns_parser.limit
                    ].index
                )
            except Exception as e:
                console.print(f"Error: {e}")

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Get overview data for selected etf",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            stockanalysis_view.view_overview(
                symbol=self.etf_name,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holdings",
            description="Look at ETF company holdings",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            dest="limit",
            help="Number of holdings to get",
            default=10,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.etf_name:
                stockanalysis_view.view_holdings(
                    symbol=self.etf_name,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
                console.print()
            else:
                console.print("Please load a ticker using <load name>. \n")

    @log_start_end(log=logger)
    def call_news(self, other_args: List[str]):
        """Process news command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="news",
            description="""
                Prints latest news about ETF, including date, title and web link.
                [Source: News API]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of latest news being printed.",
        )
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="n_start_date",
            type=valid_date,
            default=datetime.now() - timedelta(days=7),
            help="The starting date (format YYYY-MM-DD) to search articles from",
        )
        parser.add_argument(
            "-o",
            "--oldest",
            action="store_false",
            dest="n_oldest",
            default=True,
            help="Show oldest articles first",
        )
        parser.add_argument(
            "-s",
            "--sources",
            default="",
            type=str,
            help="Show news only from the sources specified (e.g bbc yahoo.com)",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.etf_name:
                sources = list_from_str(ns_parser.sources)
                for idx, source in enumerate(sources):
                    if source.find(".") == -1:
                        sources[idx] += ".com"
                clean_sources = ",".join(sources)

                newsapi_view.display_news(
                    query=self.etf_name,
                    limit=ns_parser.limit,
                    start_date=ns_parser.n_start_date.strftime("%Y-%m-%d"),
                    show_newest=ns_parser.n_oldest,
                    sources=clean_sources,
                )
            else:
                console.print("Use 'load <ticker>' prior to this command!")
        console.print()

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Shows historic data for an ETF",
        )
        parser.add_argument(
            "-p",
            "--plotly",
            dest="plotly",
            action="store_false",
            default=True,
            help="Flag to show interactive plotly chart.",
        )
        parser.add_argument(
            "--sort",
            "-s",
            choices=self.CANDLE_COLUMNS,
            default="",
            type=str.lower,
            dest="sort",
            help="Choose a column to sort by",
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
            "-n",
            "--num",
            type=check_positive,
            help="Number to show if raw selected",
            dest="num",
            default=20,
            choices=range(1, 100),
            metavar="NUM",
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store_true",
            default=False,
            help="Flag to add high and low trends to candle.",
            dest="trendlines",
        )
        parser.add_argument(
            "--ma",
            dest="mov_avg",
            type=str,
            help=(
                "Add moving average in number of days to plot and separate by a comma. "
                "Value for ma (moving average) keyword needs to be greater than 1."
            ),
            default="",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            figure = None
            if not self.etf_name:
                console.print("No ticker loaded. First use `load {ticker}`\n")
                return
            if ns_parser.raw:
                qa_view.display_raw(
                    data=self.etf_data,
                    sortby=ns_parser.sort,
                    ascend=ns_parser.reverse,
                    limit=ns_parser.num,
                )

            else:
                data = stocks_helper.process_candle(self.etf_data)
                mov_avgs = []

                if ns_parser.mov_avg:
                    mov_list = (num for num in ns_parser.mov_avg.split(","))

                    for num in mov_list:
                        try:
                            clean_num = int(num)

                            if clean_num <= 1:
                                raise ValueError

                            mov_avgs.append(clean_num)
                        except ValueError:
                            console.print(
                                f"[red]{num} is not a valid moving average, must be an integer "
                                "greater than 1.[/red]\n"
                            )

                figure = stocks_helper.display_candle(
                    symbol=self.etf_name,
                    data=data,
                    add_trend=ns_parser.trendlines,
                    ma=mov_avgs,
                    asset_type="ETF",
                    external_axes=True,
                )

            export_data(
                ns_parser.export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{self.etf_name}",
                self.etf_data,
                ns_parser.sheet_name,
                figure=figure,
            )
            if figure:
                figure.show()  # type: ignore

    @log_start_end(log=logger)
    def call_weights(self, other_args: List[str]):
        """Process weights command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="weights",
            description="Look at ETF sector holdings",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            fmp_view.display_etf_weightings(
                name=self.etf_name,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command"""
        if self.etf_name and not self.etf_data.empty:
            self.queue = self.load_class(
                ta_controller.TechnicalAnalysisController,
                self.etf_name,
                self.etf_data.index[0],
                self.etf_data,
                self.queue,
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_ca(self, other_args: List[str]):
        """Process ca command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ca",
            description="Compare ETF's holdings with each other",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )

        if ns_parser:
            if len(self.etf_holdings) == 0:
                console.print(
                    "Load a ticker with major holdings to compare them on this menu\n"
                )
            elif len(self.etf_holdings) > 0:
                self.queue = ca_controller.ComparisonAnalysisController(
                    self.etf_holdings, self.queue
                ).menu(custom_path_menu_above="/stocks/")

    @log_start_end(log=logger)
    def call_disc(self, _):
        """Process disc command"""
        self.queue = self.load_class(disc_controller.DiscoveryController, self.queue)

    @log_start_end(log=logger)
    def call_compare(self, other_args):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare selected ETFs [Source: StockAnalysis]",
        )
        parser.add_argument(
            "-e",
            "--etfs",
            type=str,
            dest="names",
            help="Symbols to compare",
            required="-h" not in other_args,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        # to allow inputs with spaces in between them instead of commas (inputs with spaces are not parsed correctly)

        if len(other_args) > 2:
            for i in range(2, len(other_args)):
                other_args[1] += "," + other_args[i]
            del other_args[2 : len(other_args)]

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            etf_list = ns_parser.names.upper().split(",")
            stockanalysis_view.view_comparisons(
                etf_list,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_holding_perf(self, other_args: List[str]):
        """Process holdings performance command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holding_perf",
            description="Look at ETF company holdings' performance",
        )
        parser.add_argument(
            "-s",
            "--start-date",
            type=valid_date,
            default=(datetime.now().date() - timedelta(days=366)),
            dest="start",
            help="The starting date (format YYYY-MM-DD) to get each holding's price",
        )
        parser.add_argument(
            "-e",
            "--end-date",
            type=valid_date,
            default=datetime.now().date(),
            dest="end",
            help="The ending date (format YYYY-MM-DD) to get each holding's price",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            dest="limit",
            help="Number of holdings to get",
            default=20,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            if self.etf_name:
                fmp_view.view_etf_holdings_performance(
                    ticker=self.etf_name,
                    start_date=ns_parser.start,
                    end_date=ns_parser.end,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=ns_parser.sheet_name,
                    raw=ns_parser.raw,
                )
            else:
                console.print("Please load a ticker using <load name>. \n")
