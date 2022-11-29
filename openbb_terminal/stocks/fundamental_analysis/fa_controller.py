"""Fundamental Analysis Controller."""
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime, timedelta
from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    valid_date,
    list_from_str,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import console, MenuText, get_ordered_list_sources
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.fundamental_analysis import (
    av_view,
    business_insider_view,
    dcf_view,
    eclect_us_view,
    finviz_view,
    market_watch_view,
    yahoo_finance_view,
    polygon_view,
    fmp_view,
    eodhd_view,
)

# pylint: disable=inconsistent-return-statements,C0302,R0904


logger = logging.getLogger(__name__)


class FundamentalAnalysisController(StockBaseController):
    """Fundamental Analysis Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "analysis",
        "score",
        "profile",
        "quote",
        "enterprise",
        "metrics",
        "ratios",
        "growth",
        "warnings",
        "data",
        "income",
        "balance",
        "cash",
        "mgmt",
        "splits",
        "info",
        "shrs",
        "sust",
        "cal",
        "web",
        "hq",
        "overview",
        "key",
        "income",
        "balance",
        "cash",
        "divs",
        "earnings",
        "fraud",
        "dcf",
        "dcfc",
        "mktcap",
        "dupont",
    ]

    PATH = "/stocks/fa/"

    SHRS_CHOICES = ["major", "institutional", "mutualfund"]
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        suffix: str = "",
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = f"{ticker}.{suffix}" if suffix else ticker
        self.start = start
        self.interval = interval
        self.suffix = suffix

        self.default_income = get_ordered_list_sources(f"{self.PATH}income")[0]
        self.default_balance = get_ordered_list_sources(f"{self.PATH}balance")[0]
        self.default_cash = get_ordered_list_sources(f"{self.PATH}cash")[0]

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("stocks/fa/")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker.upper())
        mt.add_raw("\n")
        mt.add_cmd("income")
        mt.add_cmd("balance")
        mt.add_cmd("cash")
        mt.add_cmd("data")
        mt.add_cmd("mgmt")
        mt.add_cmd("analysis")
        mt.add_cmd("score")
        mt.add_cmd("profile")
        mt.add_cmd("quote")
        mt.add_cmd("enterprise")
        mt.add_cmd("metrics")
        mt.add_cmd("ratios")
        mt.add_cmd("growth")
        mt.add_cmd("warnings")
        mt.add_cmd("dcf")
        mt.add_cmd("dcfc")
        mt.add_cmd("info")
        mt.add_cmd("mktcap")
        mt.add_cmd("shrs", not self.suffix)
        mt.add_cmd("sust", not self.suffix)
        mt.add_cmd("cal", not self.suffix)
        mt.add_cmd("divs", not self.suffix)
        mt.add_cmd("splits", not self.suffix)
        mt.add_cmd("web", not self.suffix)
        mt.add_cmd("hq", not self.suffix)
        mt.add_cmd("overview")
        mt.add_cmd("key")
        mt.add_cmd("earnings")
        mt.add_cmd("fraud")
        mt.add_cmd("dupont")
        console.print(text=mt.menu_text, menu="Stocks - Fundamental Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.suffix:
                return ["stocks", f"load {self.ticker}.{self.suffix}", "fa"]
            return ["stocks", f"load {self.ticker}", "fa"]
        return []

    @log_start_end(log=logger)
    def call_analysis(self, other_args: List[str]):
        """Process analysis command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="analysis",
            description="""Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]""",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            eclect_us_view.display_analysis(symbol=self.ticker, export=ns_parser.export)

    @log_start_end(log=logger)
    def call_mgmt(self, other_args: List[str]):
        """Process mgmt command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mgmt",
            description="""
                Print management team. Namely: Name, Title, Information from google and
                (potentially) Insider Activity page. [Source: Business Insider]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.display_management(
                symbol=self.ticker, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_data(self, other_args: List[str]):
        """Process data command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="data",
            description="""
                Print several metrics about the company. The following fields are expected:
                Company, Sector, Industry, Country, Index, P/E, EPS (ttm), Insider Own,
                Shs Outstand, Perf Week, Market Cap, Forward P/E, EPS next Y, Insider Trans,
                Shs Float, Perf Month, Income, EPS next Q, Inst Own, Short Float, Perf Quarter,
                Sales, P/S, EPS this Y, Inst Trans, Short Ratio, Perf Half Y, Book/sh, P/B, ROA,
                Target Price, Perf Year, Cash/sh, P/C, ROE, 52W Range, Perf YTD, P/FCF, EPS past 5Y,
                ROI, 52W High, Beta, Quick Ratio, Sales past 5Y, Gross Margin, 52W Low, ATR,
                Employees, Current Ratio, Sales Q/Q, Operating Margin, RSI (14), Volatility, Optionable,
                Debt/Eq, EPS Q/Q, Profit Margin, Rel Volume, Prev Close, Shortable, LT Debt/Eq,
                Earnings, Payout, Avg Volume, Price, Recommendation, SMA20, SMA50, SMA200, Volume, Change.
                [Source: Finviz]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_screen_data(symbol=self.ticker, export=ns_parser.export)

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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.valinvest_score(self.ticker)

    @log_start_end(log=logger)
    def call_profile(self, other_args: List[str]):
        """Process profile command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="profile",
            description="""
                    Prints information about, among other things, the industry, sector exchange and company
                    description. The following fields are expected: Address, Beta, Ceo, Changes, Cik, City
                    Company name, Country, Currency, Cusip, Dcf, Dcf diff, Default image, Description,
                    Exchange, Exchange short name, Full time employees, Image, Industry, Ipo date, Isin,
                    Last div, Mkt cap, Phone, Price, Range, Sector, State, Symbol, Vol avg, Website, Zip.
                    [Source: Financial Modeling Prep]
                """,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_profile(self.ticker)

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="""
                    Prints actual information about the company which is, among other things, the day high,
                    market cap, open and close price and price-to-equity ratio. The following fields are
                    expected: Avg volume, Change, Changes percentage, Day high, Day low, Earnings
                    announcement, Eps, Exchange, Market cap, Name, Open, Pe, Previous close, Price, Price
                    avg200, Price avg50, Shares outstanding, Symbol, Timestamp, Volume, Year high, and Year
                    low. [Source: Financial Modeling Prep]
                """,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_quote(self.ticker)

    @log_start_end(log=logger)
    def call_enterprise(self, other_args: List[str]):
        """Process enterprise command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="enterprise",
            description="""
                    Prints stock price, number of shares, market capitalization and
                    enterprise value over time. The following fields are expected: Add total debt,
                    Enterprise value, Market capitalization, Minus cash and cash equivalents, Number
                    of shares, Stock price, and Symbol. [Source: Financial Modeling Prep]
                """,
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
            fmp_view.display_enterprise(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
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
            fmp_view.display_key_metrics(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
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
            fmp_view.display_financial_ratios(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
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
            fmp_view.display_financial_statement_growth(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_info(self, other_args: List[str]):
        """Process info command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""
                Print information about the company. The following fields are expected:
                Zip, Sector, Full time employees, Long business summary, City, Phone, State, Country,
                Website, Max age, Address, Industry, Previous close, Regular market open, Two hundred
                day average, Payout ratio, Regular market day high, Average daily volume 10 day,
                Regular market previous close, Fifty day average, Open, Average volume 10 days, Beta,
                Regular market day low, Price hint, Currency, Trailing PE, Regular market volume,
                Market cap, Average volume, Price to sales trailing 12 months, Day low, Ask, Ask size,
                Volume, Fifty two week high, Forward PE, Fifty two week low, Bid, Tradeable, Bid size,
                Day high, Exchange, Short name, Long name, Exchange timezone name, Exchange timezone
                short name, Is esg populated, Gmt off set milliseconds, Quote type, Symbol, Message
                board id, Market, Enterprise to revenue, Profit margins, Enterprise to ebitda, 52 week
                change, Forward EPS, Shares outstanding, Book value, Shares short, Shares percent
                shares out, Last fiscal year end, Held percent institutions, Net income to common,
                Trailing EPS, Sand p52 week change, Price to book, Held percent insiders, Next fiscal
                year end, Most recent quarter, Short ratio, Shares short previous month date, Float
                shares, Enterprise value, Last split date, Last split factor, Earnings quarterly growth,
                Date short interest, PEG ratio, Short percent of float, Shares short prior month,
                Regular market price, Logo_url. [Source: Yahoo Finance]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoo_finance_view.display_info(self.ticker, export=ns_parser.export)

    @log_start_end(log=logger)
    def call_mktcap(self, other_args: List[str]):
        """Process mktcap command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mktcap",
            description="""Market Cap estimate over time. [Source: Yahoo Finance]""",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=3 * 366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the market cap display",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            yahoo_finance_view.display_mktcap(
                self.ticker, start_date=ns_parser.start, export=ns_parser.export
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            yahoo_finance_view.display_splits(self.ticker, export=ns_parser.export)

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
            "--holder",
            choices=self.SHRS_CHOICES,
            default="institutional",
            help="Table of holders to get",
            dest="holder",
        )

        if other_args and "--holder" not in other_args[0][0] and "-h" not in other_args:
            other_args.insert(0, "--holder")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.suffix:
                yahoo_finance_view.display_shareholders(
                    self.ticker, holder=ns_parser.holder, export=ns_parser.export
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_sust(self, other_args: List[str]):
        """Process sust command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sust",
            description="""
                Print sustainability values of the company. The following fields are expected:
                Palmoil, Controversialweapons, Gambling, Socialscore, Nuclear, Furleather, Alcoholic,
                Gmo, Catholic, Socialpercentile, Peercount, Governancescore, Environmentpercentile,
                Animaltesting, Tobacco, Total ESG, Highestcontroversy, ESG Performance, Coal, Pesticides,
                Adult, Percentile, Peergroup, Smallarms, Environmentscore, Governancepercentile,
                Militarycontract. [Source: Yahoo Finance]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.suffix:
                yahoo_finance_view.display_sustainability(
                    self.ticker, export=ns_parser.export
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_cal(self, other_args: List[str]):
        """Process cal command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cal",
            description="""
                Calendar earnings of the company. Including revenue and earnings estimates.
                [Source: Yahoo Finance]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.suffix:
                yahoo_finance_view.display_calendar_earnings(
                    symbol=self.ticker, export=ns_parser.export
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_web(self, other_args: List[str]):
        """Process web command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="web",
            description="""
                Opens company's website. [Source: Yahoo Finance]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.suffix:
                yahoo_finance_view.open_web(self.ticker)
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_hq(self, other_args: List[str]):
        """Process hq command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hq",
            description="""
                Opens in Google Maps HQ location of the company. [Source: Yahoo Finance]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.suffix:
                yahoo_finance_view.open_headquarters_map(self.ticker)
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
            if not self.suffix:
                yahoo_finance_view.display_dividends(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                )
            else:
                console.print("Only US tickers are recognized.", "\n")

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
                Prints an overview about the company. The following fields are expected:
                Symbol, Asset type, Name, Description, Exchange, Currency, Country, Sector, Industry,
                Address, Full time employees, Fiscal year end, Latest quarter, Market capitalization,
                EBITDA, PE ratio, PEG ratio, Book value, Dividend per share, Dividend yield, EPS,
                Revenue per share TTM, Profit margin, Operating margin TTM, Return on assets TTM,
                Return on equity TTM, Revenue TTM, Gross profit TTM, Diluted EPS TTM, Quarterly
                earnings growth YOY, Quarterly revenue growth YOY, Analyst target price, Trailing PE,
                Forward PE, Price to sales ratio TTM, Price to book ratio, EV to revenue, EV to EBITDA,
                Beta, 52 week high, 52 week low, 50 day moving average, 200 day moving average, Shares
                outstanding, Shares float, Shares short, Shares short prior month, Short ratio, Short
                percent outstanding, Short percent float, Percent insiders, Percent institutions,
                Forward annual dividend rate, Forward annual dividend yield, Payout ratio, Dividend
                date, Ex dividend date, Last split factor, and Last split date. Also, the C i k field
                corresponds to Central Index Key, which can be used to search a company on
                https://www.sec.gov/edgar/searchedgar/cik.htm [Source: Alpha Vantage]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_overview(self.ticker)

    @log_start_end(log=logger)
    def call_key(self, other_args: List[str]):
        """Process key command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="key",
            description="""
                Gives main key metrics about the company (it's a subset of the Overview data from Alpha
                Vantage API). The following fields are expected: Market capitalization, EBITDA, EPS, PE
                ratio, PEG ratio, Price to book ratio, Return on equity TTM, Payout ratio, Price to
                sales ratio TTM, Dividend yield, 50 day moving average, Analyst target price, Beta
                [Source: Alpha Vantage API]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_key(symbol=self.ticker, export=ns_parser.export)

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
            choices=stocks_helper.INCOME_PLOT[self.default_income],
            type=str,
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
            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                console.print(
                    "[red]Quarterly data currently unavailable for yfinance"
                    ", showing yearly.[/red]\n"
                )
            if ns_parser.source == "AlphaVantage":
                av_view.display_income_statement(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_income_statement(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="financials",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                console.print("Source is EOD Historical Data!")
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Income_Statement",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
            choices=stocks_helper.BALANCE_PLOT[self.default_balance],
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
            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                text = "Quarterly data currently unavailable for yfinance"
                console.print(f"[red]{text}, showing yearly.[/red]\n")
            if ns_parser.source == "AlphaVantage":
                av_view.display_balance_sheet(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_balance_sheet(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="balance-sheet",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                console.print("Source is EOD Historical Data!")
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Balance_Sheet",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
            choices=stocks_helper.CASH_PLOT[self.default_cash],
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
            ns_parser.plot = list_from_str(ns_parser.plot)
            # TODO: Switch to actually getting data
            if ns_parser.source == "YahooFinance" and ns_parser.b_quarter:
                text = "Quarterly data currently unavailable for yfinance"
                console.print(f"[red]{text}, showing yearly.[/red]\n")
            if ns_parser.source == "AlphaVantage":
                av_view.display_cash_flow(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_cash_flow(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="cash-flow",
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    limit=ns_parser.limit,
                )
            elif ns_parser.source == "EODHD":
                console.print("Source is EOD Historical Data!")
                eodhd_view.display_fundamentals(
                    symbol=self.ticker,
                    statement="Cash_Flow",
                    quarterly=ns_parser.b_quarter,
                    ratios=ns_parser.ratios,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
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
            if ns_parser.source == "AlphaVantage":
                av_view.display_earnings(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    quarterly=ns_parser.b_quarter,
                    export=ns_parser.export,
                )
            elif ns_parser.source == "YahooFinance":
                yahoo_finance_view.display_earnings(
                    symbol=self.ticker, limit=ns_parser.limit, export=ns_parser.export
                )
            else:
                pass

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
            av_view.display_fraud(
                symbol=self.ticker,
                export=ns_parser.export,
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
            default=6,
            help="Number of similar companies to generate ratios for.",
        )
        parser.add_argument(
            "-g",
            "--growth",
            action="store_true",
            dest="growth",
            default=False,
            help="Whether to replace a linear regression estimate with a growth estimate.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            dcf = dcf_view.CreateExcelFA(
                symbol=self.ticker,
                audit=ns_parser.audit,
                ratios=ns_parser.ratios,
                len_pred=ns_parser.prediction,
                max_similars=ns_parser.similar,
                growth=ns_parser.growth,
            )
            dcf.create_workbook()

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
            fmp_view.display_discounted_cash_flow(
                symbol=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
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
            market_watch_view.display_sean_seah_warnings(
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
