"""Stock Context Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import financedatabase
import yfinance as yf
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.common import newsapi_view
from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.decorators import log_start_end

from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    export_data,
    valid_date,
)
from openbb_terminal.helper_classes import AllowArgsWithWhiteSpace
from openbb_terminal.helper_funcs import choice_check_after_action
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import console, translate, MenuText
from openbb_terminal.stocks import stocks_helper

# pylint: disable=R1710,import-outside-toplevel,R0913,R1702,no-member

logger = logging.getLogger(__name__)


class StocksController(StockBaseController):
    """Stocks Controller class"""

    CHOICES_COMMANDS = [
        "search",
        "load",
        "quote",
        "candle",
        "news",
        "resources",
        "codes",
    ]
    CHOICES_MENUS = [
        "ta",
        "ba",
        "qa",
        "pred",
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
    ]

    PATH = "/stocks/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    country = financedatabase.show_options("equities", "countries")
    sector = financedatabase.show_options("equities", "sectors")
    industry = financedatabase.show_options("equities", "industries")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:

            choices: dict = {c: {} for c in self.controller_choices}

            choices["search"]["--country"] = {c: None for c in self.country}
            choices["search"]["-c"] = {c: None for c in self.country}
            choices["search"]["--sector"] = {c: None for c in self.sector}
            choices["search"]["-s"] = {c: None for c in self.sector}
            choices["search"]["--industry"] = {c: None for c in self.industry}
            choices["search"]["-i"] = {c: None for c in self.industry}
            choices["search"]["--exchange"] = {
                c: None for c in stocks_helper.market_coverage_suffix
            }
            choices["search"]["-e"] = {
                c: None for c in stocks_helper.market_coverage_suffix
            }

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        stock_text = ""
        if self.ticker:
            s_intraday = (f"Intraday {self.interval}", "Daily")[
                self.interval == "1440min"
            ]
            if self.start:
                stock_text = f"{s_intraday} {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            else:
                stock_text = f"{s_intraday} {self.ticker}"

        mt = MenuText("stocks/", 80)
        mt.add_cmd("search")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", stock_text)
        mt.add_raw(self.add_info)
        mt.add_raw("\n")
        mt.add_cmd("quote", "", self.ticker)
        mt.add_cmd("candle", "", self.ticker)
        mt.add_cmd("news", "News API", self.ticker)
        mt.add_cmd("codes", "Polygon", self.ticker)
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
        mt.add_menu("pred", self.ticker)
        console.print(text=mt.menu_text, menu="Stocks")

    def custom_reset(self):
        """Class specific component of reset command"""
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
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description=translate("stocks/SEARCH"),
        )
        parser.add_argument(
            "-q",
            "--query",
            action="store",
            dest="query",
            type=str.lower,
            default="",
            help=translate("stocks/SEARCH_query"),
        )
        parser.add_argument(
            "-c",
            "--country",
            default="",
            nargs=argparse.ONE_OR_MORE,
            action=choice_check_after_action(AllowArgsWithWhiteSpace, self.country),
            dest="country",
            help=translate("stocks/SEARCH_country"),
        )
        parser.add_argument(
            "-s",
            "--sector",
            default="",
            nargs=argparse.ONE_OR_MORE,
            action=choice_check_after_action(AllowArgsWithWhiteSpace, self.sector),
            dest="sector",
            help=translate("stocks/SEARCH_sector"),
        )
        parser.add_argument(
            "-i",
            "--industry",
            default="",
            nargs=argparse.ONE_OR_MORE,
            action=choice_check_after_action(AllowArgsWithWhiteSpace, self.industry),
            dest="industry",
            help=translate("stocks/SEARCH_industry"),
        )
        parser.add_argument(
            "-e",
            "--exchange",
            default="",
            choices=list(stocks_helper.market_coverage_suffix.keys()),
            dest="exchange_country",
            help=translate("stocks/SEARCH_exchange"),
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
            stocks_helper.search(
                query=ns_parser.query,
                country=ns_parser.country,
                sector=ns_parser.sector,
                industry=ns_parser.industry,
                exchange_country=ns_parser.exchange_country,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        ticker = self.ticker + "." + self.suffix if self.suffix else self.ticker
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description=translate("stocks/QUOTE"),
        )
        if self.ticker:
            parser.add_argument(
                "-t",
                "--ticker",
                action="store",
                dest="s_ticker",
                default=ticker,
                help=translate("stocks/QUOTE_ticker"),
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
            stocks_helper.quote(ns_parser.s_ticker)

    @log_start_end(log=logger)
    def call_codes(self, _):
        """Process codes command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="codes",
            description="Show CIK, FIGI and SCI code from polygon for loaded ticker.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, _)
        if ns_parser:
            if not self.ticker:
                console.print("No ticker loaded. First use `load {ticker}`\n")
                return
            stocks_helper.show_codes_polygon(self.ticker)

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description=translate("stocks/CANDLE"),
        )
        parser.add_argument(
            "-p",
            "--plotly",
            dest="plotly",
            action="store_false",
            default=True,
            help=translate("stocks/CANDLE_plotly"),
        )
        parser.add_argument(
            "--sort",
            choices=[
                "AdjClose",
                "Open",
                "Close",
                "High",
                "Low",
                "Volume",
                "Returns",
                "LogRet",
            ],
            default="",
            type=str,
            dest="sort",
            help=translate("stocks/CANDLE_sort"),
        )
        parser.add_argument(
            "-d",
            "--descending",
            action="store_false",
            dest="descending",
            default=True,
            help=translate("stocks/CANDLE_descending"),
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help=translate("stocks/CANDLE_raw"),
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store_true",
            default=False,
            help=translate("stocks/CANDLE_trend"),
            dest="trendlines",
        )
        parser.add_argument(
            "--ma",
            dest="mov_avg",
            type=str,
            help=translate("stocks/CANDLE_mov_avg"),
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=20,
        )
        if ns_parser:
            if self.ticker:
                export_data(
                    ns_parser.export,
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "raw_data"
                    ),
                    f"{self.ticker}",
                    self.stock,
                )

                if ns_parser.raw:
                    qa_view.display_raw(
                        df=self.stock,
                        sort=ns_parser.sort,
                        des=ns_parser.descending,
                        num=ns_parser.limit,
                    )

                else:
                    data = stocks_helper.process_candle(self.stock)
                    mov_avgs = []

                    if ns_parser.mov_avg:
                        mov_list = (num for num in ns_parser.mov_avg.split(","))

                        for num in mov_list:
                            try:
                                mov_avgs.append(int(num))
                            except ValueError:
                                console.print(
                                    f"{num} is not a valid moving average, must be integer"
                                )

                    stocks_helper.display_candle(
                        s_ticker=self.ticker,
                        df_stock=data,
                        use_matplotlib=ns_parser.plotly,
                        intraday=self.interval != "1440min",
                        add_trend=ns_parser.trendlines,
                        ma=mov_avgs,
                    )
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")

    @log_start_end(log=logger)
    def call_news(self, other_args: List[str]):
        """Process news command"""
        if not self.ticker:
            console.print("Use 'load <ticker>' prior to this command!", "\n")
            return
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="news",
            description=translate("stocks/NEWS"),
        )
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="n_start_date",
            type=valid_date,
            default=datetime.now() - timedelta(days=7),
            help=translate("stocks/NEWS_date"),
        )
        parser.add_argument(
            "-o",
            "--oldest",
            action="store_false",
            dest="n_oldest",
            default=True,
            help=translate("stocks/NEWS_oldest"),
        )
        parser.add_argument(
            "-s",
            "--sources",
            dest="sources",
            default=[],
            nargs="+",
            help=translate("stocks/NEWS_sources"),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args, limit=3)
        if ns_parser:
            sources = ns_parser.sources
            for idx, source in enumerate(sources):
                if source.find(".") == -1:
                    sources[idx] += ".com"

            d_stock = yf.Ticker(self.ticker).info

            newsapi_view.display_news(
                term=d_stock["shortName"].replace(" ", "+")
                if "shortName" in d_stock
                else self.ticker,
                num=ns_parser.limit,
                s_from=ns_parser.n_start_date.strftime("%Y-%m-%d"),
                show_newest=ns_parser.n_oldest,
                sources=",".join(sources),
            )

    @log_start_end(log=logger)
    def call_disc(self, _):
        """Process disc command"""
        from openbb_terminal.stocks.discovery.disc_controller import (
            DiscoveryController,
        )

        self.queue = self.load_class(DiscoveryController, self.queue)

    @log_start_end(log=logger)
    def call_dps(self, _):
        """Process dps command"""
        from openbb_terminal.stocks.dark_pool_shorts.dps_controller import (
            DarkPoolShortsController,
        )

        self.queue = self.load_class(
            DarkPoolShortsController, self.ticker, self.start, self.stock, self.queue
        )

    @log_start_end(log=logger)
    def call_scr(self, _):
        """Process scr command"""
        from openbb_terminal.stocks.screener.screener_controller import (
            ScreenerController,
        )

        self.queue = self.load_class(ScreenerController, self.queue)

    @log_start_end(log=logger)
    def call_sia(self, _):
        """Process ins command"""
        from openbb_terminal.stocks.sector_industry_analysis.sia_controller import (
            SectorIndustryAnalysisController,
        )

        self.queue = self.load_class(
            SectorIndustryAnalysisController, self.ticker, self.queue
        )

    @log_start_end(log=logger)
    def call_ins(self, _):
        """Process ins command"""
        from openbb_terminal.stocks.insider.insider_controller import (
            InsiderController,
        )

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
        """Process gov command"""
        from openbb_terminal.stocks.government.gov_controller import GovController

        self.queue = self.load_class(GovController, self.ticker, self.queue)

    @log_start_end(log=logger)
    def call_options(self, _):
        """Process options command"""
        from openbb_terminal.stocks.options.options_controller import (
            OptionsController,
        )

        self.queue = self.load_class(OptionsController, self.ticker, self.queue)

    @log_start_end(log=logger)
    def call_th(self, _):
        """Process th command"""
        from openbb_terminal.stocks.tradinghours import tradinghours_controller

        self.queue = self.load_class(
            tradinghours_controller.TradingHoursController,
            self.ticker,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_res(self, _):
        """Process res command"""
        if self.ticker:
            from openbb_terminal.stocks.research.res_controller import (
                ResearchController,
            )

            self.queue = self.load_class(
                ResearchController, self.ticker, self.start, self.interval, self.queue
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_dd(self, _):
        """Process dd command"""
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
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Process ca command"""

        from openbb_terminal.stocks.comparison_analysis import ca_controller

        self.queue = self.load_class(
            ca_controller.ComparisonAnalysisController,
            [self.ticker] if self.ticker else "",
            self.queue,
        )

    @log_start_end(log=logger)
    def call_fa(self, _):
        """Process fa command"""
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
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_bt(self, _):
        """Process bt command"""
        if self.ticker:
            from openbb_terminal.stocks.backtesting import bt_controller

            self.queue = self.load_class(
                bt_controller.BacktestingController, self.ticker, self.stock, self.queue
            )
        else:
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command"""
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
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_ba(self, _):
        """Process ba command"""
        from openbb_terminal.stocks.behavioural_analysis import ba_controller

        self.queue = self.load_class(
            ba_controller.BehaviouralAnalysisController,
            self.ticker,
            self.start,
            self.queue,
        )

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command"""
        if self.ticker:
            from openbb_terminal.stocks.quantitative_analysis import (
                qa_controller,
            )

            self.queue = self.load_class(
                qa_controller.QaController,
                self.ticker,
                self.start,
                self.interval,
                self.stock,
                self.queue,
            )
        # TODO: This menu should work regardless of data being daily or not!
        # James: 5/27 I think it does now
        else:
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_pred(self, _):
        """Process pred command"""
        if obbff.ENABLE_PREDICT:
            if self.ticker:
                if self.interval == "1440min":
                    try:
                        from openbb_terminal.stocks.prediction_techniques import (
                            pred_controller,
                        )

                        self.queue = self.load_class(
                            pred_controller.PredictionTechniquesController,
                            self.ticker,
                            self.start,
                            self.interval,
                            self.stock,
                            self.queue,
                        )
                    except ModuleNotFoundError as e:
                        logger.exception(
                            "One of the optional packages seems to be missing: %s",
                            str(e),
                        )
                        console.print(
                            "One of the optional packages seems to be missing: ",
                            e,
                            "\n",
                        )

                # TODO: This menu should work regardless of data being daily or not!
                else:
                    console.print("Load daily data to use this menu!", "\n")
            else:
                console.print("Use 'load <ticker>' prior to this command!", "\n")
        else:
            console.print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )
