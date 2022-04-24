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
    parse_known_args_and_warn,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper

import i18n

# pylint: disable=R1710,import-outside-toplevel,R0913,R1702

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
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.ticker and self.start:
            stock_text = (
                f"{s_intraday} {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            stock_text = f"{s_intraday} {self.ticker}"
        has_ticker_start = "" if self.ticker else "[unvl]"
        has_ticker_end = "" if self.ticker else "[/unvl]"
        help_text = f"""[cmds]
    search      {i18n.t('stocks/search')}
    load        {i18n.t('stocks/load')}[/cmds][param]

Stock: [/param]{stock_text}
{self.add_info}[cmds]
    quote       {i18n.t('stocks/quote')}
    candle      {i18n.t('stocks/candle')}
    news        {i18n.t('stocks/news')}[/cmds] [src][News API][/src]
[menu]
>   options     {i18n.t('stocks/options')}
>   disc        {i18n.t('stocks/disc')}
>   sia         {i18n.t('stocks/sia')}
>   dps         {i18n.t('stocks/dps')}
>   scr         {i18n.t('stocks/scr')}
>   ins         {i18n.t('stocks/ins')}
>   gov         {i18n.t('stocks/gov')}
>   ba          {i18n.t('stocks/ba')}
>   ca          {i18n.t('stocks/ca')}{has_ticker_start}
>   fa          {i18n.t('stocks/fa')}
>   res         {i18n.t('stocks/res')}
>   dd          {i18n.t('stocks/dd')}
>   bt          {i18n.t('stocks/bt')}
>   ta          {i18n.t('stocks/ta')}
>   qa          {i18n.t('stocks/qa')}
>   pred        {i18n.t('stocks/pred')}
{has_ticker_end}"""
        console.print(text=help_text, menu="Stocks")

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
            description=f"{i18n.t('stocks/search_')}.",
        )
        parser.add_argument(
            "-q",
            "--query",
            action="store",
            dest="query",
            type=str.lower,
            default="",
            help=f"{i18n.t('stocks/search_query')}.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=0,
            type=int,
            dest="limit",
            help=f"{i18n.t('stocks/search_limit')}.",
        )
        parser.add_argument(
            "-c",
            "--country",
            default="",
            choices=self.country,
            dest="country",
            help=f"{i18n.t('stocks/search_country')}.",
        )
        parser.add_argument(
            "-s",
            "--sector",
            default="",
            choices=self.sector,
            dest="sector",
            help=f"{i18n.t('stocks/search_sector')}.",
        )
        parser.add_argument(
            "-i",
            "--industry",
            default="",
            choices=self.industry,
            dest="industry",
            help=f"{i18n.t('stocks/search_industry')}.",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            default="",
            choices=list(stocks_helper.market_coverage_suffix.keys()),
            dest="exchange_country",
            help=f"{i18n.t('stocks/search_exchange')}.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
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
            description=f"{i18n.t('stocks/quote_')}.",
        )
        if self.ticker:
            parser.add_argument(
                "-t",
                "--ticker",
                action="store",
                dest="s_ticker",
                default=ticker,
                help=f"{i18n.t('stocks/quote_ticker')}.",
            )
        else:
            parser.add_argument(
                "-t",
                "--ticker",
                action="store",
                dest="s_ticker",
                required="-h" not in other_args,
                help=f"{i18n.t('stocks/quote_ticker')}.",
            )
        # For the case where a user uses: 'quote BB'
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            stocks_helper.quote(ticker)

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description=f"{i18n.t('stocks/candle_')}.",
        )
        parser.add_argument(
            "-p",
            "--plotly",
            dest="plotly",
            action="store_false",
            default=True,
            help=f"{i18n.t('stocks/candle_plotly')}.",
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
            help=f"{i18n.t('stocks/candle_sort')}.",
        )
        parser.add_argument(
            "-d",
            "--descending",
            action="store_false",
            dest="descending",
            default=True,
            help=f"{i18n.t('stocks/candle_descending')}.",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help=f"{i18n.t('stocks/candle_raw')}.",
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store_true",
            default=False,
            help=f"{i18n.t('stocks/candle_trend')}.",
            dest="trendlines",
        )
        parser.add_argument(
            "--ma",
            dest="mov_avg",
            type=str,
            help=f"{i18n.t('stocks/candle_mov_avg')}.",
            default=None,
        )
        ns_parser = parse_known_args_and_warn(
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
                        num=ns_parser.num,
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
            description=f"{i18n.t('stocks/news_')}.",
        )
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="n_start_date",
            type=valid_date,
            default=datetime.now() - timedelta(days=7),
            help=f"{i18n.t('stocks/news_date')}.",
        )
        parser.add_argument(
            "-o",
            "--oldest",
            action="store_false",
            dest="n_oldest",
            default=True,
            help=f"{i18n.t('stocks/news_date')}.",
        )
        parser.add_argument(
            "-s",
            "--sources",
            dest="sources",
            default=[],
            nargs="+",
            help=f"{i18n.t('stocks/news_sources')}.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args, limit=5)
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
            if self.interval == "1440min":
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
            else:
                console.print("Load daily data to use this menu!", "\n")
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
