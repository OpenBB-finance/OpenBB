"""Optimization helpers"""
__docformat__ = "numpy"

import argparse
import requests

# These are all the possible yfinance properties
l_valid_property_infos = [
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


def check_valid_property_type(aproperty: str) -> str:
    """Check that the property selected is valid"""
    if aproperty in l_valid_property_infos:
        return aproperty

    raise argparse.ArgumentTypeError(f"{aproperty} is not a valid info")


def get_rf() -> float:
    """Uses the fiscaldata.gov API to get most recent T-Bill rate"""
    try:
        base = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        end = "/v2/accounting/od/avg_interest_rates"
        filters = "?filter=security_desc:eq:Treasury Bills&sort=-record_date"
        response = requests.get(base + end + filters)
        latest = response.json()["data"][0]
        return round(float(latest["avg_interest_rate_amt"]) / 100, 8)
    except Exception:
        return 0.02
