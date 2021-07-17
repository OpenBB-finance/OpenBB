""" Financial Modeling Prep View """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import pandas as pd
import valinvest
import FundamentalAnalysis as fa  # Financial Modeling Prep
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.fundamental_analysis.fa_helper import clean_df_index
from gamestonk_terminal.helper_funcs import (
    long_number_format,
    check_positive,
    parse_known_args_and_warn,
)


def valinvest_score(other_args: List[str], ticker: str):
    """Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="score",
        description="""
            Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        valstock = valinvest.Fundamental(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        score = 100 * (valstock.fscore() / 9)
        print(f"Score: {score:.2f}".rstrip("0").rstrip(".") + " %")
        print("")

    except Exception as e:
        print(e, "\n")


def profile(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker profile

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_fa = fa.profile(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        clean_df_index(df_fa)

        print(df_fa.drop(index=["Description", "Image"]).to_string(header=False))
        print(f"\nImage: {df_fa.loc['Image'][0]}")
        print(f"\nDescription: {df_fa.loc['Description'][0]}")
        print("")

    except Exception as e:
        print(e, "\n")


def quote(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_fa = fa.quote(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        clean_df_index(df_fa)

        df_fa.loc["Market cap"][0] = long_number_format(df_fa.loc["Market cap"][0])
        df_fa.loc["Shares outstanding"][0] = long_number_format(
            df_fa.loc["Shares outstanding"][0]
        )
        df_fa.loc["Volume"][0] = long_number_format(df_fa.loc["Volume"][0])
        # Check if there is a valid earnings announcement
        if df_fa.loc["Earnings announcement"][0]:
            earning_announcement = datetime.strptime(
                df_fa.loc["Earnings announcement"][0][0:19], "%Y-%m-%dT%H:%M:%S"
            )
            df_fa.loc["Earnings announcement"][
                0
            ] = f"{earning_announcement.date()} {earning_announcement.time()}"
        print(df_fa.to_string(header=False))
        print("")

    except Exception as e:
        print(e, "\n")


def enterprise(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.enterprise(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.enterprise(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num, mask=False)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def discounted_cash_flow(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker discounted cash flow

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.discounted_cash_flow(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.discounted_cash_flow(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num, mask=False)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def income_statement(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker income statement

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="inc",
        description="""
            Prints a complete income statement over time. This can be either quarterly or annually.
            The following fields are expected: Accepted date, Cost and expenses, Cost of
            revenue, Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling
            date, Final link, General and administrative expenses, Gross profit, Gross profit
            ratio, Income before tax, Income before tax ratio, Income tax expense, Interest
            expense, Link, Net income, Net income ratio, Operating expenses, Operating income,
            Operating income ratio, Other expenses, Period, Research and development expenses,
            Revenue, Selling and marketing expenses, Total other income expenses net, Weighted
            average shs out, Weighted average shs out dil [Source: Financial Modeling Prep]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.income_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.income_statement(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)

        print(df_fa.drop(index=["Final link", "Link"]).to_string())

        pd.set_option("display.max_colwidth", None)
        print("")
        print(df_fa.loc["Final link"].to_frame().to_string())
        print("")
        print(df_fa.loc["Link"].to_frame().to_string())
        print("")

    except Exception as e:
        print(e, "\n")


def balance_sheet(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker balance sheet

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.balance_sheet_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.balance_sheet_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)

        print(df_fa.drop(index=["Final link", "Link"]).to_string())

        pd.set_option("display.max_colwidth", None)
        print("")
        print(df_fa.loc["Final link"].to_frame().to_string())
        print("")
        print(df_fa.loc["Link"].to_frame().to_string())
        print("")

    except Exception as e:
        print(e, "\n")


def cash_flow(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker cash flow

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.cash_flow_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.cash_flow_statement(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)

        print(df_fa.drop(index=["Final link", "Link"]).to_string())

        pd.set_option("display.max_colwidth", None)
        print("")
        print(df_fa.loc["Final link"].to_frame().to_string())
        print("")
        print(df_fa.loc["Link"].to_frame().to_string())
        print("")

    except Exception as e:
        print(e, "\n")


def key_metrics(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker key metrics

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
            ratio, Pfcf ratio, Pocfratio, Price to sales ratio, Ptb ratio, Receivables turnover,
            Research and development to revenue, Return on tangible assets, Revenue per share,
            Roe, Roic, Sales general and administrative to revenue, Shareholders equity per
            share, Stock based compensation to revenue, Tangible book value per share, and Working
            capital. [Source: Financial Modeling Prep]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 50

        if ns_parser.b_quarter:
            df_fa = fa.key_metrics(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.key_metrics(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def financial_ratios(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker ratios

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
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
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        if ns_parser.b_quarter:
            df_fa = fa.financial_ratios(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_ratios(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def financial_statement_growth(other_args: List[str], ticker: str):
    """Financial Modeling Prep ticker growth

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="growth",
        description=""" Prints the growth of several financial statement items and ratios over
        time. This can be either annually and quarterly. These are, among other things, Revenue
        Growth (3, 5 and 10 years), inventory growth and operating cash flow growth (3, 5 and 10
        years). The following fields are expected: Asset growth, Book valueper share growth, Debt
        growth, Dividendsper share growth, Ebitgrowth, Epsdiluted growth, Epsgrowth, Five y
        dividendper share growth per share, Five y net income growth per share, Five y operating c
        f growth per share, Five y revenue growth per share, Five y shareholders equity growth per
        share, Free cash flow growth, Gross profit growth, Inventory growth, Net income growth,
        Operating cash flow growth, Operating income growth, Rdexpense growth, Receivables growth,
        Revenue growth, Sgaexpenses growth, Ten y dividendper share growth per share, Ten y net
        income growth per share, Ten y operating c f growth per share, Ten y revenue growth per
        share, Ten y shareholders equity growth per share, Three y dividendper share growth per
        share, Three y net income growth per share, Three y operating c f growth per share, Three y
        revenue growth per share, Three y shareholders equity growth per share, Weighted average
        shares diluted growth, and Weighted average shares growth [Source: Financial Modeling Prep]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 50

        if ns_parser.b_quarter:
            df_fa = fa.financial_statement_growth(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_statement_growth(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def clean_metrics_df(df_fa: pd.DataFrame, num: int, mask: bool = True) -> pd.DataFrame:
    """Clean metrics data frame

    Parameters
    ----------
    df_fa : pd.DataFrame
        Metrics data frame
    num : int
        Number of columns to clean
    mask : bool, optional
        Apply mask, by default True

    Returns
    -------
    pd.DataFrame
        Cleaned metrics data frame
    """

    df_fa = df_fa.iloc[:, 0:num]
    if mask:
        df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["None"])).dropna()
        df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["0"])).dropna()
    df_fa = df_fa.applymap(lambda x: long_number_format(x))
    clean_df_index(df_fa)
    df_fa.columns.name = "Fiscal Date Ending"
    df_fa = df_fa.rename(
        index={
            "Enterprise value over e b i t d a": "Enterprise value over EBITDA",
            "Net debt to e b i t d a": "Net debt to EBITDA",
            "D c f": "DCF",
            "Net income per e b t": "Net income per EBT",
        }
    )

    return df_fa
