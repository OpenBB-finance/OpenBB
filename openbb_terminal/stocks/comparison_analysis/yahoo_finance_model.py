"""Yahoo Finance Comparison Model"""
__docformat__ = "numpy"

import logging
import warnings
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.manifold import TSNE
from sklearn.preprocessing import normalize

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
}


@log_start_end(log=logger)
def get_historical(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
) -> pd.DataFrame:
    """Get historical prices for all comparison stocks

    Parameters
    ----------
    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date: Optional[str], optional
        End date (e.g., 2023-01-01). None defaults to today
    candle_type: str, optional
        Candle variable to compare, by default "a" for Adjusted Close. Possible values are: o, h, l, c, a, v, r

    Returns
    -------
    pd.DataFrame
        Dataframe of historical prices for all comparison stocks

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb

    Start by getting similar tickers from finviz for AAPL

    >>> similar = openbb.stocks.comparison_analysis.finviz_peers("AAPL")
    >>> hist_df = openbb.stocks.ca.hist(similar)

    We can specify a start date and an end date
    >>> hist_df_2022 = openbb.stocks.ca.hist(similar, start_date="2022-01-01", end_date="2022-12-31")
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    candle_type = candle_type.lower()
    use_returns = False
    if candle_type == "r":
        # Calculate returns based off of adjusted close
        use_returns = True
        candle_type = "a"

    # To avoid having to recursively append, just do a single yfinance call.  This will give dataframe
    # where all tickers are columns.
    similar_tickers_dataframe = yf.download(
        similar, start=start_date, progress=False, threads=False, ignore_tz=True
    )[d_candle_types[candle_type]]

    returnable = (
        similar_tickers_dataframe
        if similar_tickers_dataframe.empty
        else similar_tickers_dataframe[similar]
    )

    if use_returns:
        # To calculate the period to period return,
        # shift the dataframe by one row, then divide it into
        # the other, then subtract 1 to get a percentage, which is the return.
        shifted = returnable.shift(1)[1:]
        returnable = returnable.div(shifted) - 1

    df_similar = returnable[similar]

    if np.any(df_similar.isna()):
        nan_tickers = df_similar.columns[df_similar.isna().sum() >= 1].to_list()
        console.print(
            f"NaN values found in: {', '.join(nan_tickers)}.  Backfilling data"
        )
        df_similar = df_similar.fillna(method="bfill")

    df_similar = df_similar.dropna(axis=1, how="all")

    if end_date:
        df_similar = df_similar[df_similar.index <= end_date]
    return df_similar


@log_start_end(log=logger)
def get_correlation(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get historical price correlation. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to today
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Dataframe with correlation matrix, Dataframe with historical prices for all comparison stocks
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    df_similar = get_historical(similar, start_date, end_date, candle_type=candle_type)

    correlations = df_similar.corr()

    return correlations, df_similar


@log_start_end(log=logger)
def get_volume(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get stock volume. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date : Optional[str], optional
        End date (e.g., 2023-01-01). None defaults to today

    Returns
    -------
    pd.DataFrame
        Dataframe with volume for stock
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    df_similar = get_historical(similar, start_date, end_date, candle_type="v")
    df_similar = df_similar[df_similar.columns]
    return df_similar


@log_start_end(log=logger)
def get_1y_sp500() -> pd.DataFrame:
    """
    Gets the last year of Adj Close prices for all current SP 500 stocks.
    They are scraped daily using yfinance at https://github.com/jmaslek/daily_sp_500

    Returns
    -------
    pd.DataFrame
        DataFrame containing last 1 year of closes for all SP500 stocks.
    """
    df = pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/daily_sp_500/main/SP500_prices_1yr.csv",
        index_col=0,
    )
    df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", utc=True).dt.strftime(
        "%Y-%m-%d"
    )
    df.set_index("Date", inplace=True)
    return df


# pylint:disable=E1137,E1101


@log_start_end(log=logger)
def get_sp500_comps_tsne(
    symbol: str,
    lr: int = 200,
) -> pd.DataFrame:
    """
    Runs TSNE on SP500 tickers (along with ticker if not in SP500).
    TSNE is a method of visualing higher dimensional data
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    Note that the TSNE numbers are meaningless and will be arbitrary if run again.

    Parameters
    ----------
    symbol: str
        Ticker to get comparisons to
    lr: int
        Learning rate for TSNE

    Returns
    -------
    pd.DataFrame
        Dataframe of tickers closest to selected ticker
    """

    # Adding the type makes pylint stop yelling
    close_vals: pd.DataFrame = get_1y_sp500()

    if symbol not in close_vals.columns:
        df_symbol = yf.download(
            symbol, start=close_vals.index[0], progress=False, ignore_tz=True
        )["Adj Close"].to_frame()
        df_symbol.columns = [symbol]
        df_symbol.index = df_symbol.index.astype(str)
        close_vals = close_vals.join(df_symbol)

    close_vals = close_vals.fillna(method="bfill")
    rets = close_vals.pct_change()[1:].T
    # Future warning from sklearn.  Think 1.2 will stop printing it
    warnings.filterwarnings("ignore", category=FutureWarning)
    model = TSNE(learning_rate=lr, init="pca")
    tsne_features = model.fit_transform(normalize(rets))
    warnings.resetwarnings()
    xs = tsne_features[:, 0]
    ys = tsne_features[:, 1]

    data = pd.DataFrame({"X": xs, "Y": ys}, index=rets.index)
    x0, y0 = data.loc[symbol]
    data["dist"] = (data.X - x0) ** 2 + (data.Y - y0) ** 2
    data = data.sort_values(by="dist")

    return data
