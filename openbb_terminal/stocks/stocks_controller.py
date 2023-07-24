"""Stock Context Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import financedatabase as fd

from openbb_terminal import config_terminal
from openbb_terminal.common import (
    feedparser_view,
    newsapi_view,
    ultima_newsmonitor_view,
)
from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    export_data,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks import cboe_view, stocks_helper, stocks_view
from openbb_terminal.terminal_helper import suppress_stdout

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
        "dd",
        "fa",
        "bt",
        "ca",
        "options",
        "th",
        "forecast",
    ]

    PATH = "/stocks/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    try:
        stocks_options = fd.obtain_options("equities")
        country = stocks_options["country"].tolist()
        sector = stocks_options["sector"].tolist()
        industry_group = stocks_options["industry_group"].tolist()
        industry = stocks_options["industry"].tolist()
        exchange = stocks_options["exchange"].tolist()
    except Exception:
        country, sector, industry_group, industry, exchange = {}, {}, {}, {}, {}
        console.print(
            "[red]Note: Some datasets from GitHub failed to load. This means that the `search` command will not work. "
            "If other commands are failing please check your internet connection or communicate with your "
            "IT department that certain websites are blocked.[/red] \n"
        )

    TOB_EXCHANGES = ["BZX", "EDGX", "BYX", "EDGA"]
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct stocks controller."""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
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
        mt.add_menu("dps")
        mt.add_menu("scr")
        mt.add_menu("ins")
        mt.add_menu("gov")
        mt.add_menu("ba")
        mt.add_menu("ca")
        mt.add_menu("fa")
        mt.add_menu("bt")
        mt.add_menu("ta")
        mt.add_menu("qa")
        mt.add_menu("forecast")
        mt.add_menu("res", self.ticker)

        console.print(text=mt.menu_text, menu="Stocks")

    def custom_reset(self):
        """Class specific component of reset command."""
        if self.ticker:
            return ["stocks", f"load {self.ticker}"]
        return []

    def custom_load_wrapper(self, other_args: List[str]):
        """Class specific component of load command"""
        with suppress_stdout():
            self.call_load(other_args)

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Show companies matching the search query, country, sector, industry and/or exchange. "
            "Note that by default only the United States exchanges are searched which tend to contain the most "
            "extensive data for each company. To search all exchanges use the --all-exchanges flag.",
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
            "--industrygroup",
            default="",
            choices=stocks_helper.format_parse_choices(self.industry_group),
            type=str.lower,
            metavar="industry_group",
            dest="industry_group",
            help="Search by industry group to find stocks matching the criteria",
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
            choices=stocks_helper.format_parse_choices(self.exchange),
            type=str.lower,
            metavar="exchange",
            dest="exchange",
            help="Search by a specific exchange to find stocks matching the criteria",
        )
        parser.add_argument(
            "--exchangecountry",
            default="",
            choices=stocks_helper.format_parse_choices(
                list(stocks_helper.market_coverage_suffix.keys())
            ),
            type=str.lower,
            metavar="exchange_country",
            dest="exchange_country",
            help="Search by a specific country and all its exchanges to find stocks matching the criteria",
        )
        parser.add_argument(
            "-a",
            "--all-exchanges",
            default=False,
            action="store_true",
            dest="all_exchanges",
            help="Whether to search all exchanges, without this option only the United States market is searched.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")
        if ns_parser := self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        ):
            # Mapping
            sector = stocks_helper.map_parse_choices(self.sector)[ns_parser.sector]
            industry = stocks_helper.map_parse_choices(self.industry)[
                ns_parser.industry
            ]
            industry_group = stocks_helper.map_parse_choices(self.industry_group)[
                ns_parser.industry_group
            ]
            exchange = stocks_helper.map_parse_choices(self.exchange)[
                ns_parser.exchange
            ]
            exchange_country = stocks_helper.map_parse_choices(
                list(stocks_helper.market_coverage_suffix.keys())
            )[ns_parser.exchange_country]

            stocks_helper.search(
                query=" ".join(ns_parser.query),
                country=ns_parser.country,
                sector=sector,
                industry_group=industry_group,
                industry=industry,
                exchange=exchange,
                exchange_country=exchange_country,
                all_exchanges=ns_parser.all_exchanges,
                limit=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_tob(self, other_args: List[str]):
        """Process tob command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tob",
            description="Get top of book for loaded ticker from selected exchange",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="s_ticker",
            required=all(x not in other_args for x in ["-h", "--help"])
            and not self.ticker,
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

        if not self.ticker and other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        if ns_parser := self.parse_known_args_and_warn(parser, other_args):
            ticker = ns_parser.s_ticker or self.ticker
            cboe_view.display_top_of_book(ticker, ns_parser.exchange)

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process quote command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Current quote for the loaded stock ticker.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="s_ticker",
            required=False,
            default=self.ticker,
            help="Get a quote for a specific ticker, or comma-separated list of tickers.",
        )

        # For the case where a user uses: 'quote BB'
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            tickers = ns_parser.s_ticker.split(",")
            if ns_parser.s_ticker and len(tickers) == 1:
                self.ticker = ns_parser.s_ticker
                self.custom_load_wrapper([self.ticker])

            stocks_view.display_quote(
                tickers,
                ns_parser.export,
                " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
            )

    @log_start_end(log=logger)
    def call_codes(self, _):
        """Process codes command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="codes",
            description="Show CIK, FIGI and SCI code from polygon for loaded ticker.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(parser, _)
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
            if self.ticker:
                stocks_helper.show_codes_polygon(self.ticker)
                self.custom_load_wrapper([self.ticker])
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Shows historic price and volume for the asset.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze.",
            type=str,
            default=None,
            required=not any(x in other_args for x in ["-h", "--help"])
            and not self.ticker,
        )
        parser.add_argument(
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only works for intraday data.",
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
            help="Shows raw data instead of a chart.",
        )
        parser.add_argument(
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
            default=None,
        )
        parser.add_argument(
            "--ha",
            dest="ha",
            action="store_true",
            default=False,
            help="Flag to show Heikin Ashi candles.",
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
        if config_terminal.HOLD:
            console.print("[red]Hold functionality not supported with candle.[/]")
            return

        if ns_parser:
            figure_export = None
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
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

                    figure_export = stocks_helper.display_candle(
                        symbol=self.ticker,
                        data=data,
                        add_trend=ns_parser.trendlines,
                        ma=mov_avgs,
                        ha=ns_parser.ha,
                        prepost=ns_parser.prepost,
                        asset_type="",
                        yscale="log" if ns_parser.logy else "linear",
                        external_axes=ns_parser.is_image,
                    )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{self.ticker}",
                    self.stock,
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
                    figure=figure_export,
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
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required=not any(x in other_args for x in ["-h", "--help"])
            and not self.ticker,
            help="Ticker to get data for",
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
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if self.ticker:
                if ns_parser.source == "NewsApi":
                    newsapi_view.display_news(
                        query=self.ticker,
                        limit=ns_parser.limit,
                        start_date=ns_parser.n_start_date.strftime("%Y-%m-%d"),
                        show_newest=ns_parser.n_oldest,
                        sources=ns_parser.sources,
                    )
                elif str(ns_parser.source).lower() == "ultima":
                    query = str(self.ticker).upper()
                    if query not in ultima_newsmonitor_view.supported_terms():
                        console.print(
                            "[red]Ticker not supported by Ultima Insights News Monitor. Falling back to default.\n[/red]"
                        )
                        feedparser_view.display_news(
                            term=query,
                            sources=ns_parser.sources,
                            limit=ns_parser.limit,
                            export=ns_parser.export,
                            sheet_name=ns_parser.sheet_name,
                        )
                    else:
                        ultima_newsmonitor_view.display_news(
                            term=query,
                            sources=ns_parser.sources,
                            limit=ns_parser.limit,
                            export=ns_parser.export,
                            sheet_name=ns_parser.sheet_name,
                        )
                elif ns_parser.source == "Feedparser":
                    feedparser_view.display_news(
                        term=self.ticker,
                        sources=ns_parser.sources,
                        limit=ns_parser.limit,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
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
        """Process sia command."""
        # from openbb_terminal.stocks.sector_industry_analysis.sia_controller import (
        #     SectorIndustryAnalysisController,
        # )

        # self.queue = self.load_class(
        #     SectorIndustryAnalysisController, self.ticker, self.queue
        # )

        # TODO: Make the call_sia command available again after improving the functionality
        # TODO: Update test_stocks_controller.py to reflect the changes

        console.print(
            "The sia (Sector & Industry Analysis) menu is currently inactive as the functionality is "
            "better represented through the stocks/ca, stocks/fa and routines functionalities. "
            "Improvements to this menu is on the projects list."
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

        # TODO: Get rid of the call_dd on the next release since it has been deprecated.

        console.print(
            "The dd (Due Diligence) menu has been integrated into the fa (Fundamental Analysis) menu. "
            "Please use this menu instead.\n"
        )

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Process ca command."""
        from openbb_terminal.stocks.comparison_analysis import ca_controller

        self.queue = self.load_class(
            ca_controller.ComparisonAnalysisController,
            [f"{self.ticker}"] if self.ticker else "",
            self.queue,
        )

    @log_start_end(log=logger)
    def call_fa(self, _):
        """Process fa command."""
        from openbb_terminal.stocks.fundamental_analysis import fa_controller

        self.queue = self.load_class(
            fa_controller.FundamentalAnalysisController,
            self.ticker,
            self.start,
            self.interval,
            self.stock,
            self.suffix,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_bt(self, _):
        """Process bt command."""
        from openbb_terminal.stocks.backtesting import bt_controller

        self.queue = self.load_class(
            bt_controller.BacktestingController, self.ticker, self.stock, self.queue
        )

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command."""
        from openbb_terminal.stocks.technical_analysis import ta_controller

        self.queue = self.load_class(
            ta_controller.TechnicalAnalysisController,
            self.ticker,
            self.start,
            self.interval,
            self.stock,
            self.queue,
        )

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
        from openbb_terminal.stocks.quantitative_analysis import qa_controller

        self.queue = self.load_class(
            qa_controller.QaController,
            self.ticker,
            self.start,
            self.interval,
            self.stock,
            self.queue,
        )

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
