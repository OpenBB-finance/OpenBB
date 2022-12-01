"""Optimization helpers"""
__docformat__ = "numpy"

import argparse
from typing import Any
import pandas as pd

from openbb_terminal.portfolio.portfolio_optimization.statics import (
    RISK_CHOICES,
    OPTIMIZATION_PARAMETERS,
    TERMINAL_TEMPLATE_MAP,
)
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
    if risk_measure.lower() in RISK_CHOICES:
        return RISK_CHOICES[risk_measure.lower()]
    if warning:
        console.print("[yellow]Risk measure not found. Using 'MV'.[/yellow]")
    return "MV"


def get_kwarg(key: str, kwargs: dict, default: Any = None) -> Any:
    """Get a key from kwargs

    If key is in kwargs, returns it.
    Otherwise, if default provided, returns it.
    Otherwise, if key is in OPTIMIZATION_PARAMETERS, returns it.

    Parameters
    ----------
    key : str
        The key to be searched
    kwargs : dict
        The kwargs to be searched
    default : Any
        The default value to be returned if the key is not found

    Returns
    -------
    Any
        The value of the key if it exists, else None
    """

    if key in kwargs:
        return kwargs[key]

    if default:
        return default

    # TODO: Remove this line when mapping between template and terminal is not needed
    template_key = TERMINAL_TEMPLATE_MAP.get(key, key)

    PARAMETER = OPTIMIZATION_PARAMETERS.get(template_key)
    if PARAMETER is None:
        return default
    return PARAMETER.default
