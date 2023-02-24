"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import logging

import numpy as np
import pandas as pd
import pandas_ta as ta

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

MAMODES = ["ema", "sma", "wma", "hma", "zlma"]
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
            As markets are most active during the opening and closing of a trading session, it makes volatility estimation more accurate.

            Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency.

            Rogers-Satchell is an estimator for measuring the volatility of securities with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term (mean return not equal to zero).

            Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.

    Returns
    -------
    pd.DataFrame: cones
        DataFrame of realized volatility quantiles.

    Example
    -------
    df = openbb.stocks.load("AAPL")
    cones_df = openbb.ta.cones(data = df, lower_q = 0.10, upper_q = 0.90)
    """

    n_days: int = 365 if is_crypto else 252

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

        def standard_deviation(data, window=30, trading_periods=n_days, clean=True):
            """Standard deviation measures how widely returns are dispersed from the average return.
            It is the most common (and biased) estimator of volatility."""
            log_return = (data["Close"] / data["Close"].shift(1)).apply(np.log)

            result = log_return.rolling(window=window, center=False).std() * np.sqrt(
                trading_periods
            )

            if clean:
                return result.dropna()

            return result

        def parkinson(data, window=30, trading_periods=n_days, clean=True):
            """Parkinson volatility uses the high and low price of the day rather than just close to close prices.
            It is useful for capturing large price movements during the day."""
            rs = (1.0 / (4.0 * np.log(2.0))) * (
                (data["High"] / data["Low"]).apply(np.log)
            ) ** 2.0

            def f(v):
                return (trading_periods * v.mean()) ** 0.5

            result = rs.rolling(window=window, center=False).apply(func=f)

            if clean:
                return result.dropna()

            return result

        def garman_klass(data, window=30, trading_periods=n_days, clean=True):
            """Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
            As markets are most active during the opening and closing of a trading session, it makes volatility estimation more accurate.
            """
            log_hl = (data["High"] / data["Low"]).apply(np.log)
            log_co = (data["Close"] / data["Open"]).apply(np.log)

            rs = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2

            def f(v):
                return (trading_periods * v.mean()) ** 0.5

            result = rs.rolling(window=window, center=False).apply(func=f)

            if clean:
                return result.dropna()

            return result

        def hodges_tompkins(data, window=30, trading_periods=n_days, clean=True):
            """Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency."""
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

        def rogers_satchell(data, window=30, trading_periods=n_days, clean=True):
            """Rogers-Satchell is an estimator for measuring the volatility of securities with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term (mean return not equal to zero).
            """

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

        def yang_zhang(data, window=30, trading_periods=n_days, clean=True):
            """Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.
            """
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
            window_rs = rs.rolling(window=window, center=False).sum() * (
                1.0 / (window - 1.0)
            )

            k = 0.34 / (1.34 + (window + 1) / (window - 1))
            result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(
                np.sqrt
            ) * np.sqrt(trading_periods)

            if clean:
                return result.dropna()

            return result

        for window in windows:
            # Looping to build a dataframe with realized volatility over each window.
            if model not in VOLATILITY_MODELS:
                print("Model not available. Available models: ", VOLATILITY_MODELS)
            elif model == "STD":
                estimator = standard_deviation(window=window, data=data)
            elif model == "Parkinson":
                estimator = parkinson(window=window, data=data)
            elif model == "Garman-Klass":
                estimator = garman_klass(window=window, data=data)
            elif model == "Hodges-Tompkins":
                estimator = hodges_tompkins(window=window, data=data)
            elif model == "Rogers-Satchell":
                estimator = rogers_satchell(window=window, data=data)
            elif model == "Yang-Zhang":
                estimator = yang_zhang(window=window, data=data)
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
        if lower_q or upper_q > 0:
            print(
                "Upper and lower quantiles should be expressed as a value between 0 and 1"
            )
        return cones_df
