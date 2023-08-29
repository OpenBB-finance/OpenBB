"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import logging
from typing import Optional

import numpy as np
import pandas as pd
import pandas_ta as ta

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

MAMODES = ["ema", "sma", "wma", "hma", "zlma"]

# These are parameters for the volatility models
VOLATILITY_MODELS = [
    "STD",
    "Parkinson",
    "Garman-Klass",
    "Hodges-Tompkins",
    "Rogers-Satchell",
    "Yang-Zhang",
]


@log_start_end(log=logger)
def bbands(
    data: pd.DataFrame, window: int = 15, n_std: float = 2, mamode: str = "ema"
) -> pd.DataFrame:
    """Calculate Bollinger Bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe of bollinger band data
    """
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.bbands(
            close=data[close_col],
            length=window,
            std=n_std,
            mamode=mamode,
        )
    ).dropna()


@log_start_end(log=logger)
def donchian(
    data: pd.DataFrame,
    upper_length: int = 20,
    lower_length: int = 20,
) -> pd.DataFrame:
    """Calculate Donchian Channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel

    Returns
    -------
    pd.DataFrame
        Dataframe of upper and lower channels
    """
    close_col = ta_helpers.check_columns(data, close=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.donchian(
            high=data["High"],
            low=data["Low"],
            upper_length=upper_length,
            lower_length=lower_length,
        ).dropna()
    )


@log_start_end(log=logger)
def kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
) -> pd.DataFrame:
    """Keltner Channels

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of rolling kc
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.kc(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )


@log_start_end(log=logger)
def atr(
    data: pd.DataFrame,
    window: int = 14,
    mamode: str = "ema",
    offset: int = 0,
) -> pd.DataFrame:
    """Average True Range

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of atr
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.atr(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )


@log_start_end(log=logger)
def standard_deviation(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean: bool = True,
) -> pd.DataFrame:
    """Standard deviation measures how widely returns are dispersed from the average return.
    It is the most common (and biased) estimator of volatility.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate over.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.

    Example
    -------
    >>> data = openbb.stocks.load('SPY')
    >>> df = openbb.ta.standard_deviation(data)
    """

    if window < 2:
        console.print("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["Close"] / data["Close"].shift(1)).apply(np.log)

    result = log_return.rolling(window=window, center=False).std() * np.sqrt(
        trading_periods
    )

    if clean:
        return result.dropna()

    return result


@log_start_end(log=logger)
def parkinson(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Parkinson volatility uses the high and low price of the day rather than just close to close prices.
    It is useful for capturing large price movements during the day.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate over.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.

    Example
    -------
    >>> data = openbb.stocks.load('BTC-USD')
    >>> df = openbb.ta.rvol_parkinson(data, is_crypto = True)
    """

    if window < 1:
        console.print("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    rs = (1.0 / (4.0 * np.log(2.0))) * (
        (data["High"] / data["Low"]).apply(np.log)
    ) ** 2.0

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


@log_start_end(log=logger)
def garman_klass(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
    As markets are most active during the opening and closing of a trading session.
    It makes volatility estimation more accurate.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate overn.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.

    Example
    -------
    >>> data = openbb.stocks.load('BTC-USD')
    >>> df = openbb.ta.rvol_garman_klass(data, is_crypto = True)
    """

    if window < 1:
        console.print("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_hl = (data["High"] / data["Low"]).apply(np.log)
    log_co = (data["Close"] / data["Open"]).apply(np.log)

    rs = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


@log_start_end(log=logger)
def hodges_tompkins(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
    It produces unbiased estimates and a substantial gain in efficiency.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate over.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.

    Example
    -------
    >>> data = openbb.stocks.load('BTC-USD')
    >>> df = openbb.ta.rvol_hodges_tompkins(data, is_crypto = True)
    """

    if window < 2:
        console.print("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["Close"] / data["Close"].shift(1)).apply(np.log)

    vol = log_return.rolling(window=window, center=False).std() * np.sqrt(
        trading_periods
    )

    h = window
    n = (log_return.count() - h) + 1

    adj_factor = 1.0 / (1.0 - (h / n) + ((h**2 - 1) / (3 * n**2)))

    result = vol * adj_factor

    if clean:
        return result.dropna()

    return result


@log_start_end(log=logger)
def rogers_satchell(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.Series:
    """Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
    Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
    mean return not equal to zero.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate over.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.Series : results
        Pandas Series with results.

    Example
    -------
    >>> data = openbb.stocks.load('BTC-USD')
    >>> df = openbb.ta.rvol_rogers_satchell(data, is_crypto = True)
    """

    if window < 1:
        console.print("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["High"] / data["Open"]).apply(np.log)
    log_lo = (data["Low"] / data["Open"]).apply(np.log)
    log_co = (data["Close"] / data["Open"]).apply(np.log)

    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def yang_zhang(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
    It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 30]
        Length of window to calculate standard deviation.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.
    is_crypto : bool [default: False]
        If true, trading_periods is defined as 365.
    clean : bool [default: True]
        Whether to clean the data or not by dropping NaN values.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.

    Example
    -------
    >>> data = openbb.stocks.load('BTC-USD')
    >>> df = openbb.ta.rvol_yang_zhang(data, is_crypto = True)
    """

    if window < 2:
        console.print("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        console.print("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["High"] / data["Open"]).apply(np.log)
    log_lo = (data["Low"] / data["Open"]).apply(np.log)
    log_co = (data["Close"] / data["Open"]).apply(np.log)

    log_oc = (data["Open"] / data["Close"].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2

    log_cc = (data["Close"] / data["Close"].shift(1)).apply(np.log)
    log_cc_sq = log_cc**2

    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)

    close_vol = log_cc_sq.rolling(window=window, center=False).sum() * (
        1.0 / (window - 1.0)
    )
    open_vol = log_oc_sq.rolling(window=window, center=False).sum() * (
        1.0 / (window - 1.0)
    )
    window_rs = rs.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))

    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(
        trading_periods
    )

    if clean:
        return result.dropna()

    return result


@log_start_end(log=logger)
def cones(
    data: pd.DataFrame,
    lower_q: float = 0.25,
    upper_q: float = 0.75,
    is_crypto: bool = False,
    model: str = "STD",
) -> pd.DataFrame:
    """Returns a DataFrame of realized volatility quantiles.

    Parameters
    ---------
    data: pd.DataFrame
        DataFrame of the OHLC data.
    lower_q: float (default = 0.25)
        The lower quantile to calculate the realized volatility over time for.
    upper_q: float (default = 0.75)
        The upper quantile to calculate the realized volatility over time for.
    is_crypto: bool (default = False)
        If true, volatility is calculated for 365 days instead of 252.
    model: str (default = "STD")
        The model to use for volatility calculation. Choices are:
        ["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"]

            Standard deviation measures how widely returns are dispersed from the average return.
            It is the most common (and biased) estimator of volatility.

            Parkinson volatility uses the high and low price of the day rather than just close to close prices.
            It is useful for capturing large price movements during the day.

            Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
            As markets are most active during the opening and closing of a trading session,
            it makes volatility estimation more accurate.

            Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency.

            Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
            mean return not equal to zero.

            Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.

    Returns
    -------
    pd.DataFrame: cones
        DataFrame of realized volatility quantiles.

    Example
    -------
    >>> df = openbb.stocks.load("AAPL")
    >>> cones_df = openbb.ta.cones(data = df, lower_q = 0.10, upper_q = 0.90)

    >>> cones_df = openbb.ta.cones(df,0.15,0.85,False,"Garman-Klass")

    """
    estimator = pd.DataFrame()

    if lower_q > upper_q:
        lower_q, upper_q = upper_q, lower_q

    if (lower_q >= 1) or (upper_q >= 1):
        console.print("Error: lower_q and upper_q must be between 0 and 1")
        cones_df = pd.DataFrame()
        return cones_df

    try:
        lower_q_label = str(int(lower_q * 100))
        upper_q_label = str(int(upper_q * 100))
        quantiles = [lower_q, upper_q]
        windows = [3, 10, 30, 60, 90, 120, 150, 180, 210, 240, 300, 360]
        min_ = []
        max_ = []
        median = []
        top_q = []
        bottom_q = []
        realized = []
        data = data.sort_index(ascending=False)

        for window in windows:
            # Looping to build a dataframe with realized volatility over each window.
            if model not in VOLATILITY_MODELS:
                console.print(
                    "Model not available. Available models: ", VOLATILITY_MODELS
                )
            elif model == "STD":
                estimator = standard_deviation(
                    window=window, data=data, is_crypto=is_crypto
                )
            elif model == "Parkinson":
                estimator = parkinson(window=window, data=data, is_crypto=is_crypto)
            elif model == "Garman-Klass":
                estimator = garman_klass(window=window, data=data, is_crypto=is_crypto)
            elif model == "Hodges-Tompkins":
                estimator = hodges_tompkins(
                    window=window, data=data, is_crypto=is_crypto
                )
            elif model == "Rogers-Satchell":
                estimator = rogers_satchell(
                    window=window, data=data, is_crypto=is_crypto
                )
            elif model == "Yang-Zhang":
                estimator = yang_zhang(window=window, data=data, is_crypto=is_crypto)
            min_.append(estimator.min())
            max_.append(estimator.max())
            median.append(estimator.median())
            top_q.append(estimator.quantile(quantiles[1]))
            bottom_q.append(estimator.quantile(quantiles[0]))
            realized.append(estimator[-1])
        df_ = [realized, min_, bottom_q, median, top_q, max_]
        df_windows = windows
        df = pd.DataFrame(df_, columns=df_windows)
        df = df.rename(
            index={
                0: "Realized",
                1: "Min",
                2: "Lower " f"{lower_q_label}" "%",
                3: "Median",
                4: "Upper " f"{upper_q_label}" "%",
                5: "Max",
            }
        )
        cones_df = df.copy()
        return cones_df.transpose()

    except Exception:
        cones_df = pd.DataFrame()
        return cones_df
