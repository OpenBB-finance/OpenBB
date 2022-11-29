"""Optimization helpers"""
__docformat__ = "numpy"

import argparse
import pandas as pd

from openbb_terminal.portfolio.portfolio_optimization import statics
from openbb_terminal.rich_config import console

# These are all the possible yfinance properties
valid_property_infos = [
    "previousClose",
    "regularMarketOpen",
    "twoHundredDayAverage",
    "trailingAnnualDividendYield",
    "payoutRatio",
    "volume24Hr",
    "regularMarketDayHigh",
    "navPrice",
    "averageDailyVolume10Day",
    "totalAssets",
    "regularMarketPreviousClose",
    "fiftyDayAverage",
    "trailingAnnualDividendRate",
    "open",
    "toCurrency",
    "averageVolume10days",
    "expireDate",
    "yield",
    "algorithm",
    "dividendRate",
    "exDividendDate",
    "beta",
    "circulatingSupply",
    "regularMarketDayLow",
    "priceHint",
    "currency",
    "trailingPE",
    "regularMarketVolume",
    "lastMarket",
    "maxSupply",
    "openInterest",
    "marketCap",
    "volumeAllCurrencies",
    "strikePrice",
    "averageVolume",
    "priceToSalesTrailing12Months",
    "dayLow",
    "ask",
    "ytdReturn",
    "askSize",
    "volume",
    "fiftyTwoWeekHigh",
    "forwardPE",
    "fromCurrency",
    "fiveYearAvgDividendYield",
    "fiftyTwoWeekLow",
    "bid",
    "dividendYield",
    "bidSize",
    "dayHigh",
    "annualHoldingsTurnover",
    "enterpriseToRevenue",
    "beta3Year",
    "profitMargins",
    "enterpriseToEbitda",
    "52WeekChange",
    "morningStarRiskRating",
    "forwardEps",
    "revenueQuarterlyGrowth",
    "sharesOutstanding",
    "fundInceptionDate",
    "annualReportExpenseRatio",
    "bookValue",
    "sharesShort",
    "sharesPercentSharesOut",
    "fundFamily",
    "lastFiscalYearEnd",
    "heldPercentInstitutions",
    "netIncomeToCommon",
    "trailingEps",
    "lastDividendValue",
    "SandP52WeekChange",
    "priceToBook",
    "heldPercentInsiders",
    "shortRatio",
    "sharesShortPreviousMonthDate",
    "floatShares",
    "enterpriseValue",
    "threeYearAverageReturn",
    "lastSplitFactor",
    "legalType",
    "lastDividendDate",
    "morningStarOverallRating",
    "earningsQuarterlyGrowth",
    "pegRatio",
    "lastCapGain",
    "shortPercentOfFloat",
    "sharesShortPriorMonth",
    "impliedSharesOutstanding",
    "fiveYearAverageReturn",
    "regularMarketPrice",
]


def check_valid_property_type(check_property: str) -> str:
    """Check that the property selected is valid"""
    if check_property in valid_property_infos:
        return check_property

    raise argparse.ArgumentTypeError(f"{check_property} is not a valid info")


def dict_to_df(d: dict) -> pd.DataFrame:
    """Convert a dictionary to a DataFrame

    Parameters
    ----------
    d : dict
        Dictionary to convert

    Returns
    -------
    pd.DataFrame
        DataFrame with dictionary
    """

    if not d:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(data=d, orient="index", columns=["value"])

    return df


def validate_risk_measure(risk_measure: str, warning: bool = True) -> str:
    """Check that the risk measure selected is valid

    Parameters
    ----------
    risk_measure : str
        Risk measure to check

    Returns
    -------
    str
        Validated risk measure
    """
    if risk_measure.lower() in statics.RISK_CHOICES:
        return statics.RISK_CHOICES[risk_measure.lower()]
    if warning:
        console.print("[yellow]Risk measure not found. Using 'MV'.[/yellow]")
    return "MV"
