""" Financial Modeling Prep Controller """
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from gamestonk_terminal.menu import session


class FinancialModelingPrepController(BaseController):
    """Financial Modeling Prep Controller class"""

    CHOICES_COMMANDS = [
        "profile",
        "quote",
        "enterprise",
        "dcf",
        "income",
        "balance",
        "cash",
        "metrics",
        "ratios",
        "growth",
    ]
    PATH = "/stocks/fa/fmp/"

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.interval = interval

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
[param]Ticker: [/param]{self.ticker}[cmds]

    profile       profile of the company
    quote         quote of the company
    enterprise    enterprise value of the company over time
    dcf           discounted cash flow of the company over time
    income        income statements of the company
    balance       balance sheet of the company
    cash          cash flow statement of the company
    metrics       key metrics of the company
    ratios        financial ratios of the company
    growth        financial statement growth of the company[/cmds]
        """
        console.print(
            text=help_text,
            menu="Stocks - Fundamental Analysis - Financial Modeling Prep",
        )

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "fa", "fmp"]
        return []

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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_profile(self.ticker)

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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            fmp_view.display_quote(self.ticker)

    def call_enterprise(self, other_args: List[str]):
        """Process income command"""
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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_enterprise(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_dcf(self, other_args: List[str]):
        """Process dcf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dcf",
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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_discounted_cash_flow(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_income(self, other_args: List[str]):
        """Process income command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="inc",
            description="""
                Prints a complete income statement over time. This can be either quarterly or annually.
                The following fields are expected: Accepted date, Cost and expenses, Cost of
                revenue, Depreciation and amortization, EBITDA, EBITDA Ratio, Eps, Eps Diluted, Filling
                date, Final link, General and administrative expenses, Gross profit, Gross profit
                ratio, Income before tax, Income before tax ratio, Income tax expense, Interest
                expense, Link, Net income, Net income ratio, Operating expenses, Operating income,
                Operating income ratio, Other expenses, Period, Research and development expenses,
                Revenue, Selling and marketing expenses, Total other income expenses net, Weighted
                average shs out, Weighted average shs out dil [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_income_statement(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bal",
            description="""
                Prints a complete balance sheet statement over time. This can be
                either quarterly or annually. The following fields are expected: Accepted date,
                Account payables, Accumulated other comprehensive income loss, Cash and cash
                equivalents, Cash and short term investments, Common stock, Deferred revenue,
                Deferred revenue non current, Deferred tax liabilities non current, Filling date,
                Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory,
                Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets,
                Other current assets, Other current liabilities, Other liabilities, Other non current
                assets, Other non current liabilities, Othertotal stockholders equity, Period, Property
                plant equipment net, Retained earnings, Short term debt, Short term investments, Tax
                assets, Tax payables, Total assets, Total current assets, Total current liabilities,
                Total debt, Total investments, Total liabilities, Total liabilities and stockholders
                equity, Total non current assets, Total non current liabilities, and Total stockholders
                equity. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_balance_sheet(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_cash(self, other_args: List[str]):
        """Process cash command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cash",
            description="""
                Prints a complete cash flow statement over time. This can be either
                quarterly or annually. The following fields are expected: Accepted date, Accounts
                payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at
                beginning of period, Cash at end of period, Change in working capital, Common stock
                issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and
                amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final
                link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net
                cash provided by operating activities, Net cash used for investing activities, Net cash
                used provided by financing activities, Net change in cash, Net income, Operating cash
                flow, Other financing activities, Other investing activities, Other non cash items,
                Other working capital, Period, Purchases of investments, Sales maturities of
                investments, Stock based compensation. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_cash_flow(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_key_metrics(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_ratios(self, other_args: List[str]):
        """Process cash command"""
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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_financial_ratios(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )

    def call_growth(self, other_args: List[str]):
        """Process cash command"""
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
            default=1,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.display_financial_statement_growth(
                ticker=self.ticker,
                number=ns_parser.limit,
                quarterly=ns_parser.b_quarter,
                export=ns_parser.export,
            )
