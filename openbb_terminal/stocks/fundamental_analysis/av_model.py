"""Alpha Vantage Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, List

import numpy as np
import pandas as pd
import requests
from alpha_vantage.fundamentaldata import FundamentalData
from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.stocks_helper import clean_fraction
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_overview(ticker: str) -> pd.DataFrame:
    """Get alpha vantage company overview

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of fundamentals
    """
    # Request OVERVIEW data from Alpha Vantage API
    s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    result = requests.get(s_req, stream=True)

    df_fa = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in result.json():
        console.print(result.json()["Error Message"])
    else:
        # check if json is empty
        if not result.json():
            console.print("No data found")
        # Parse json data to dataframe
        elif "Note" in result.json():
            console.print(result.json()["Note"], "\n")
        else:
            df_fa = pd.json_normalize(result.json())

            # Keep json data sorting in dataframe
            df_fa = df_fa[list(result.json().keys())].T
            df_fa.iloc[5:] = df_fa.iloc[5:].applymap(
                lambda x: lambda_long_number_format(x)
            )
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
    return df_fa


@log_start_end(log=logger)
def get_key_metrics(ticker: str) -> pd.DataFrame:
    """Get key metrics from overview

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of key metrics
    """
    # Request OVERVIEW data
    s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    result = requests.get(s_req, stream=True)

    # If the returned data was unsuccessful
    if "Error Message" in result.json():
        console.print(result.json()["Error Message"])
    else:
        # check if json is empty
        if not result.json() or len(result.json()) < 2:
            console.print("No data found")
            return pd.DataFrame()

        df_fa = pd.json_normalize(result.json())
        df_fa = df_fa[list(result.json().keys())].T
        df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
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
            "Price to sales ratio TTM",
            "Dividend yield",
            "50 day moving average",
            "Analyst target price",
            "Beta",
        ]
        return df_fa.loc[as_key_metrics]

    return pd.DataFrame()


@log_start_end(log=logger)
def get_income_statements(
    ticker: str, number: int, quarterly: bool = False
) -> pd.DataFrame:
    """Get income statements for company

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements
    """
    url = (
        f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}"
        f"&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    r = requests.get(url)

    # If the returned data was unsuccessful
    if "Error Message" in r.json():
        console.print(r.json()["Error Message"])
    else:
        # check if json is empty
        if not r.json():
            console.print("No data found")
        else:
            statements = r.json()
            df_fa = pd.DataFrame()

            if quarterly:
                if "quarterlyReports" in statements:
                    df_fa = pd.DataFrame(statements["quarterlyReports"])
            else:
                if "annualReports" in statements:
                    df_fa = pd.DataFrame(statements["annualReports"])

            if df_fa.empty:
                console.print("No data found")
                return pd.DataFrame()

            df_fa = df_fa.set_index("fiscalDateEnding")
            df_fa = df_fa.head(number)
            df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
            return df_fa[::-1].T
    return pd.DataFrame()


@log_start_end(log=logger)
def get_balance_sheet(
    ticker: str, number: int, quarterly: bool = False
) -> pd.DataFrame:
    """Get balance sheets for company

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements
    """
    url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url)

    # If the returned data was unsuccessful
    if "Error Message" in r.json():
        console.print(r.json()["Error Message"])
    else:
        # check if json is empty
        if not r.json():
            console.print("No data found")
        else:
            statements = r.json()
            df_fa = pd.DataFrame()

            if quarterly:
                if "quarterlyReports" in statements:
                    df_fa = pd.DataFrame(statements["quarterlyReports"])
            else:
                if "annualReports" in statements:
                    df_fa = pd.DataFrame(statements["annualReports"])

            if df_fa.empty:
                console.print("No data found")
                return pd.DataFrame()

            df_fa = df_fa.set_index("fiscalDateEnding")
            df_fa = df_fa.head(number)
            df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
            return df_fa[::-1].T
    return pd.DataFrame()


@log_start_end(log=logger)
def get_cash_flow(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get cash flows for company

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements
    """
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url)

    # If the returned data was unsuccessful
    if "Error Message" in r.json():
        console.print(r.json()["Error Message"])
    else:
        # check if json is empty
        if not r.json():
            console.print("No data found")
        else:
            statements = r.json()
            df_fa = pd.DataFrame()

            if quarterly:
                if "quarterlyReports" in statements:
                    df_fa = pd.DataFrame(statements["quarterlyReports"])
            else:
                if "annualReports" in statements:
                    df_fa = pd.DataFrame(statements["annualReports"])

            if df_fa.empty:
                console.print("No data found")
                return pd.DataFrame()

            df_fa = df_fa.set_index("fiscalDateEnding")
            df_fa = df_fa.head(number)
            df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
            return df_fa[::-1].T
    return pd.DataFrame()


@log_start_end(log=logger)
def get_earnings(ticker: str, quarterly: bool = False) -> pd.DataFrame:
    """Get earnings calendar for ticker

    Parameters
    ----------
    ticker : str
        Stock ticker
    quarterly : bool, optional
        Flag to get quarterly and not annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of earnings
    """
    # Request EARNINGS data from Alpha Vantage API
    s_req = (
        "https://www.alphavantage.co/query?function=EARNINGS&"
        f"symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )
    result = requests.get(s_req, stream=True)
    df_fa = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in result.json():
        console.print(result.json()["Error Message"])
    else:
        # check if json is empty
        if not result.json() or len(result.json()) < 2:
            console.print("No data found")
        else:

            df_fa = pd.json_normalize(result.json())

            if quarterly:
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

    return df_fa


@log_start_end(log=logger)
def df_values(
    df: pd.DataFrame, item: str, index: int = 0, length: int = 2
) -> List[int]:
    """Clean the values from the df

    Parameters
    ----------
    df : pd.DataFrame
        The Dataframe to use
    item : str
        The item to select
    index : int
        The number of row to display
    length : int
        The number of rows to return

    Returns
    -------
    values : List[int]
        The values for the dataframe
    """
    if index:
        df = df.iloc[index : index + length]
    selection = df[item]
    values = selection.apply(lambda x: 0 if (not x or x == "None") else int(x)).values
    return values.tolist()


@log_start_end(log=logger)
def get_fraud_ratios(ticker: str) -> pd.DataFrame:
    """Get fraud ratios based on fundamentals

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    metrics : pd.DataFrame
        The fraud ratios
    """

    try:
        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        # pylint: disable=unbalanced-tuple-unpacking
        df_cf, _ = fd.get_cash_flow_annual(symbol=ticker)
        df_bs, _ = fd.get_balance_sheet_annual(symbol=ticker)
        df_is, _ = fd.get_income_statement_annual(symbol=ticker)

    except Exception as e:
        console.print(e)
        return pd.DataFrame()

    # pylint: disable=no-member
    df_cf = df_cf.set_index("fiscalDateEnding")
    df_bs = df_bs.set_index("fiscalDateEnding")
    df_is = df_is.set_index("fiscalDateEnding")
    fraud_years = pd.DataFrame()
    for i in range(len(df_cf) - 1):
        ar = df_values(df_bs, "currentNetReceivables", i)
        sales = df_values(df_is, "totalRevenue", i)
        cogs = df_values(df_is, "costofGoodsAndServicesSold", i)
        ni = df_values(df_is, "netIncome", i)
        ca = df_values(df_bs, "totalCurrentAssets", i)
        cl = df_values(df_bs, "totalCurrentLiabilities", i)
        ppe = df_values(df_bs, "propertyPlantEquipment", i)
        cash = df_values(df_bs, "cashAndCashEquivalentsAtCarryingValue", i)
        cash_and_sec = df_values(df_bs, "cashAndShortTermInvestments", i)
        sec = [y - x for (x, y) in zip(cash, cash_and_sec)]
        ta = df_values(df_bs, "totalAssets", i)
        dep = df_values(df_bs, "accumulatedDepreciationAmortizationPPE", i)
        sga = df_values(df_is, "sellingGeneralAndAdministrative", i)
        tl = df_values(df_bs, "totalLiabilities", i)
        icfo = df_values(df_is, "netIncomeFromContinuingOperations", i)
        cfo = df_values(df_cf, "operatingCashflow", i)

        ratios: Dict = {}
        try:
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
            v1 = np.log(ta[0] / 1000)
            v2 = ni[0] / ta[0]
            v3 = cash[0] / cl[0]

            x = ((v1 + 0.85) * v2) - 0.85
            y = 1 + v3

            mckee = x**2 / (x**2 + y**2)
            ratios["Zscore"] = zscore
            ratios["Mscore"] = mckee
        except ZeroDivisionError:
            for item in [
                "DSRI",
                "GMI",
                "AQI",
                "SGI",
                "DEPI",
                "SGAI",
                "LVGI",
                "TATA",
                "MSCORE",
                "Zscore",
                "Mscore",
            ]:
                ratios[item] = "N/A"
        if fraud_years.empty:
            fraud_years.index = ratios.keys()
        fraud_years[df_cf.index[i]] = ratios.values()
    fraud_years = fraud_years[sorted(fraud_years)]
    return fraud_years


@log_start_end(log=logger)
def get_dupont(ticker: str) -> pd.DataFrame:
    """Get dupont ratios

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    dupont : pd.DataFrame
        The dupont ratio breakdown
    """

    try:
        fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        # pylint: disable=unbalanced-tuple-unpacking
        df_bs, _ = fd.get_balance_sheet_annual(symbol=ticker)
        df_is, _ = fd.get_income_statement_annual(symbol=ticker)

    except Exception as e:
        console.print(e)
        return pd.DataFrame()

    # pylint: disable=no-member
    df_bs = df_bs.set_index("fiscalDateEnding")
    df_is = df_is.set_index("fiscalDateEnding")
    dupont_years = pd.DataFrame()

    for i in range(len(df_bs)):
        ni = df_values(df_is, "netIncome", i, 1)
        pretax = df_values(df_is, "incomeBeforeTax", i, 1)
        ebit = df_values(df_is, "ebit", i, 1)
        sales = df_values(df_is, "totalRevenue", i, 1)
        assets = df_values(df_bs, "totalAssets", i, 1)
        equity = df_values(df_bs, "totalShareholderEquity", i, 1)

        ratios: Dict = {}
        try:
            ratios["Tax Burden"] = clean_fraction(ni[0], pretax[0])
            ratios["Interest Burden"] = clean_fraction(pretax[0], ebit[0])
            ratios["EBIT Margin"] = clean_fraction(ebit[0], sales[0])
            ratios["Asset Turnover"] = clean_fraction(sales[0], assets[0])
            ratios["Finance Leverage"] = clean_fraction(assets[0], equity[0])
            ratios["ROI"] = clean_fraction(ni[0], equity[0])
        except IndexError:
            pass

        if dupont_years.empty:
            dupont_years.index = ratios.keys()
        dupont_years[df_bs.index[i]] = ratios.values()
    dupont_years = dupont_years[sorted(dupont_years)]
    return dupont_years
