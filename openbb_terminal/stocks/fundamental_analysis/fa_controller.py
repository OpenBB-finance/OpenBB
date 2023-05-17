"""Fundamental Analysis Controller."""
__docformat__ = "numpy"
import argparse
import logging
from datetime import datetime
from typing import List, Optional

from pandas.core.frame import DataFrame

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    list_from_str,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console, get_ordered_list_sources
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.fundamental_analysis import (
    av_view,
    business_insider_view,
    csimarket_view,
    dcf_view,
    eclect_us_view,
    eodhd_view,
    finnhub_view,
    finviz_view,
    fmp_view,
    marketwatch_view,
    nasdaq_model,
    nasdaq_view,
    polygon_view,
    seeking_alpha_view,
    yahoo_finance_view,
)
from openbb_terminal.terminal_helper import suppress_stdout

# pylint: disable=inconsistent-return-statements,C0302,R0904


logger = logging.getLogger(__name__)

no_ticker_message = (
    "No ticker loaded. Use 'load' command to load a ticker or use the -t flag."
)


class FundamentalAnalysisController(StockBaseController):
    """Fundamental Analysis Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "analysis",
        "score",
        "mktcap",
        "metrics",
        "ratios",
        "growth",
        "revfc",
        "epsfc",
        "warnings",
        "income",
        "balance",
        "cash",
        "mgmt",
        "splits",
        "shrs",
        "overview",
        "income",
        "balance",
        "cash",
        "divs",
        "earnings",
        "fraud",
        "dcf",
        "dcfc",
        "dupont",
        "sec",
        "rating",
        "pt",
        "rot",
        "est",
        "supplier",
        "customer",
    ]

    PATH = "/stocks/fa/"

    SHRS_CHOICES = ["major", "institutional", "mutualfund"]
    ESTIMATE_CHOICES = ["annual_earnings", "quarter_earnings", "quarter_revenues"]
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: DataFrame,
        suffix: str = "",
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = f"{ticker}.{suffix}" if suffix else ticker
        self.start = start
        self.interval = interval
        self.suffix = suffix
        self.stock = stock

        self.default_income = get_ordered_list_sources(f"{self.PATH}income")[0]
        self.default_balance = get_ordered_list_sources(f"{self.PATH}balance")[0]
        self.default_cash = get_ordered_list_sources(f"{self.PATH}cash")[0]

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("stocks/fa/")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker.upper())
        mt.add_raw("\n")
        mt.add_info("_company_overview")
        mt.add_cmd("mktcap", not self.stock.empty)
        mt.add_cmd("overview", not self.stock.empty)
        mt.add_cmd("divs", not self.suffix and not self.stock.empty)
        mt.add_cmd("splits", not self.suffix and not self.stock.empty)
        mt.add_cmd("rating", not self.stock.empty)
        mt.add_cmd("rot", not self.stock.empty)
        mt.add_cmd("score", not self.stock.empty)
        mt.add_cmd("warnings", not self.stock.empty)
        mt.add_raw("\n")
        mt.add_info("_management_shareholders")
        mt.add_cmd("mgmt", not self.stock.empty)
        mt.add_cmd("shrs", not self.suffix and not self.stock.empty)
        mt.add_cmd("supplier", not self.stock.empty)
        mt.add_cmd("customer", not self.stock.empty)
        mt.add_raw("\n")
        mt.add_info("_financial_statements")
        mt.add_cmd("income", not self.stock.empty)
        mt.add_cmd("balance", not self.stock.empty)
        mt.add_cmd("cash", not self.stock.empty)
        mt.add_cmd("growth", not self.stock.empty)
        mt.add_cmd("metrics", not self.stock.empty)
        mt.add_cmd("ratios", not self.stock.empty)
        mt.add_cmd("dupont", not self.stock.empty)
        mt.add_cmd("fraud", not self.stock.empty)
        mt.add_cmd("sec", not self.stock.empty)
        mt.add_cmd("analysis", not self.stock.empty)
        mt.add_raw("\n")
        mt.add_info("_future_estimations")
        mt.add_cmd("earnings", not self.stock.empty)
        mt.add_cmd("epsfc", not self.stock.empty)
        mt.add_cmd("revfc", not self.stock.empty)
        mt.add_cmd("est", not self.stock.empty)
        mt.add_cmd("pt", not self.stock.empty)
        mt.add_cmd("dcf", not self.stock.empty)
        mt.add_cmd("dcfc", not self.stock.empty)
        console.print(text=mt.menu_text, menu="Stocks - Fundamental Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.suffix:
                return ["stocks", f"load {self.ticker}.{self.suffix}", "fa"]
            return ["stocks", f"load {self.ticker}", "fa"]
        return []

    def custom_load_wrapper(self, other_args: List[str]):
        """Class specific component of load command"""
        with suppress_stdout():
            self.call_load(other_args)

    @log_start_end(log=logger)
    def call_analysis(self, other_args: List[str]):
        """Process analysis command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="analysis",
            description="""Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return
            eclect_us_view.display_analysis(
                symbol=self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_mgmt(self, other_args: List[str]):
        """Process mgmt command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mgmt",
            description="""
                Print management team. Namely: Name, Title, and Information from google
                [Source: Business Insider]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return
            business_insider_view.display_management(
                symbol=self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
                Prints information about, among other things, the industry, sector exchange and company description.
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return
            if ns_parser.source == "Finviz":
                finviz_view.display_screen_data(
                    symbol=self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_info(
                    self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "AlphaVantage":
                av_view.display_overview(
                    self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_profile(
                    self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_score(self, other_args: List[str]):
        """Process score command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="score",
            description="""
                Value investing tool based on Warren Buffett, Joseph Piotroski
                and Benjamin Graham thoughts [Source: FMP]
                """,
        )
        parser.add_argument(
            "-y",
            "--years",
            type=int,
            default=10,
            dest="years",
            help="Define the amount of years required to calculate the score.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return
            fmp_view.valinvest_score(
                self.ticker,
                ns_parser.years,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_mktcap(self, other_args: List[str]):
        """Process enterprise command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mktcap",
            description="""
                    Prints stock price, number of shares, market capitalization and
                    enterprise value over time. The following fields are expected: Add total debt,
                    Enterprise value, Market capitalization, Minus cash and cash equivalents, Number
                    of shares, Stock price, and Symbol. [Source: Financial Modeling Prep]
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default="1900-01-01",
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the enterprise value to display. ",
        )

        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now(),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the enterprise value to display. ",
        )

        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )

        parser.add_argument(
            "-m",
            "--method",
            default="market_cap",
            type=str,
            dest="method",
            choices=["enterprise_value", "market_cap"],
            help="Define the data to display.",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, raw=True
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_enterprise(
                    symbol=self.ticker,
                    start_date=ns_parser.start,
                    end_date=ns_parser.end,
                    quarterly=ns_parser.b_quarter,
                    method=ns_parser.method,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                if ns_parser.method == "enterprise_value":
                    console.print("YahooFinance only has market cap data.")

                yahoo_finance_view.display_mktcap(
                    self.ticker,
                    start_date=ns_parser.start,
                    end_date=ns_parser.end,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_metrics(self, other_args: List[str]):
        """Process metrics command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metrics",
            description="""
                    Prints a list of the key metrics of a company over time. This can be either
                    quarterly or annually. This includes, among other things, Return on Equity (ROE),
                    Working Capital, Current Ratio and Debt to Assets. The following fields are expected:
                    Average inventory, Average payables, Average receivables, Book value per share, Capex
                    per share, Capex to depreciation, Capex to operating cash flow, Capex to revenue, Cash
                    per share, Current ratio, Days of inventory on hand, Days payables outstanding, Days
                    sales outstanding, Debt to assets, Debt to equity, Dividend yield, Earnings yield,
                    Enterprise value, Enterprise value over EBITDA, Ev to free cash flow, Ev to operating
                    cash flow, Ev to sales, Free cash flow per share, Free cash flow yield, Graham net net,
                    Graham number, Income quality, Intangibles to total assets, Interest debt per share,
                    Inventory turnover, Market cap, Net current asset value, Net debt to EBITDA, Net income
                    per share, Operating cash flow per share, Payables turnover, Payout ratio, Pb ratio, Pe
                    ratio, Pfcf ratio, Pocf ratio, Price to sales ratio, Ptb ratio, Receivables turnover,
                    Research and development to revenue, Return on tangible assets, Revenue per share,
                    Roe, Roic, Sales general and administrative to revenue, Shareholders equity per
                    share, Stock based compensation to revenue, Tangible book value per share, and Working
                    capital. [Source: Financial Modeling Prep]
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_key_metrics(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            if ns_parser.source == "AlphaVantage":
                av_view.display_key(
                    symbol=self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_ratios(self, other_args: List[str]):
        """Process ratios command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ratios",
            description="""
                    Prints in-depth ratios of a company over time. This can be either quarterly or
                    annually. This contains, among other things, Price-to-Book Ratio, Payout Ratio and
                    Operating Cycle. The following fields are expected: Asset turnover, Capital expenditure
                    coverage ratio, Cash conversion cycle, Cash flow coverage ratios, Cash flow to debt
                    ratio, Cash per share, Cash ratio, Company equity multiplier, Current ratio, Days of
                    inventory outstanding, Days of payables outstanding, Days of sales outstanding, Debt
                    equity ratio, Debt ratio, Dividend paid and capex coverage ratio, Dividend payout ratio,
                    Dividend yield, Ebit per revenue, Ebt per ebit, Effective tax rate, Enterprise value
                    multiple, Fixed asset turnover, Free cash flow operating cash flow ratio, Free cash
                    flow per share, Gross profit margin, Inventory turnover, Long term debt to
                    capitalization, Net income per EBT, Net profit margin, Operating cash flow per share,
                    Operating cash flow sales ratio, Operating cycle, Operating profit margin, Payables
                    turnover, Payout ratio, Pretax profit margin, Price book value ratio, Price cash flow
                    ratio, Price earnings ratio, Price earnings to growth ratio, Price fair value,
                    Price sales ratio, Price to book ratio, Price to free cash flows ratio, Price to
                    operating cash flows ratio, Price to sales ratio, Quick ratio, Receivables turnover,
                    Return on assets, Return on capital employed, Return on equity, Short term coverage
                    ratios, and Total debt to capitalization. [Source: Financial Modeling Prep]
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            fmp_view.display_financial_ratios(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_growth(self, other_args: List[str]):
        """Process growth command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="growth",
            description=""" Prints the growth of several financial statement items and ratios over
                time. This can be either annually and quarterly. These are, among other things, Revenue
                Growth (3, 5 and 10 years), inventory growth and operating cash flow growth (3, 5 and 10
                years). The following fields are expected: Asset growth, Book valueper share growth, Debt
                growth, Dividendsper share growth, Ebit growth, Eps diluted growth, Eps growth, Five y
                dividendper share growth per share, Five y net income growth per share, Five y operating c
                f growth per share, Five y revenue growth per share, Five y shareholders equity growth per
                share, Free cash flow growth, Gross profit growth, Inventory growth, Net income growth,
                Operating cash flow growth, Operating income growth, Rd expense growth, Receivables growth,
                Revenue growth, Sga expenses growth, Ten y dividendper share growth per share, Ten y net
                income growth per share, Ten y operating c f growth per share, Ten y revenue growth per
                share, Ten y shareholders equity growth per share, Three y dividendper share growth per
                share, Three y net income growth per share, Three y operating c f growth per share, Three y
                revenue growth per share, Three y shareholders equity growth per share, Weighted average
                shares diluted growth, and Weighted average shares growth [Source: Financial Modeling Prep]
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            fmp_view.display_financial_statement_growth(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_epsfc(self, other_args: List[str]):
        """Process eps forecast command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="epsfc",
            description="""Estimated EPS [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            seeking_alpha_view.display_eps_estimates(
                self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_revfc(self, other_args: List[str]):
        """Process revenue forecast command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="revfc",
            description="""Estimated revenue [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            seeking_alpha_view.display_rev_estimates(
                self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_splits(self, other_args: List[str]):
        """Process splits command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="splits",
            description="""Stock splits and reverse split events since IPO [Source: Yahoo Finance]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            yahoo_finance_view.display_splits(
                self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_shrs(self, other_args: List[str]):
        """Process shrs command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shrs",
            description="""Print Major, institutional and mutualfunds shareholders.
            [Source: Yahoo Finance]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--holder",
            choices=self.SHRS_CHOICES,
            default="institutional",
            help="Table of holders to get",
            dest="holder",
        )

        if other_args and "--holder" not in other_args[0] and "-h" not in other_args:
            other_args.insert(0, "--holder")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if not self.suffix:
                yahoo_finance_view.display_shareholders(
                    self.ticker,
                    holder=ns_parser.holder,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_divs(self, other_args: List[str]):
        """Process divs command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="divs",
            description="Historical dividends for a company",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            default=16,
            help="Number of previous dividends to show",
        )
        parser.add_argument(
            "-p",
            "--plot",
            dest="plot",
            default=False,
            action="store_true",
            help="Plots changes in dividend over time",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if not self.suffix:
                yahoo_finance_view.display_dividends(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_income(self, other_args: List[str]):
        """Process income command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="income",
            description="""
                Prints a complete income statement over time. This can be either quarterly or annually.
                The following fields are expected: Accepted date, Cost and expenses, Cost of revenue,
                Depreciation and amortization, Ebitda, Ebitda Ratio, Eps, EPS Diluted, Filling date,
                Final link, General and administrative expenses, Gross profit, Gross profit ratio,
                Income before tax, Income before tax ratio, Income tax expense, Interest expense, Link,
                Net income, Net income ratio, Operating expenses, Operating income, Operating income
                ratio, Other expenses, Period, Research and development expenses, Revenue, Selling and
                marketing expenses, Total other income expenses net, Weighted average shs out, Weighted
                average shs out dil [Source: Alpha Vantage]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        parser.add_argument(
            "-r",
            "--ratios",
            action="store_true",
            default=False,
            dest="ratios",
            help="Shows percentage change of values.",
        )
        parser.add_argument(
            "-p",
            "--plot",
            action="store",
            metavar="column",
            choices=stocks_helper.INCOME_PLOT_CHOICES,
            type=str,
            default=None,
            dest="plot",
            help="Rows to plot, comma separated. (-1 represents invalid data)",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            limit=5,
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                console.print(
                    "[red]Quarterly data currently unavailable for yfinance"
                    ", showing yearly.[/red]\n"
                )
            if stocks_helper.verify_plot_options(
                "income", ns_parser.source, ns_parser.plot
            ):
                return
            if ns_parser.source == "AlphaVantage":
                av_view.display_income_statement(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "Polygon":
                polygon_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="income",
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_income_statement(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="financials",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Income_Statement",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_balance(self, other_args: List[str]):
        """Process balance command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balance",
            description="""
                Prints a complete balance sheet statement over time. This can be either quarterly or
                annually. The following fields are expected: Accepted date, Account payables,
                Accumulated other comprehensive income loss, Cash and cash equivalents, Cash and short
                term investments, Common stock, Deferred revenue, Deferred revenue non current,
                Deferred tax liabilities non current, Filling date, Final link, Goodwill,
                Goodwill and intangible assets, Intangible assets, Inventory, Link, Long term debt,
                Long term investments, Net debt, Net receivables, Other assets, Other current assets,
                Other current liabilities, Other liabilities, Other non current assets, Other non
                current liabilities, Othertotal stockholders equity, Period, Property plant equipment
                net, Retained earnings, Short term debt, Short term investments, Tax assets, Tax
                payables, Total assets, Total current assets, Total current liabilities, Total debt,
                Total investments, Total liabilities, Total liabilities and stockholders equity, Total
                non current assets, Total non current liabilities, and Total stockholders equity.
                [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        parser.add_argument(
            "-r",
            "--ratios",
            action="store_true",
            default=False,
            dest="ratios",
            help="Shows percentage change of values.",
        )
        parser.add_argument(
            "-p",
            "--plot",
            action="store",
            choices=stocks_helper.BALANCE_PLOT_CHOICES,
            type=str,
            metavar="column",
            default=None,
            dest="plot",
            help="Rows to plot, comma separated. (-1 represents invalid data)",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=5,
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                text = "Quarterly data currently unavailable for yfinance"
                console.print(f"[red]{text}, showing yearly.[/red]\n")
            if stocks_helper.verify_plot_options(
                "balance", ns_parser.source, ns_parser.plot
            ):
                return
            if ns_parser.source == "AlphaVantage":
                av_view.display_balance_sheet(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "Polygon":
                polygon_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="balance",
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_balance_sheet(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="balance-sheet",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Balance_Sheet",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_cash(self, other_args: List[str]):
        """Process cash command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cash",
            description="""
                Prints a complete cash flow statement over time. This can be either quarterly or
                annually. The following fields are expected: Accepted date, Accounts payables, Accounts
                receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash
                at end of period, Change in working capital, Common stock issued, Common stock
                repurchased, Debt repayment, Deferred income tax, Depreciation and amortization,
                Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash
                flow, Inventory, Investments in property plant and equipment, Link, Net cash provided
                by operating activities, Net cash used for investing activities, Net cash used provided
                by financing activities, Net change in cash, Net income, Operating cash flow, Other
                financing activities, Other investing activities, Other non cash items, Other working
                capital, Period, Purchases of investments, Sales maturities of investments, Stock based
                compensation. [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Number of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        parser.add_argument(
            "-r",
            "--ratios",
            action="store_true",
            default=False,
            dest="ratios",
            help="Shows percentage change of values.",
        )
        parser.add_argument(
            "-p",
            "--plot",
            action="store",
            type=str,
            choices=stocks_helper.CASH_PLOT_CHOICES,
            metavar="column",
            default=None,
            dest="plot",
            help="Rows to plot. (-1 represents invalid data)",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                text = "Quarterly data currently unavailable for yfinance"
                console.print(f"[red]{text}, showing yearly.[/red]\n")
            if stocks_helper.verify_plot_options(
                "cash", ns_parser.source, ns_parser.plot
            ):
                return
            if ns_parser.source == "AlphaVantage":
                av_view.display_cash_flow(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_cash_flow(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "Polygon":
                polygon_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="cash",
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="cash-flow",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Cash_Flow",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_earnings(self, other_args: List[str]):
        """Process earnings command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="earnings",
            description="""
                Print earnings dates and reported EPS of the company. The following fields are
                expected: Fiscal Date Ending and Reported EPS. [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Number of latest info",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if ns_parser.source == "AlphaVantage":
                av_view.display_earnings(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_earnings(
                    symbol=self.ticker, limit=ns_parser.limit, export=ns_parser.export
                )

    @log_start_end(log=logger)
    def call_fraud(self, other_args: List[str]):
        """Process fraud command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter,
            prog="fraud",
            description=(
                "M-score:\n------------------------------------------------\n"
                "The Beneish model is a statistical model that uses financial ratios calculated with"
                " accounting data of a specific company in order to check if it is likely (high"
                " probability) that the reported earnings of the company have been manipulated."
                " A score of -5 to -2.22 indicated a low chance of fraud, a score of -2.22 to -1.78"
                " indicates a moderate change of fraud, and a score above -1.78 indicated a high"
                " chance of fraud.[Source: Wikipedia]\n\nDSRI:\nDays Sales in Receivables Index"
                " gauges whether receivables and revenue are out of balance, a large number is"
                " expected to be associated with a higher likelihood that revenues and earnings are"
                " overstated.\n\nGMI:\nGross Margin Index shows if gross margins are deteriorating."
                " Research suggests that firms with worsening gross margin are more likely to engage"
                " in earnings management, therefore there should be a positive correlation between"
                " GMI and probability of earnings management.\n\nAQI:\nAsset Quality Index measures"
                " the proportion of assets where potential benefit is less certain. A positive"
                " relation between AQI and earnings manipulation is expected.\n\nSGI:\nSales Growth"
                " Index shows the amount of growth companies are having. Higher growth companies are"
                " more likely to commit fraud so there should be a positive relation between SGI and"
                " earnings management.\n\nDEPI:\nDepreciation Index is the ratio for the rate of"
                " depreciation. A DEPI greater than 1 shows that the depreciation rate has slowed and"
                " is positively correlated with earnings management.\n\nSGAI:\nSales General and"
                " Administrative Expenses Index measures the change in SG&A over sales. There should"
                " be a positive relationship between SGAI and earnings management.\n\nLVGI:\nLeverage"
                " Index represents change in leverage. A LVGI greater than one indicates a lower"
                " change of fraud.\n\nTATA: \nTotal Accruals to Total Assets is a proxy for the"
                " extent that cash underlies earnings. A higher number is associated with a higher"
                " likelihood of manipulation.\n\n\n"
                "Z-score:\n------------------------------------------------\n"
                "The Zmijewski Score is a bankruptcy model used to predict a firm's bankruptcy in two"
                " years. The ratio uses in the Zmijewski score were determined by probit analysis ("
                "think of probit as probability unit). In this case, scores less than .5 represent a"
                " higher probability of default. One of the criticisms that Zmijewski made was that"
                " other bankruptcy scoring models oversampled distressed firms and favored situations"
                " with more complete data.[Source: YCharts]"
                "\n\nMcKee-score:\n------------------------------------------------\n"
                "The McKee Score is a bankruptcy model used to predict a firm's bankruptcy in one year"
                "It looks at a company's size, profitability, and liquidity to determine the probability."
                "This model is 80% accurate in predicting bankruptcy."
            ),
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-e",
            "--explanation",
            action="store_true",
            dest="exp",
            default=False,
            help="Shows an explanation for the metrics",
        )
        parser.add_argument(
            "-d",
            "--detail",
            action="store_true",
            dest="detail",
            default=False,
            help="Shows the details for calculating the mscore",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return
            av_view.display_fraud(
                symbol=self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                detail=ns_parser.detail,
            )

    @log_start_end(log=logger)
    def call_dupont(self, other_args: List[str]):
        """Process dupont command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter,
            prog="dupont",
            description="The extended dupont deconstructs return on equity to allow investors to understand it better",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            av_view.display_dupont(
                self.ticker, raw=ns_parser.raw, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_dcf(self, other_args: List[str]):
        """Process dcf command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dcf",
            description="""
                A discounted cash flow statement looks to analyze the value of a company. To do
                this we need to predict the future cash flows and then determine how much those
                cash flows are worth to us today.\n\n

                We predict the future expected cash flows by predicting what the financial
                statements will look like in the future, and then using this to determine the
                cash the company will have in the future. This cash is paid to share holders.
                We use linear regression to predict the future financial statements.\n\n

                Once we have our predicted financial statements we need to determine how much the
                cash flows are worth today. This is done with a discount factor. Our DCF allows
                users to choose between Fama French and CAPM for the factor. This allows us
                to calculate the present value of the future cash flows.\n\n

                The present value of all of these cash payments is the companies' value. Dividing
                this value by the number of shares outstanding allows us to calculate the value of
                each share in a company.\n\n
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-a",
            "--audit",
            action="store_true",
            dest="audit",
            default=False,
            help="Generates a tie-out for financial statement information pulled from online.",
        )
        parser.add_argument(
            "--no-ratios",
            action="store_false",
            dest="ratios",
            default=True,
            help="Removes ratios from DCF.",
        )
        parser.add_argument(
            "--no-filter",
            action="store_true",
            dest="ratios",
            default=False,
            help="Allow similar companies of any market cap to be shown.",
        )
        parser.add_argument(
            "-p",
            "--prediction",
            type=int,
            dest="prediction",
            default=10,
            help="Number of years to predict before using terminal value.",
        )
        parser.add_argument(
            "-s",
            "--similar",
            type=int,
            dest="similar",
            default=0,
            help="Number of similar companies to generate ratios for.",
        )
        parser.add_argument(
            "-b",
            "--beta",
            type=float,
            dest="beta",
            default=1,
            help="The beta you'd like to use for the calculation.",
        )
        parser.add_argument(
            "-g",
            "--growth",
            action="store_true",
            dest="growth",
            default=False,
            help="Whether to replace a linear regression estimate with a growth estimate.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if self.ticker:
                try:
                    dcf = dcf_view.CreateExcelFA(
                        symbol=self.ticker,
                        beta=ns_parser.beta,
                        audit=ns_parser.audit,
                        ratios=ns_parser.ratios,
                        len_pred=ns_parser.prediction,
                        max_similars=ns_parser.similar,
                        growth=ns_parser.growth,
                    )
                except Exception as e:
                    logger.exception(e)
                    console.print(
                        "[red]Could not properly create the DCF, please make sure you are"
                        " using a valid, US listed ticker.[/red]"
                    )
                    return
                if dcf and dcf.data:
                    dcf.create_workbook()
            else:
                console.print("Please use --ticker or load a ticker first.")

    @log_start_end(log=logger)
    def call_dcfc(self, other_args: List[str]):
        """Process dcfc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dcfc",
            description="""
                    Prints the discounted cash flow of a company over time including the DCF of today. The
                    following fields are expected: DCF, Stock price, and Date. [Source: Financial Modeling
                    Prep]
                """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of latest years/quarters.",
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter fundamental data flag.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            fmp_view.display_discounted_cash_flow(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_warnings(self, other_args: List[str]):
        """Process warnings command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="warnings",
            description="""
                Sean Seah warnings. Check: Consistent historical earnings per share;
                Consistently high return on equity; Consistently high return on assets; 5x Net
                Income > Long-Term Debt; and Interest coverage ratio more than 3. See
                https://www.drwealth.com/gone-fishing-with-buffett-by-sean-seah/comment-page-1/
                [Source: Market Watch]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            default=False,
            dest="b_debug",
            help="print insights into warnings calculation.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])

            marketwatch_view.display_sean_seah_warnings(
                symbol=self.ticker, debug=ns_parser.b_debug
            )

    @log_start_end(log=logger)
    def key_metrics_explained(self, other_args: List[str]):
        """Key metrics explained."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""
                Provides information about main key metrics. Namely: EBITDA,
                EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            filepath = "fundamental_analysis/key_metrics_explained.txt"
            with open(filepath) as fp:
                line = fp.readline()
                while line:
                    console.print(f"{line.strip()}")
                    line = fp.readline()

    @log_start_end(log=logger)
    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pt",
            description="""Prints price target from analysts. [Source: Business Insider and Financial Modeling Prep]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True, limit=10
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if ns_parser.source == "BusinessInsider":
                business_insider_view.display_price_target_from_analysts(
                    symbol=self.ticker,
                    data=self.stock,
                    start_date=self.start,
                    limit=ns_parser.limit,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_price_targets(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_est(self, other_args: List[str]):
        """Process est command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="est",
            description="""Yearly estimates and quarter earnings/revenues.
            [Source: Business Insider]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-e",
            "--estimate",
            help="Estimates to get",
            dest="estimate",
            choices=self.ESTIMATE_CHOICES,
            default="annual_earnings",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            business_insider_view.display_estimates(
                symbol=self.ticker,
                estimate=ns_parser.estimate,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rot(self, other_args: List[str]):
        """Process rot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rot",
            description="""
                Rating over time (monthly). [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of last months",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            finnhub_view.rating_over_time(
                symbol=self.ticker,
                limit=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rating(self, other_args: List[str]):
        """Process rating command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rating",
            description="""
                Based on specific ratios, prints information whether the company
                is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
                P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of last days to display ratings",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            if ns_parser.source == "Finviz":
                finviz_view.analyst(
                    symbol=self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.rating(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_sec(self, other_args: List[str]):
        """Process sec command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="sec",
            description="""
                Prints SEC filings of the company. The following fields are expected: Filing Date,
                Document Date, Type, Category, Amended, and Link. [Source: Market Watch and FinancialModelingPrep]
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            default=self.ticker,
            help="The ticker to be used to get SEC filings.",
        )

        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=20,
            help="number of latest SEC filings.",
        )
        parser.add_argument(
            "-y",
            "--year",
            action="store",
            dest="year",
            type=check_positive,
            default=None,
            help="year of SEC filings.",
        )
        parser.add_argument(
            "-f",
            "--form",
            action="store",
            dest="form",
            type=str,
            help="form group of SEC filings.",
            choices=nasdaq_model.FORM_GROUP.keys(),
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            nasdaq_view.sec_filings(
                symbol=ns_parser.ticker,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                year=ns_parser.year,
                form_group=ns_parser.form,
            )

    @log_start_end(log=logger)
    def call_supplier(self, other_args: List[str]):
        """Process supplier command"""
        parser = argparse.ArgumentParser(
            prog="supplier",
            add_help=False,
            description="List of suppliers from ticker provided. [Source: CSIMarket]",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            csimarket_view.suppliers(
                symbol=self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_customer(self, other_args: List[str]):
        """Process customer command"""
        parser = argparse.ArgumentParser(
            prog="customer",
            add_help=False,
            description="List of customers from ticker provided. [Source: CSIMarket]",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])
            if not self.ticker:
                console.print(no_ticker_message)
                return

            csimarket_view.customers(
                symbol=self.ticker,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
