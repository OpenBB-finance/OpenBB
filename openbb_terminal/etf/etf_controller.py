"""ETF Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import yfinance as yf
from prompt_toolkit.completion import NestedCompleter
from thepassiveinvestor import create_ETF_report

from openbb_terminal import feature_flags as obbff
from openbb_terminal.common import newsapi_view
from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import (
    financedatabase_view,
    stockanalysis_model,
    stockanalysis_view,
    yfinance_view,
)
from openbb_terminal.etf.discovery import disc_controller
from openbb_terminal.etf.screener import screener_controller
from openbb_terminal.etf.technical_analysis import ta_controller
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative_float,
    check_positive,
    export_data,
    parse_known_args_and_warn,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.comparison_analysis import ca_controller

# pylint: disable=C0415,C0302


logger = logging.getLogger(__name__)


class ETFController(BaseController):
    """ETF Controller class"""

    CHOICES_COMMANDS = [
        "ln",
        "ld",
        "load",
        "overview",
        "holdings",
        "news",
        "candle",
        "pir",
        "weights",
        "summary",
        "compare",
        "resources",
    ]
    CHOICES_MENUS = [
        "ta",
        "pred",
        "ca",
        "scr",
        "disc",
    ]
    PATH = "/etf/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.etf_name = ""
        self.etf_data = ""
        self.etf_holdings: List = list()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        has_ticker_start = "" if self.etf_name else "[unvl]"
        has_ticker_end = "" if self.etf_name else "[/unvl]"
        has_etfs_start = "[unvl]" if len(self.etf_holdings) == 0 else ""
        has_etfs_end = "[/unvl]" if len(self.etf_holdings) == 0 else ""
        help_text = f"""[cmds]
    ln            lookup by name [src][FinanceDatabase/StockAnalysis.com][/src]
    ld            lookup by description [src][FinanceDatabase][/src]
    load          load ETF data [src][Yfinance][/src][/cmds]

[param]Symbol: [/param]{self.etf_name}{has_etfs_start}
[param]Major holdings: [/param]{', '.join(self.etf_holdings)}
[menu]
>   ca            comparison analysis,          e.g.: get similar, historical, correlation, financials{has_etfs_end}
>   disc          discover ETFs,                e.g.: gainers/decliners/active
>   scr           screener ETFs,                e.g.: overview/performance, using preset filters[/menu]
{has_ticker_start}[cmds]
    overview      get overview [src][StockAnalysis][/src]
    holdings      top company holdings [src][StockAnalysis][/src]
    weights       sector weights allocation [src][Yfinance][/src]
    summary       summary description of the ETF [src][Yfinance][/src]
    candle        view a candle chart for ETF
    news          latest news of the company [src][News API][/src]

    pir           create (multiple) passive investor excel report(s) [src][PassiveInvestor][/src]
    compare       compare multiple different ETFs [src][StockAnalysis][/src][/cmds]
[menu]
>   ta            technical analysis,           e.g.: ema, macd, rsi, adx, bbands, obv
>   pred          prediction techniques,        e.g.: regression, arima, rnn, lstm[/menu]
{has_ticker_end}"""
        console.print(text=help_text, menu="ETF")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.etf_name:
            return ["etf", f"load {self.etf_name}"]
        return []

    @log_start_end(log=logger)
    def call_ln(self, other_args: List[str]):
        """Process ln command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ln",
            description="Lookup by name [Source: FinanceDatabase/StockAnalysis.com]",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="Name to look for ETFs",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="fd",
            dest="source",
            help="Name to search for, using either FinanceDatabase (fd) or StockAnalysis (sa) as source.",
            choices=["sa", "fd"],
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            dest="limit",
            help="Limit of ETFs to display",
            default=5,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            name_to_search = " ".join(ns_parser.name)
            if ns_parser.source == "fd":
                financedatabase_view.display_etf_by_name(
                    name=name_to_search,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                )
            elif ns_parser.source == "sa":
                stockanalysis_view.display_etf_by_name(
                    name=name_to_search,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                )
            else:
                console.print("Wrong source choice!\n")

    @log_start_end(log=logger)
    def call_ld(self, other_args: List[str]):
        """Process ld command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ld",
            description="Lookup by description [Source: FinanceDatabase/StockAnalysis.com]",
        )
        parser.add_argument(
            "-d",
            "--description",
            type=str,
            dest="description",
            nargs="+",
            help="Name to look for ETFs",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            dest="limit",
            help="Limit of ETFs to display",
            default=5,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            description_to_search = " ".join(ns_parser.description)
            financedatabase_view.display_etf_by_description(
                description=description_to_search,
                limit=ns_parser.limit,
                export=ns_parser.export,
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
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

            holdings = stockanalysis_model.get_etf_holdings(self.etf_name)
            if holdings.empty:
                console.print("No company holdings found!\n")
            else:
                self.etf_holdings = holdings.index[: ns_parser.limit].tolist()

                if "n/a" in self.etf_holdings:
                    na_tix_idx = []
                    for idx, item in enumerate(self.etf_holdings):
                        if item == "n/a":
                            na_tix_idx.append(str(idx))

                    console.print(
                        f"n/a tickers found at position {','.join(na_tix_idx)}.  Dropping these from holdings.\n"
                    )

                self.etf_holdings = list(
                    filter(lambda x: x != "n/a", self.etf_holdings)
                )

                console.print(
                    f"Top company holdings found: {', '.join(self.etf_holdings)}\n"
                )

            console.print("")

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Get overview data for selected etf",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            stockanalysis_view.view_overview(
                symbol=self.etf_name, export=ns_parser.export
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockanalysis_view.view_holdings(
                symbol=self.etf_name,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_news(self, other_args: List[str]):
        """Process news command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="news",
            description="""
                Prints latest news about ETF, including date, title and web link. [Source: News API]
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
            default=[],
            nargs="+",
            help="Show news only from the sources specified (e.g bbc yahoo.com)",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.etf_name:
                sources = ns_parser.sources
                for idx, source in enumerate(sources):
                    if source.find(".") == -1:
                        sources[idx] += ".com"

                d_stock = yf.Ticker(self.etf_name).info

                newsapi_view.display_news(
                    term=d_stock["shortName"].replace(" ", "+")
                    if "shortName" in d_stock
                    else self.etf_name,
                    num=ns_parser.limit,
                    s_from=ns_parser.n_start_date.strftime("%Y-%m-%d"),
                    show_newest=ns_parser.n_oldest,
                    sources=",".join(sources),
                )
            else:
                console.print("Use 'load <ticker>' prior to this command!", "\n")

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
            help="Choose a column to sort by",
        )
        parser.add_argument(
            "-d",
            "--descending",
            action="store_false",
            dest="descending",
            default=True,
            help="Sort selected column descending",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Shows raw data instead of chart",
        )
        parser.add_argument(
            "-n",
            "--num",
            type=check_positive,
            help="Number to show if raw selected",
            dest="num",
            default=20,
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
            help="Add moving averaged to plot",
            default="",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.etf_name:
                export_data(
                    ns_parser.export,
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "raw_data"
                    ),
                    f"{self.etf_name}",
                    self.etf_data,
                )

                if ns_parser.raw:
                    qa_view.display_raw(
                        df=self.etf_data,
                        sort=ns_parser.sort,
                        des=ns_parser.descending,
                        num=ns_parser.num,
                    )

                else:

                    data = stocks_helper.process_candle(self.etf_data)
                    mov_avgs = (
                        tuple(int(num) for num in ns_parser.mov_avg.split(","))
                        if ns_parser.mov_avg
                        else None
                    )

                    stocks_helper.display_candle(
                        s_ticker=self.etf_name,
                        df_stock=data,
                        use_matplotlib=ns_parser.plotly,
                        intraday=False,
                        add_trend=ns_parser.trendlines,
                        ma=mov_avgs,
                        asset_type="ETF",
                    )
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")

    @log_start_end(log=logger)
    def call_pir(self, other_args):
        """Process pir command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pir",
            description="Create passive investor ETF excel report which contains most of the important metrics "
            "about an ETF obtained from Yahoo Finnace. You are able to input any ETF ticker you like "
            "within the command to create am extensive report",
        )
        parser.add_argument(
            "-e",
            "--etfs",
            nargs="+",
            type=str,
            dest="names",
            help="Symbols to create a report for (e.g. pir ARKW ARKQ QQQ VOO)",
            default=[self.etf_name],
        )
        parser.add_argument(
            "--filename",
            default=f"ETF_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            dest="filename",
            help="Filename of the excel ETF report",
        )
        parser.add_argument(
            "--folder",
            default=os.path.dirname(os.path.abspath(__file__)).replace(
                "openbb_terminal", "exports"
            ),
            dest="folder",
            help="Folder where the excel ETF report will be saved",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.names:
                create_ETF_report(
                    ns_parser.names,
                    filename=ns_parser.filename,
                    folder=ns_parser.folder,
                )
                console.print(
                    f"Created ETF report as {ns_parser.filename} in folder {ns_parser.folder} \n"
                )

    @log_start_end(log=logger)
    def call_weights(self, other_args: List[str]):
        """Process weights command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="weights",
            description="Look at ETF sector holdings",
        )
        parser.add_argument(
            "-m",
            "--min",
            type=check_non_negative_float,
            dest="min",
            help="Minimum positive float to display sector",
            default=5,
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            yfinance_view.display_etf_weightings(
                name=self.etf_name,
                raw=ns_parser.raw,
                min_pct_to_display=ns_parser.min,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="summary",
            description="Print ETF description summary",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
        )
        if ns_parser:
            yfinance_view.display_etf_description(
                name=self.etf_name,
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
            console.print("Use 'load <ticker>' prior to this command!", "\n")

    @log_start_end(log=logger)
    def call_pred(self, _):
        """Process pred command"""
        if obbff.ENABLE_PREDICT:
            if self.etf_name:
                try:
                    from openbb_terminal.etf.prediction_techniques import (
                        pred_controller,
                    )

                    self.queue = self.load_class(
                        pred_controller.PredictionTechniquesController,
                        self.etf_name,
                        self.etf_data.index[0],
                        "1440min",
                        self.etf_data,
                        self.queue,
                    )

                except ModuleNotFoundError as e:
                    logger.exception(
                        "One of the optional packages seems to be missing: %s", str(e)
                    )
                    console.print(
                        "One of the optional packages seems to be missing: ",
                        e,
                        "\n",
                    )
            else:
                console.print("Use 'load <ticker>' prior to this command!", "\n")
        else:
            console.print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Process ca command"""
        if len(self.etf_holdings) > 0:
            self.queue = ca_controller.ComparisonAnalysisController(
                self.etf_holdings, self.queue
            ).menu(custom_path_menu_above="/stocks/")
        else:
            console.print(
                "Load a ticker with major holdings to compare them on this menu\n"
            )

    @log_start_end(log=logger)
    def call_scr(self, _):
        """Process scr command"""
        self.queue = self.load_class(screener_controller.ScreenerController, self.queue)

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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            etf_list = ns_parser.names.upper().split(",")
            stockanalysis_view.view_comparisons(etf_list, export=ns_parser.export)
