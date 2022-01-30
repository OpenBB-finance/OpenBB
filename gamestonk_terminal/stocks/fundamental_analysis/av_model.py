"""Alpha Vantage Model"""
__docformat__ = "numpy"

from typing import Dict, Tuple, List

import requests

from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import numpy as np
from gamestonk_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index
from gamestonk_terminal.helper_funcs import long_number_format
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.rich_config import console


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

    # If the returned data was successful
    if result.status_code == 200:
        # Parse json data to dataframe
        if "Note" in result.json():
            console.print(result.json()["Note"], "\n")
            return pd.DataFrame()

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
        return df_fa
    return pd.DataFrame()


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
            "Price to sales ratio TTM",
            "Dividend yield",
            "50 day moving average",
            "Analyst target price",
            "Beta",
        ]
        return df_fa.loc[as_key_metrics]

    return pd.DataFrame()


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
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url)
    if r.status_code == 200:
        statements = r.json()
        df_fa = pd.DataFrame()
        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        else:
            if "annualReports" in statements:
                df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa.head(number)
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        return df_fa[::-1].T
    return pd.DataFrame()


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
    if r.status_code == 200:
        statements = r.json()
        df_fa = pd.DataFrame()
        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        else:
            if "annualReports" in statements:
                df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa.head(number)
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        return df_fa[::-1].T
    return pd.DataFrame()


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
    if r.status_code == 200:
        statements = r.json()
        df_fa = pd.DataFrame()
        if quarterly:
            if "quarterlyReports" in statements:
                df_fa = pd.DataFrame(statements["quarterlyReports"])
        else:
            if "annualReports" in statements:
                df_fa = pd.DataFrame(statements["annualReports"])

        if df_fa.empty:
            return pd.DataFrame()

        df_fa = df_fa.set_index("fiscalDateEnding")
        df_fa = df_fa.head(number)
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        return df_fa[::-1].T
    return pd.DataFrame()


def get_earnings(ticker: str, quarterly: bool = False) -> pd.DataFrame:
    """Get earnings calendar for ticker

    Parameters
    ----------
    ticker : str
        Stock ticker
    quarterly : bool, optional
        [Flag to get quarterly and not annual, by default False

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

    # If the returned data was successful
    if result.status_code == 200:
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
    return pd.DataFrame()


def df_values(df: pd.DataFrame, item: str) -> List[int]:
    """Clean the values from the df

    Parameters
    ----------
    df : pd.DataFrame
        The Dataframe to use
    item : str
        The item to select

    Returns
    -------
    values : List[int]
        The values for the dataframe
    """
    selection = df[item]
    values = selection.apply(lambda x: int(x) if x else 0).values
    return values.tolist()


def get_fraud_ratios(ticker: str) -> Tuple[Dict[str, float], float, float]:
    """Get fraud ratios based on fundamentals

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    Dict[float]:
        Dictionary of fraud metrics
    float:
        Z score for fraud metrics
    """
    fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
    # pylint: disable=unbalanced-tuple-unpacking
    # pylint: disable=no-member
    df_cf, _ = fd.get_cash_flow_annual(symbol=ticker)
    df_bs, _ = fd.get_balance_sheet_annual(symbol=ticker)
    df_is, _ = fd.get_income_statement_annual(symbol=ticker)
    df_cf = df_cf.set_index("fiscalDateEnding").iloc[:2]
    df_bs = df_bs.set_index("fiscalDateEnding").iloc[:2]
    df_is = df_is.set_index("fiscalDateEnding").iloc[:2]

    ar = df_values(df_bs, "currentNetReceivables")
    sales = df_values(df_is, "totalRevenue")
    cogs = df_values(df_is, "costofGoodsAndServicesSold")
    ni = df_values(df_is, "netIncome")
    ca = df_values(df_bs, "totalCurrentAssets")
    cl = df_values(df_bs, "totalCurrentLiabilities")
    ppe = df_values(df_bs, "propertyPlantEquipment")
    cash = df_values(df_bs, "cashAndCashEquivalentsAtCarryingValue")
    cash_and_sec = df_values(df_bs, "cashAndShortTermInvestments")
    sec = [y - x for (x, y) in zip(cash, cash_and_sec)]
    ta = df_values(df_bs, "totalAssets")
    dep = df_values(df_bs, "accumulatedDepreciationAmortizationPPE")
    sga = df_values(df_is, "sellingGeneralAndAdministrative")
    tl = df_values(df_bs, "totalLiabilities")
    icfo = df_values(df_is, "netIncomeFromContinuingOperations")
    cfo = df_values(df_cf, "operatingCashflow")

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
    v1 = np.log(ta[0] / 1000)
    v2 = ni[0] / ta[0]
    v3 = cash[0] / cl[0]

    x = ((v1 + 0.85) * v2) - 0.85
    y = 1 + v3

    mckee = x ** 2 / (x ** 2 + y ** 2)

    return ratios, zscore, mckee
