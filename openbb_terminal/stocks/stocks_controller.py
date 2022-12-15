"""Stock Context Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import financedatabase
import yfinance as yf

from openbb_terminal import feature_flags as obbff
from openbb_terminal.common import feedparser_view, newsapi_view
from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks import cboe_view

from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    export_data,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import (
    MenuText,
    console,
    translate,
)
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks import stocks_view

# pylint: disable=R1710,import-outside-toplevel,R0913,R1702,no-member

logger = logging.getLogger(__name__)


class StocksController(StockBaseController):
    """Stocks Controller class."""

    CHOICES_COMMANDS = [
        "search",
        "load",
        "quote",
        "tob",
        "candle",
        "news",
        "resources",
        "codes",
    ]
    CHOICES_MENUS = [
        "ta",
        "ba",
        "qa",
        "disc",
        "dps",
        "scr",
        "sia",
        "ins",
        "gov",
        "res",
        "fa",
        "bt",
        "dd",
        "ca",
        "options",
        "th",
        "forecast",
    ]

    PATH = "/stocks/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    try:
        country = financedatabase.show_options("equities", "countries")
        sector = financedatabase.show_options("equities", "sectors")
        industry = financedatabase.show_options("equities", "industries")
    except Exception:
        country, sector, industry = {}, {}, {}
        console.print(
            "[red]Note: Some datasets from GitHub failed to load. This means that the `search` command and "
            "the /stocks/sia menu will not work. If other commands are failing please check your internet connection or "
            "communicate with your IT department that certain websites are blocked.[/red] \n"
        )

    TOB_EXCHANGES = ["BZX", "EDGX", "BYX", "EDGA"]
    CHOICES_GENERATION = True

    def __init__(self, queue: List[str] = None):
        """Construct stocks controller."""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        stock_text = ""
        if self.ticker:
            s_intraday = (f"Intraday {self.interval}", "Daily")[
                self.interval == "1440min"
            ]
            stock_text += f"{s_intraday} {self.ticker}"
            if self.start:
                stock_text += f" (from {self.start.strftime('%Y-%m-%d')})"

        mt = MenuText("stocks/", 100)
        mt.add_cmd("search")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", stock_text)
        mt.add_raw(self.add_info)
        mt.add_raw("\n")
        mt.add_cmd("quote", self.ticker)
        mt.add_cmd("tob", self.ticker)
        mt.add_cmd("candle", self.ticker)
        mt.add_cmd("codes", self.ticker)
        mt.add_cmd("news", self.ticker)
        mt.add_raw("\n")
        mt.add_menu("th")
        mt.add_menu("options")
        mt.add_menu("disc")
        mt.add_menu("sia")
        mt.add_menu("dps")
        mt.add_menu("scr")
        mt.add_menu("ins")
        mt.add_menu("gov")
        mt.add_menu("ba")
        mt.add_menu("ca")
        mt.add_menu("fa", self.ticker)
        mt.add_menu("res", self.ticker)
        mt.add_menu("dd", self.ticker)
        mt.add_menu("bt", self.ticker)
        mt.add_menu("ta", self.ticker)
        mt.add_menu("qa", self.ticker)
        mt.add_menu("forecast", self.ticker)
        console.print(text=mt.menu_text, menu="Stocks")

    def custom_reset(self):
        """Class specific component of reset command."""
        if self.ticker:
            return [
                "stocks",
                f"load {self.ticker}.{self.suffix}"
                if self.suffix
                else f"load {self.ticker}",
            ]
        return []

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Show companies matching the search query",
        )
        parser.add_argument(
            "-q",
            "--query",
            action="store",
            dest="query",
            type=str.lower,
            default="",
            nargs="+",
            help="The search term used to find company tickers",
        )
        clean_countries = [x.lower().replace(" ", "_") for x in self.country]
        parser.add_argument(
            "-c",
            "--country",
            default="",
            choices=clean_countries,
            dest="country",
            metavar="country",
            type=str.lower,
            help="Search by country to find stocks matching the criteria",
        )
        parser.add_argument(
            "-s",
            "--sector",
            default="",
            choices=stocks_helper.format_parse_choices(self.sector),
            type=str.lower,
            metavar="sector",
            dest="sector",
            help="Search by sector to find stocks matching the criteria",
        )
        parser.add_argument(
            "-i",
            "--industry",
            default="",
            choices=stocks_helper.format_parse_choices(self.industry),
            type=str.lower,
            metavar="industry",
            dest="industry",
            help="Search by industry to find stocks matching the criteria",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            default="",
            choices=stocks_helper.format_parse_choices(
                list(stocks_helper.market_coverage_suffix.keys())
            ),
            type=str.lower,
            metavar="exchange",
            dest="exchange_country",
            help="Search by a specific exchange country to find stocks matching the criteria",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )
        if ns_parser:
            # Mapping
            sector = stocks_helper.map_parse_choices(self.sector)[ns_parser.sector]
            industry = stocks_helper.map_parse_choices(self.industry)[
                ns_parser.industry
            ]
            exchange = stocks_helper.map_parse_choices(
                list(stocks_helper.market_coverage_suffix.keys())
            )[ns_parser.exchange_country]

            stocks_helper.search(
                query=" ".join(ns_parser.query),
                country=ns_parser.country,
                sector=sector,
                industry=industry,
                exchange_country=exchange,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_tob(self, other_args: List[str]):
        """Process quote command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Get top of book for loaded ticker from selected exchange",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="s_ticker",
            required="-h" not in other_args and not self.ticker,
            help="Ticker to get data for",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            default="BZX",
            choices=self.TOB_EXCHANGES,
            type=str,
            dest="exchange",
        )

        if not self.ticker:
            if other_args and "-" not in other_args[0][0]:
                other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            ticker = ns_parser.s_ticker if ns_parser.s_ticker else self.ticker
            cboe_view.display_top_of_book(ticker, ns_parser.exchange)

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process quote command."""
        ticker = self.ticker + "." + self.suffix if self.suffix else self.ticker
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Current quote for stock ticker",
        )
        if self.ticker:
            parser.add_argument(
                "-t",
                "--ticker",
                action="store",
                dest="s_ticker",
                default=ticker,
                help="Stock ticker",
            )
        else:
            parser.add_argument(
                "-t",
                "--ticker",
                action="store",
                dest="s_ticker",
                required="-h" not in other_args,
                help=translate("stocks/QUOTE_ticker"),
            )
        # For the case where a user uses: 'quote BB'
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            stocks_view.display_quote(ns_parser.s_ticker)

    @log_start_end(log=logger)
    def call_codes(self, _):
        """Process codes command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="codes",
            description="Show CIK, FIGI and SCI code from polygon for loaded ticker.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, _)
        if ns_parser:
            if self.ticker:
                stocks_helper.show_codes_polygon(self.ticker)
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Shows historic data for a stock",
        )
        parser.add_argument(
            "-p",
            "--plotly",
            dest="plotly",
            action="store_false",
            default=True,
            help="Flag to show interactive plotly chart",
        )
        parser.add_argument(
            "--sort",
            choices=stocks_helper.CANDLE_SORT,
            default="",
            type=str.lower,
            dest="sort",
            help="Choose a column to sort by. Only works when raw data is displayed.",
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
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Shows raw data instead of chart.",
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store_true",
            default=False,
            help="Flag to add high and low trends to candle",
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
            default=None,
        )
        parser.add_argument(
            "--log",
            help="Plot with y axis on log scale",
            action="store_true",
            default=False,
            dest="logy",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            limit=20,
        )
        if ns_parser:
            if self.ticker:
                if ns_parser.raw:
                    qa_view.display_raw(
                        data=self.stock,
                        sortby=ns_parser.sort,
                        ascend=ns_parser.reverse,
                        limit=ns_parser.limit,
                    )
                else:
                    data = stocks_helper.process_candle(self.stock)
                    mov_avgs = []

                    if ns_parser.mov_avg:
                        mov_list = (num for num in ns_parser.mov_avg.split(","))

                        for num in mov_list:
                            try:
                                num = int(num)

                                if num <= 1:
                                    raise ValueError

                                mov_avgs.append(num)
                            except ValueError:
                                console.print(
                                    f"[red]{num} is not a valid moving average, must be an integer greater than 1."
                                )

                    stocks_helper.display_candle(
                        symbol=self.ticker,
                        data=data,
                        use_matplotlib=ns_parser.plotly,
                        intraday=self.interval != "1440min",
                        add_trend=ns_parser.trendlines,
                        ma=mov_avgs,
                        yscale="log" if ns_parser.logy else "linear",
                    )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{self.ticker}",
                    self.stock,
                )
            else:
                console.print("No ticker loaded. First use 'load <ticker>'")

    @log_start_end(log=logger)
    def call_news(self, other_args: List[str]):
        """Process news command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="news",
            description="latest news of the company",
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
            dest="sources",
            type=str,
            default="",
            help="Show news only from the sources specified (e.g bloomberg,reuters)",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=3
        )
        if ns_parser:
            if self.ticker:
                if ns_parser.source == "NewsApi":
                    d_stock = yf.Ticker(self.ticker).info

                    newsapi_view.display_news(
                        query=d_stock["shortName"].replace(" ", "+")
                        if "shortName" in d_stock
                        else self.ticker,
                        limit=ns_parser.limit,
                        start_date=ns_parser.n_start_date.strftime("%Y-%m-%d"),
                        show_newest=ns_parser.n_oldest,
                        sources=ns_parser.sources,
                    )
                elif ns_parser.source == "Feedparser":
                    d_stock = yf.Ticker(self.ticker).info

                    feedparser_view.display_news(
                        term=d_stock["shortName"].replace(" ", "+")
                        if "shortName" in d_stock
                        else self.ticker,
                        sources=ns_parser.sources,
                        limit=ns_parser.limit,
                        export=ns_parser.export,
                    )
            else:
                console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_disc(self, _):
        """Process disc command."""
        from openbb_terminal.stocks.discovery.disc_controller import DiscoveryController

        self.queue = self.load_class(DiscoveryController, self.queue)

    @log_start_end(log=logger)
    def call_dps(self, _):
        """Process dps command."""
        from openbb_terminal.stocks.dark_pool_shorts.dps_controller import (
            DarkPoolShortsController,
        )

        self.queue = self.load_class(
            DarkPoolShortsController, self.ticker, self.start, self.stock, self.queue
        )

    @log_start_end(log=logger)
    def call_scr(self, _):
        """Process scr command."""
        from openbb_terminal.stocks.screener.screener_controller import (
            ScreenerController,
        )

        self.queue = self.load_class(ScreenerController, self.queue)

    @log_start_end(log=logger)
    def call_sia(self, _):
        """Process ins command."""
        from openbb_terminal.stocks.sector_industry_analysis.sia_controller import (
            SectorIndustryAnalysisController,
        )

        self.queue = self.load_class(
            SectorIndustryAnalysisController, self.ticker, self.queue
        )

    @log_start_end(log=logger)
    def call_ins(self, _):
        """Process ins command."""
        from openbb_terminal.stocks.insider.insider_controller import InsiderController

        self.queue = self.load_class(
            InsiderController,
            self.ticker,
            self.start,
            self.interval,
            self.stock,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_gov(self, _):
        """Process gov command."""
        from openbb_terminal.stocks.government.gov_controller import GovController

        self.queue = self.load_class(GovController, self.ticker, self.queue)

    @log_start_end(log=logger)
    def call_options(self, _):
        """Process options command."""
        from openbb_terminal.stocks.options.options_controller import OptionsController

        self.queue = self.load_class(OptionsController, self.ticker, self.queue)

    @log_start_end(log=logger)
    def call_th(self, _):
        """Process th command."""
        from openbb_terminal.stocks.tradinghours import tradinghours_controller

        self.queue = self.load_class(
            tradinghours_controller.TradingHoursController,
            self.ticker,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_res(self, _):
        """Process res command."""
        if self.ticker:
            from openbb_terminal.stocks.research.res_controller import (
                ResearchController,
            )

            self.queue = self.load_class(
                ResearchController, self.ticker, self.start, self.interval, self.queue
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_dd(self, _):
        """Process dd command."""
        if self.ticker:
            from openbb_terminal.stocks.due_diligence import dd_controller

            self.queue = self.load_class(
                dd_controller.DueDiligenceController,
                self.ticker,
                self.start,
                self.interval,
                self.stock,
                self.queue,
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Process ca command."""
        from openbb_terminal.stocks.comparison_analysis import ca_controller

        self.queue = self.load_class(
            ca_controller.ComparisonAnalysisController,
            [f"{self.ticker}.{self.suffix}" if self.suffix else self.ticker]
            if self.ticker
            else "",
            self.queue,
        )

    @log_start_end(log=logger)
    def call_fa(self, _):
        """Process fa command."""
        if self.ticker:
            from openbb_terminal.stocks.fundamental_analysis import fa_controller

            self.queue = self.load_class(
                fa_controller.FundamentalAnalysisController,
                self.ticker,
                self.start,
                self.interval,
                self.suffix,
                self.queue,
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_bt(self, _):
        """Process bt command."""
        if self.ticker:
            from openbb_terminal.stocks.backtesting import bt_controller

            self.queue = self.load_class(
                bt_controller.BacktestingController, self.ticker, self.stock, self.queue
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command."""
        if self.ticker:
            from openbb_terminal.stocks.technical_analysis import ta_controller

            self.queue = self.load_class(
                ta_controller.TechnicalAnalysisController,
                self.ticker,
                self.start,
                self.interval,
                self.stock,
                self.queue,
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_ba(self, _):
        """Process ba command."""
        from openbb_terminal.stocks.behavioural_analysis import ba_controller

        self.queue = self.load_class(
            ba_controller.BehaviouralAnalysisController,
            self.ticker,
            self.start,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command."""
        if self.ticker:
            from openbb_terminal.stocks.quantitative_analysis import qa_controller

            self.queue = self.load_class(
                qa_controller.QaController,
                self.ticker,
                self.start,
                self.interval,
                self.stock,
                self.queue,
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!")

    @log_start_end(log=logger)
    def call_forecast(self, _):
        """Process forecast command."""
        from openbb_terminal.forecast import forecast_controller

        self.queue = self.load_class(
            forecast_controller.ForecastController,
            self.ticker,
            self.stock,
            self.queue,
        )
