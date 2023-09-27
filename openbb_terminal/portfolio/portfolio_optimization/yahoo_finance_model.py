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
from dateutil.relativedelta import FR, relativedelta

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=R0912, E1101

fast_info_map = {
    "previousClose": "previous_close",
    "twoHundredDayAverage": "two_hundred_day_average",
    "regularMarketDayHigh": "day_high",
    "averageDailyVolume10Day": "ten_day_average_volume",
    "regularMarketPreviousClose": "regular_market_previous_close",
    "fiftyDayAverage": "fifty_day_average",
    "open": "open",
    "averageVolume10days": "ten_day_average_volume",
    "regularMarketDayLow": "day_low",
    "currency": "currency",
    "marketCap": "market_cap",
    "averageVolume": "three_month_average_volume",
    "dayLow": "day_low",
    "volume": "last_volume",
    "fiftyTwoWeekHigh": "year_high",
    "fiftyTwoWeekLow": "year_low",
    "dayHigh": "day_high",
    "regularMarketPrice": "last_price",
}

yf_info_choices = [
    "previousClose",
    "twoHundredDayAverage",
    "trailingAnnualDividendYield",
    "payoutRatio",
    "volume24Hr",
    "regularMarketDayHigh",
    "navPrice",
    "averageDailyVolume10Day",
    "totalAssets",
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
    "lastMarket",
    "maxSupply",
    "openInterest",
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
    symbols: List[str], interval: str = "3mo", start_date: str = "", end_date: str = ""
) -> pd.DataFrame:
    """Get adjusted closing price for each stock in the list

    Parameters
    ----------
    symbols: List[str]
        List of tickers to get historical data for
    interval: str
        interval to get data from yfinance, personalized
    start_date: str
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str
        If not using interval, end date string (YYYY-MM-DD). If empty use last
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

    if start_date != "":
        end_ = date.today() if end_date == "" else date.fromisoformat(end_date)

        # Check if end date is on weekend
        if end_.weekday() >= 5:
            end_ = end_ + relativedelta(weekday=FR(-1))

        end_date = end_.strftime("%Y-%m-%d")

        # Creating temporal file name
        name = os.path.join(path, "Stocks " + start_date + " to " + end_date + ".pkl")

        # Checking if exist
        if os.path.exists(name):
            stock_closes_0 = pd.read_pickle(name)  # noqa: S301
            list_of_stocks_0 = list(set(symbols) - set(stock_closes_0.columns))
        else:
            stock_closes_0 = None
            list_of_stocks_0 = symbols

        # Download assets that are not in temporal file
        if list_of_stocks_0 == []:
            stock_closes = stock_closes_0.copy()
        else:
            stock_prices = yf.download(
                list_of_stocks_0,
                start=start_date,
                end=end_date,
                progress=False,
                group_by="ticker",
            )

    elif interval in period_choices:
        # Setting temporal file name
        name = os.path.join(
            path,
            "Stocks " + interval + " " + date.today().strftime("%Y-%m-%d") + ".pkl",
        )

        # Creating if exist
        if os.path.exists(name):
            stock_closes_0 = pd.read_pickle(name)  # noqa: S301
            list_of_stocks_0 = list(set(symbols) - set(stock_closes_0.columns))
        else:
            stock_closes_0 = None
            list_of_stocks_0 = symbols

        # Download assets that are not in temporal file
        if list_of_stocks_0 == []:
            stock_closes = stock_closes_0.copy()
        else:
            stock_prices = yf.download(
                list_of_stocks_0, period=interval, progress=False, group_by="ticker"
            )

    else:
        end_ = date.today()
        if end_.weekday() >= 5:
            end_ = end_ + relativedelta(weekday=FR(-1))
        for item in ["d", "w", "mo", "y"]:
            if interval.find(item) >= 1:
                n = int(interval[: -len(item)])
                start_ = end_ - relativedelta(days=n)
                break
        else:
            return None

        start_date = start_.strftime("%Y-%m-%d")
        end_date = end_.strftime("%Y-%m-%d")

        # Creating temporal file name
        name = os.path.join(path, "Stocks " + start_date + " to " + end_date + ".pkl")

        # Checking if temporal file exists
        if os.path.exists(name):
            stock_closes_0 = pd.read_pickle(name)  # noqa: S301
            list_of_stocks_0 = list(set(symbols) - set(stock_closes_0.columns))
        else:
            stock_closes_0 = None
            list_of_stocks_0 = symbols

        # Download assets that are not in temporal file
        if list_of_stocks_0 == []:
            stock_closes = stock_closes_0.copy()
        else:
            stock_prices = yf.download(
                list_of_stocks_0,
                start=start_date,
                end=end_date,
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

    stock_closes = stock_closes[symbols]

    return stock_closes


@log_start_end(log=logger)
def process_returns(
    data: pd.DataFrame,
    log_returns: bool = False,
    freq: str = "D",
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = "time",
) -> pd.DataFrame:
    """Process stock prices to calculate returns and delete outliers

    Parameters
    ----------
    data: pd.DataFrame
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
    stock_returns = data.copy()
    stock_returns = stock_returns.set_index(pd.DatetimeIndex(stock_returns.index))
    stock_returns.interpolate(method=method, axis=0, inplace=True)

    # Select stocks with low number of nans
    selected_stocks = np.isnan(stock_returns).sum(axis=0)
    selected_stocks = np.where(selected_stocks <= maxnan * stock_returns.shape[0])[0]
    filtered_out = [
        s
        for s in stock_returns.columns
        if s not in stock_returns.iloc[:, selected_stocks]
    ]
    if filtered_out:
        console.print(
            "The following stocks were filtered out, due to too many NaNs: "
            + ", ".join(filtered_out)
        )
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
        if freq.upper() == ["W"] and last_day.weekday() < 4:
            stock_returns = stock_returns.iloc[:-1, :]
        if (
            freq.upper() == ["M"]
            and monthrange(last_day.year, last_day.month)[1] - last_day.day <= 5
        ):
            stock_returns = stock_returns.iloc[:-1, :]

    # Calculate returns
    if log_returns is True:
        stock_returns = np.log(stock_returns)
        stock_returns = stock_returns.diff().dropna()
    else:
        stock_returns = stock_returns.pct_change().dropna()

    return stock_returns
