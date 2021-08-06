""" Alpha Vantage View """
__docformat__ = "numpy"

import argparse
from typing import List, Dict
import requests

from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index
from gamestonk_terminal.helper_funcs import (
    check_positive,
    long_number_format,
    parse_known_args_and_warn,
)


def overview(other_args: List[str], ticker: str):
    """Alpha Vantage stock ticker overview

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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Request OVERVIEW data from Alpha Vantage API
        s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
        result = requests.get(s_req, stream=True)

        # If the returned data was successful
        if result.status_code == 200:
            # Parse json data to dataframe
            df_fa = pd.json_normalize(result.json())
            # Keep json data sorting in dataframe
            df_fa = df_fa[list(result.json().keys())].T
            df_fa.iloc[5:] = df_fa.iloc[5:].applymap(lambda x: long_number_format(x))
            clean_df_index(df_fa)
            df_fa = df_fa.rename(
                index={
                    "E b i t d a": "EBITDA",
                    "P e ratio": "PE ratio",
                    "P e g ratio": "PEG ratio",
                    "E p s": "EPS",
                    "Revenue per share t t m": "Revenue per share TTM",
                    "Operating margin t t m": "Operating margin TTM",
                    "Return on assets t t m": "Return on assets TTM",
                    "Return on equity t t m": "Return on equity TTM",
                    "Revenue t t m": "Revenue TTM",
                    "Gross profit t t m": "Gross profit TTM",
                    "Diluted e p s t t m": "Diluted EPS TTM",
                    "Quarterly earnings growth y o y": "Quarterly earnings growth YOY",
                    "Quarterly revenue growth y o y": "Quarterly revenue growth YOY",
                    "Trailing p e": "Trailing PE",
                    "Forward p e": "Forward PE",
                    "Price to sales ratio t t m": "Price to sales ratio TTM",
                    "E v to revenue": "EV to revenue",
                    "E v to e b i t d a": "EV to EBITDA",
                }
            )

            pd.set_option("display.max_colwidth", None)

            print(df_fa.drop(index=["Description"]).to_string(header=False))
            print(f"Description: {df_fa.loc['Description'][0]}")
            print("")
        else:
            print(f"Error: {result.status_code}")
        print("")

    except Exception as e:
        print(e, "\n")


def key(other_args: List[str], ticker: str):
    """Alpha Vantage key metrics

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
        prog="key",
        description="""
            Gives main key metrics about the company (it's a subset of the Overview data from Alpha
            Vantage API). The following fields are expected: Market capitalization, EBITDA, EPS, PE
            ratio, PEG ratio, Price to book ratio, Return on equity TTM, Payout ratio, Price to
            sales ratio TTM, Dividend yield, 50 day moving average, Analyst target price, Beta
            [Source: Alpha Vantage API]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Request OVERVIEW data
        s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
        result = requests.get(s_req, stream=True)

        # If the returned data was successful
        if result.status_code == 200:
            df_fa = pd.json_normalize(result.json())
            df_fa = df_fa[list(result.json().keys())].T
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            clean_df_index(df_fa)
            df_fa = df_fa.rename(
                index={
                    "E b i t d a": "EBITDA",
                    "P e ratio": "PE ratio",
                    "P e g ratio": "PEG ratio",
                    "E p s": "EPS",
                    "Return on equity t t m": "Return on equity TTM",
                    "Price to sales ratio t t m": "Price to sales ratio TTM",
                }
            )
            as_key_metrics = [
                "Market capitalization",
                "EBITDA",
                "EPS",
                "PE ratio",
                "PEG ratio",
                "Price to book ratio",
                "Return on equity TTM",
                "Payout ratio",
                "Price to sales ratio TTM",
                "Dividend yield",
                "50 day moving average",
                "Analyst target price",
                "Beta",
            ]
            print(df_fa.loc[as_key_metrics].to_string(header=False))
        else:
            print(f"Error: {result.status_code}")
        print("")

    except Exception as e:
        print(e, "\n")


def income_statement(other_args: List[str], ticker: str):
    """Alpha Vantage income statement

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
        prog="income",
        description="""
            Prints a complete income statement over time. This can be either quarterly or annually.
            The following fields are expected: Accepted date, Cost and expenses, Cost of revenue,
            Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling date,
            Final link, General and administrative expenses, Gross profit, Gross profit ratio,
            Income before tax, Income before tax ratio, Income tax expense, Interest expense, Link,
            Net income, Net income ratio, Operating expenses, Operating income, Operating income
            ratio, Other expenses, Period, Research and development expenses, Revenue, Selling and
            marketing expenses, Total other income expenses net, Weighted average shs out, Weighted
            average shs out dil [Source: Alpha Vantage]""",
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

        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        if ns_parser.b_quarter:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_income_statement_quarterly(symbol=ticker)
        else:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_income_statement_annual(symbol=ticker)

        df_fa = clean_fundamentals_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def balance_sheet(other_args: List[str], ticker: str):
    """Alpha Vantage balance sheet

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
        (ns_parser, l_unknown_args) = parser.parse_known_args(other_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        if ns_parser.b_quarter:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_balance_sheet_quarterly(symbol=ticker)
        else:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_balance_sheet_annual(symbol=ticker)

        df_fa = clean_fundamentals_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def cash_flow(other_args: List[str], ticker: str):
    """Alpha Vantage cash flow

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

        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        if ns_parser.b_quarter:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_cash_flow_quarterly(symbol=ticker)
        else:
            # pylint: disable=unbalanced-tuple-unpacking
            df_fa, _ = fd.get_cash_flow_annual(symbol=ticker)

        df_fa = clean_fundamentals_df(df_fa, num=ns_parser.n_num)
        print(df_fa)
        print("")

    except Exception as e:
        print(e, "\n")


def earnings(other_args: List[str], ticker: str):
    """Alpha Vantage earnings

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
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=5,
        help="Number of latest info",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.n_num == 1:
            pd.set_option("display.max_colwidth", None)
        else:
            pd.options.display.max_colwidth = 40

        # Request EARNINGS data from Alpha Vantage API
        s_req = (
            "https://www.alphavantage.co/query?function=EARNINGS&"
            f"symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
        )
        result = requests.get(s_req, stream=True)

        # If the returned data was successful
        if result.status_code == 200:
            df_fa = pd.json_normalize(result.json())
            if ns_parser.b_quarter:
                df_fa = pd.DataFrame(df_fa["quarterlyEarnings"][0])
                df_fa = df_fa[
                    [
                        "fiscalDateEnding",
                        "reportedDate",
                        "reportedEPS",
                        "estimatedEPS",
                        "surprise",
                        "surprisePercentage",
                    ]
                ]
                df_fa = df_fa.rename(
                    columns={
                        "fiscalDateEnding": "Fiscal Date Ending",
                        "reportedEPS": "Reported EPS",
                        "estimatedEPS": "Estimated EPS",
                        "reportedDate": "Reported Date",
                        "surprise": "Surprise",
                        "surprisePercentage": "Surprise Percentage",
                    }
                )
            else:
                df_fa = pd.DataFrame(df_fa["annualEarnings"][0])
                df_fa = df_fa.rename(
                    columns={
                        "fiscalDateEnding": "Fiscal Date Ending",
                        "reportedEPS": "Reported EPS",
                    }
                )

            print(df_fa.head(n=ns_parser.n_num).T.to_string(header=False))

        else:
            print(f"Error: {result.status_code}")
        print("")

    except Exception as e:
        print(e, "\n")


def clean_fundamentals_df(df_fa: pd.DataFrame, num: int) -> pd.DataFrame:
    """Clean fundamentals dataframe

    Parameters
    ----------
    df_fa : pd.DataFrame
        Fundamentals dataframe
    num : int
        Number of data rows to display

    Returns
    ----------
    pd.DataFrame
        Clean dataframe to output
    """
    # pylint: disable=no-member
    df_fa = df_fa.set_index("fiscalDateEnding")
    df_fa = df_fa.head(n=num).T
    df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["None"])).dropna()
    df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["0"])).dropna()
    df_fa = df_fa.applymap(lambda x: long_number_format(x))
    clean_df_index(df_fa)
    df_fa.columns.name = "Fiscal Date Ending"

    return df_fa


def fraud(other_args: List[str], ticker: str):
    """Fraud indicators for given ticker
    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        prog="fraud",
        description=(
            "Mscore:\n------------------------------------------------\n"
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
            " extent that cash underlies earnigns. A higher number is associated with a higher"
            " likelihood of manipulation.\n\n\n"
            "Zscore:\n------------------------------------------------\n"
            "The Zmijewski Score is a bankruptcy model used to predict a firm's bankruptcy in two"
            " years. The ratio uses in the Zmijewski score were determined by probit analysis ("
            "think of probit as probability unit). In this case, scores less than .5 represent a"
            " higher probability of default. One of the criticisms that Zmijewski made was that"
            " other bankruptcy scoring models oversampled distressed firms and favored situations"
            " with more complete data.[Source: YCharts]"
        ),
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        # pylint: disable=unbalanced-tuple-unpacking
        # pylint: disable=no-member
        df_cf, _ = fd.get_cash_flow_annual(symbol=ticker)
        df_bs, _ = fd.get_balance_sheet_annual(symbol=ticker)
        df_is, _ = fd.get_income_statement_annual(symbol=ticker)
        df_cf = df_cf.set_index("fiscalDateEnding").iloc[:2]
        df_bs = df_bs.set_index("fiscalDateEnding").iloc[:2]
        df_is = df_is.set_index("fiscalDateEnding").iloc[:2]

        ar = df_bs["currentNetReceivables"].apply(lambda x: int(x)).values
        sales = df_is["totalRevenue"].apply(lambda x: int(x)).values
        cogs = df_is["costofGoodsAndServicesSold"].apply(lambda x: int(x)).values
        ni = df_is["netIncome"].apply(lambda x: int(x)).values
        ca = df_bs["totalCurrentAssets"].apply(lambda x: int(x)).values
        cl = df_bs["totalCurrentLiabilities"].apply(lambda x: int(x)).values
        ppe = df_bs["propertyPlantEquipment"].apply(lambda x: int(x)).values
        cash = (
            df_bs["cashAndCashEquivalentsAtCarryingValue"]
            .apply(lambda x: int(x))
            .values
        )
        cash_and_sec = (
            df_bs["cashAndShortTermInvestments"].apply(lambda x: int(x)).values
        )
        sec = [y - x for (x, y) in zip(cash, cash_and_sec)]
        ta = df_bs["totalAssets"].apply(lambda x: int(x)).values
        dep = (
            df_bs["accumulatedDepreciationAmortizationPPE"]
            .apply(lambda x: int(x))
            .values
        )
        sga = df_is["sellingGeneralAndAdministrative"].apply(lambda x: int(x)).values
        tl = df_bs["totalLiabilities"].apply(lambda x: int(x)).values
        icfo = df_is["netIncomeFromContinuingOperations"].apply(lambda x: int(x)).values
        cfo = df_cf["operatingCashflow"].apply(lambda x: int(x)).values
        ratios: Dict = {}
        ratios["DSRI"] = (ar[0] / sales[0]) / (ar[1] / sales[1])
        ratios["GMI"] = ((sales[1] - cogs[1]) / sales[1]) / (
            (sales[0] - cogs[0]) / sales[0]
        )
        ratios["AQI"] = (1 - ((ca[0] + ppe[0] + sec[0]) / ta[0])) / (
            1 - ((ca[1] + ppe[1] + sec[1]) / ta[1])
        )
        ratios["SGI"] = sales[0] / sales[1]
        ratios["DEPI"] = (dep[1] / (ppe[1] + dep[1])) / (dep[0] / (ppe[0] + dep[0]))
        ratios["SGAI"] = (sga[0] / sales[0]) / (sga[1] / sales[1])
        ratios["LVGI"] = (tl[0] / ta[0]) / (tl[1] / ta[1])
        ratios["TATA"] = (icfo[0] - cfo[0]) / ta[0]
        ratios["MSCORE"] = (
            -4.84
            + (0.92 * ratios["DSRI"])
            + (0.58 * ratios["GMI"])
            + (0.404 * ratios["AQI"])
            + (0.892 * ratios["SGI"])
            + (0.115 * ratios["DEPI"] - (0.172 * ratios["SGAI"]))
            + (4.679 * ratios["TATA"])
            - (0.327 * ratios["LVGI"])
        )

        zscore = (
            -4.336
            - (4.513 * (ni[0] / ta[0]))
            + (5.679 * (tl[0] / ta[0]))
            + (0.004 * (ca[0] / cl[0]))
        )

        if ratios["MSCORE"] > -1.78:
            chanceM = "high"
        elif ratios["MSCORE"] > -2.22:
            chanceM = "moderate"
        else:
            chanceM = "low"

        if zscore < 0.5:
            chanceZ = "high"
        else:
            chanceZ = "low"

        print("Mscore Sub Stats:")
        for rkey, value in ratios.items():
            if rkey != "MSCORE":
                print("  ", f"{rkey} : {value:.2f}")

        print(
            "\n" + "MSCORE: ",
            f"{ratios['MSCORE']:.2f} ({chanceM} chance of fraud)",
        )

        print("ZSCORE: ", f"{zscore:.2f} ({chanceZ} chance of bankruptcy)", "\n")

    except Exception as e:
        print(e, "\n")
