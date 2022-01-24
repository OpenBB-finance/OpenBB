"""Fundamental Analysis Controller."""
__docformat__ = "numpy"

import argparse
from datetime import datetime, timedelta
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_controller,
    fmp_view,
)
from gamestonk_terminal.stocks.fundamental_analysis import (
    eclect_us_view,
    finviz_view,
    yahoo_finance_view,
    av_view,
    business_insider_view,
    dcf_view,
    market_watch_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    check_positive,
    valid_date,
)
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.menu import session

# pylint: disable=inconsistent-return-statements


class FundamentalAnalysisController(BaseController):
    """Fundamental Analysis Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "analysis",
        "score",
        "warnings",
        "data",
        "income",
        "balance",
        "cash",
        "mgmt",
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
    ]

    CHOICES_MENUS = [
        "fmp",
    ]
    PATH = "/stocks/fa/"

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

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"]["-i"] = {c: {} for c in stocks_helper.INTERVALS}
            choices["load"]["-s"] = {c: {} for c in stocks_helper.SOURCES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        is_foreign_start = "" if not self.suffix else "[unvl]"
        is_foreign_end = "" if not self.suffix else "[/unvl]"
        help_text = f"""[param]
Ticker: [/param] {self.ticker} [cmds]

[cmds]    data          fundamental and technical data of company [src][FinViz][/src]
    mgmt          management team of the company [src][Business Insider][/src]
    analysis      analyse SEC filings with the help of machine learning [src][Eclect.us][/src]
    score         investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham [src][FMP][/src]
    warnings      company warnings according to Sean Seah book [src][Market Watch][/src]
    dcf           advanced Excel customizable discounted cash flow [src][Stockanalysis][/src][/cmds]
[src][Yahoo Finance][/src]
    info          information scope of the company{is_foreign_start}
    shrs          shareholders of the company
    sust          sustainability values of the company
    cal           calendar earnings and estimates of the company
    web           open web browser of the company
    hq            open HQ location of the company
    divs          show historical dividends for company{is_foreign_end}
[src][Alpha Vantage][/src]
    overview      overview of the company
    key           company key metrics
    income        income statements of the company
    balance       balance sheet of the company
    cash          cash flow of the company
    earnings      earnings dates and reported EPS
    fraud         key fraud ratios[/cmds]
[info]Other Sources:[/info][menu]
>   fmp           profile,quote,enterprise,dcf,income,ratios,growth from FMP[/menu]
        """
        console.print(text=help_text, menu="Stocks - Fundamental Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "fa"]
        return []

    def call_load(self, other_args: List[str]):
        """Process load command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source "
            + "is 'yf', an Indian ticker can be loaded by using '.NS' at the end, e.g. "
            + "'SBIN.NS'. See available market in"
            + " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
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
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=stocks_helper.INTERVALS,
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=stocks_helper.SOURCES,
            default="yf",
            help="Source of historical data.",
        )
        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ticker=ns_parser.ticker,
                start=ns_parser.start,
                interval=ns_parser.interval,
                source=ns_parser.source,
            )

            if not df_stock_candidate.empty:
                self.start = ns_parser.start
                self.interval = str(ns_parser.interval) + "min"
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()

    def call_analysis(self, other_args: List[str]):
        """Process analysis command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="analysis",
            description="""Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            eclect_us_view.display_analysis(self.ticker)

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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.display_management(
                ticker=self.ticker, export=ns_parser.export
            )

    def call_data(self, other_args: List[str]):
        """Process screener command."""
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
                Earnings, Payout, Avg Volume, Price, Recomendation, SMA20, SMA50, SMA200, Volume, Change.
                [Source: Finviz]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_screen_data(self.ticker)

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.valinvest_score(self.ticker)

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoo_finance_view.display_info(self.ticker)

    def call_shrs(self, other_args: List[str]):
        """Process shrs command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shrs",
            description="""Print Major, institutional and mutualfunds shareholders.
            [Source: Yahoo Finance]""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.display_shareholders(self.ticker)
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.display_sustainability(self.ticker)
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.display_calendar_earnings(ticker=self.ticker)
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.open_web(self.ticker)
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.open_headquarters_map(self.ticker)
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not self.suffix:
            if ns_parser:
                yahoo_finance_view.display_dividends(
                    ticker=self.ticker,
                    limit=ns_parser.limit,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                )
        else:
            console.print("Only US tickers are recognized.", "\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_overview(self.ticker)

    def call_key(self, other_args: List[str]):
        """Process overview command."""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_key(self.ticker)

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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_income_statement(
                ticker=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_balance_sheet(
                ticker=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_cash_flow(
                ticker=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_earnings(
                ticker=self.ticker,
                limit=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
            )

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
            ),
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            av_view.display_fraud(self.ticker)

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

                We predict the future expected cash flows by prediciting what the financial
                statements will look like in the future, and then using this to determine the
                cash the company will have in the future. This cash is paid to share holders.
                We us linear regression to predict the future financial statements.\n\n

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
            "-p" "--prediction",
            type=int,
            dest="prediction",
            default=10,
            help="Number of years to predict before using terminal value.",
        )
        parser.add_argument(
            "-s" "--similar",
            type=int,
            dest="similar",
            default=6,
            help="Number of similar companies to generate ratios for.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            dcf = dcf_view.CreateExcelFA(
                self.ticker,
                ns_parser.audit,
                ns_parser.ratios,
                ns_parser.prediction,
                ns_parser.similar,
            )
            dcf.create_workbook()

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            market_watch_view.display_sean_seah_warnings(
                ticker=self.ticker, debug=ns_parser.b_debug
            )

    def call_fmp(self, _):
        """Process fmp command."""
        self.queue = self.load_class(
            fmp_controller.FinancialModelingPrepController,
            self.ticker,
            self.start,
            self.interval,
            self.queue,
        )


def key_metrics_explained(other_args: List[str]):
    """Key metrics explained.

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
        description="""
            Provides information about main key metrics. Namely: EBITDA,
            EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.
        """,
    )
    ns_parser = parse_known_args_and_warn(
        parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
    )
    if ns_parser:
        filepath = "fundamental_analysis/key_metrics_explained.txt"
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                console.print(f"{line.strip()}")
                line = fp.readline()
            console.print("")
