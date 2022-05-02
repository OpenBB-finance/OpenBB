"""YFinance Model"""
__docformat__ = "numpy"

import logging
import os
import tempfile
from calendar import monthrange
from datetime import date
from typing import List

import numpy as np
import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta, FR

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

# pylint: disable=R0912, E1101

yf_info_choices = [
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
    "fundFamily",
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


@log_start_end(log=logger)
def process_stocks(
    list_of_stocks: List[str], period: str = "3mo", start: str = "", end: str = ""
) -> pd.DataFrame:
    """Get adjusted closing price for each stock in the list

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to get historical data for
    period: str
        Period to get data from yfinance, personalized
    start: str
        If not using period, start date string (YYYY-MM-DD)
    end: str
        If not using period, end date string (YYYY-MM-DD). If empty use last
        weekday.

    Returns
    -------
    stock_closes: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """

    period_choices = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    directory = "gst_temp_files"
    parent_dir = tempfile.gettempdir()
    path = os.path.join(parent_dir, directory)

    if os.path.isdir(path) is False:
        os.mkdir(path)

    stock_closes = None

    if start != "":
        if end == "":
            end_ = date.today()
        else:
            end_ = date.fromisoformat(end)

        # Check if end date is on weekend
        if end_.weekday() >= 5:
            end_ = end_ + relativedelta(weekday=FR(-1))

        end = end_.strftime("%Y-%m-%d")

        # Creating temporal file name
        name = os.path.join(path, "Stocks " + start + " to " + end + ".pkl")

        # Checking if exist
        if os.path.exists(name):
            stock_closes_0 = pd.read_pickle(name)
            list_of_stocks_0 = list(set(list_of_stocks) - set(stock_closes_0.columns))
        else:
            stock_closes_0 = None
            list_of_stocks_0 = list_of_stocks

        # Download assets that are not in temporal file
        if list_of_stocks_0 == []:
            stock_closes = stock_closes_0.copy()
        else:
            stock_prices = yf.download(
                list_of_stocks_0,
                start=start,
                end=end,
                progress=False,
                group_by="ticker",
            )

    else:
        if period in period_choices:
            # Setting temporal file name
            name = os.path.join(
                path,
                "Stocks " + period + " " + date.today().strftime("%Y-%m-%d") + ".pkl",
            )

            # Creating if exist
            if os.path.exists(name):
                stock_closes_0 = pd.read_pickle(name)
                list_of_stocks_0 = list(
                    set(list_of_stocks) - set(stock_closes_0.columns)
                )
            else:
                stock_closes_0 = None
                list_of_stocks_0 = list_of_stocks

            # Download assets that are not in temporal file
            if list_of_stocks_0 == []:
                stock_closes = stock_closes_0.copy()
            else:
                stock_prices = yf.download(
                    list_of_stocks_0, period=period, progress=False, group_by="ticker"
                )

        else:
            end_ = date.today()
            if end_.weekday() >= 5:
                end_ = end_ + relativedelta(weekday=FR(-1))
            if period.find("d") >= 1:
                days = int(period[:-1])
                start_ = end_ - relativedelta(days=days)
            elif period.find("w") >= 1:
                weeks = int(period[:-1])
                start_ = end_ - relativedelta(weeks=weeks)
            elif period.find("mo") >= 1:
                months = int(period[:-2])
                start_ = end_ - relativedelta(months=months)
            elif period.find("y") >= 1:
                years = int(period[:-1])
                start_ = end_ - relativedelta(years=years)
            else:
                # console.print(
                #     "Please use an adequate period."
                # )
                return None

            start = start_.strftime("%Y-%m-%d")
            end = end_.strftime("%Y-%m-%d")

            # Creating temporal file name
            name = os.path.join(path, "Stocks " + start + " to " + end + ".pkl")

            # Checking if temporal file exists
            if os.path.exists(name):
                stock_closes_0 = pd.read_pickle(name)
                list_of_stocks_0 = list(
                    set(list_of_stocks) - set(stock_closes_0.columns)
                )
            else:
                stock_closes_0 = None
                list_of_stocks_0 = list_of_stocks

            # Download assets that are not in temporal file
            if list_of_stocks_0 == []:
                stock_closes = stock_closes_0.copy()
            else:
                stock_prices = yf.download(
                    list_of_stocks_0,
                    start=start,
                    end=end,
                    progress=False,
                    group_by="ticker",
                )

    if stock_closes is None:
        if len(list_of_stocks_0) == 1:
            stock_closes = stock_prices.loc[:, ["Adj Close"]]
            stock_closes.columns = list_of_stocks_0
        else:
            stock_closes = stock_prices.loc[:, (slice(None), "Adj Close")]
            stock_closes.columns = stock_closes.columns.get_level_values(0)

    if list_of_stocks_0 != []:
        stock_closes = pd.concat([stock_closes, stock_closes_0], axis=1)
        stock_closes.to_pickle(name)

    stock_closes = stock_closes[list_of_stocks]

    return stock_closes


@log_start_end(log=logger)
def process_returns(
    stock_prices: pd.DataFrame,
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
) -> pd.DataFrame:
    """Process stock prices to calculate returns and delete outliers

    Parameters
    ----------
    stock_prices: pd.DataFrame
        DataFrame of stock prices
    log_returns: bool
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str or int
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
            - 'D' for daily returns.
            - 'W' for weekly returns.
            - 'M' for monthly returns.

    maxnan: str or float
        Max percentage of nan values accepted per asset to be included in
        returns
    threshold: str or float
        Value used to replace outliers that are higher to threshold in daily returns.
    method: str
        Method used to fill nan values. Default value is 'time'. For more information see
        `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`_.

    Returns
    -------
    stock_returns: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """

    # Interpolate nan values
    stock_returns = stock_prices.copy()
    stock_returns.interpolate(method=method, axis=0, inplace=True)

    # Select stocks with low number of nans
    selected_stocks = np.isnan(stock_returns).sum(axis=0)
    selected_stocks = np.where(selected_stocks <= maxnan * stock_returns.shape[0])[0]
    stock_returns = stock_returns.iloc[:, selected_stocks]

    # Replace values above and below threshold
    if threshold > 0:
        stock_returns = stock_returns.pct_change()
        stock_returns.mask(stock_returns > threshold, threshold, inplace=True)
        stock_returns.mask(stock_returns < -threshold, -threshold, inplace=True)

        s = stock_returns.isna().idxmin().tolist()
        j = 0
        for i in s:
            stock_returns.iloc[stock_returns.index.get_loc(i) - 1, j] = 0
            j += 1

        stock_returns = stock_returns + 1
        stock_returns = stock_returns.cumprod()

    # Change the frequency of the data
    if freq.upper() == "D":
        pass
    elif freq.upper() in ["W", "M"]:
        last_day = stock_returns.index[-1]
        stock_returns = stock_returns.resample(freq).last()
        if freq.upper() == ["W"]:
            if last_day.weekday() < 4:
                stock_returns = stock_returns.iloc[:-1, :]
        if freq.upper() == ["M"]:
            if monthrange(last_day.year, last_day.month)[1] - last_day.day <= 5:
                stock_returns = stock_returns.iloc[:-1, :]

    # Calculate returns
    if log_returns is True:
        stock_returns = np.log(stock_returns)
        stock_returns = stock_returns.diff().dropna()
    else:
        stock_returns = stock_returns.pct_change().dropna()

    return stock_returns
