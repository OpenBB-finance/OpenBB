"""Technical Analysis Helpers."""

import warnings
from typing import Any, Literal, Optional, Tuple

import numpy as np
import pandas as pd

_warn = warnings.warn


def parkinson(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Parkinson volatility.

    Uses the high and low price of the day rather than just close to close prices.
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
    """
    if window < 1:
        _warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    rs = (1.0 / (4.0 * np.log(2.0))) * (
        (data["high"] / data["low"]).apply(np.log)
    ) ** 2.0

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def standard_deviation(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean: bool = True,
) -> pd.DataFrame:
    """Standard deviation.

    Measures how widely returns are dispersed from the average return.
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
    """
    if window < 2:
        _warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["close"] / data["close"].shift(1)).apply(np.log)

    result = log_return.rolling(window=window, center=False).std() * np.sqrt(
        trading_periods
    )

    if clean:
        return result.dropna()

    return result


def garman_klass(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Garman-Klass volatility.

    Extends Parkinson volatility by taking into account the opening and closing price.
    As markets are most active during the opening and closing of a trading session.
    It makes volatility estimation more accurate.

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
    """
    if window < 1:
        _warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_hl = (data["high"] / data["low"]).apply(np.log)
    log_co = (data["close"] / data["open"]).apply(np.log)

    rs = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def hodges_tompkins(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.DataFrame:
    """Hodges-Tompkins volatility.

    Is a bias correction for estimation using an overlapping data sample.
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
    >>> data = obb.equity.price.historical('BTC-USD')
    >>> df = obb.technical.hodges_tompkins(data, is_crypto = True)
    """
    if window < 2:
        _warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["close"] / data["close"].shift(1)).apply(np.log)

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


def rogers_satchell(
    data: pd.DataFrame,
    window: int = 30,
    trading_periods: Optional[int] = None,
    is_crypto: bool = False,
    clean=True,
) -> pd.Series:
    """Rogers-Satchell Estimator.

    Is an estimator for measuring the volatility with an average return not equal to zero.
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
    """
    if window < 1:
        _warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["high"] / data["open"]).apply(np.log)
    log_lo = (data["low"] / data["open"]).apply(np.log)
    log_co = (data["close"] / data["open"]).apply(np.log)

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
    """Yang-Zhang Volatility.

    Is the combination of the overnight (close-to-open volatility).
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
    """
    if window < 2:
        _warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        _warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["high"] / data["open"]).apply(np.log)
    log_lo = (data["low"] / data["open"]).apply(np.log)
    log_co = (data["close"] / data["open"]).apply(np.log)

    log_oc = (data["open"] / data["close"].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2

    log_cc = (data["close"] / data["close"].shift(1)).apply(np.log)
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


def calculate_cones(
    data: pd.DataFrame,
    lower_q: float,
    upper_q: float,
    is_crypto: bool,
    model: Literal[
        "STD",
        "Parkinson",
        "Garman-Klass",
        "Hodges-Tompkins",
        "Rogers-Satchell",
        "Yang-Zhang",
    ],
    trading_periods: Optional[int] = None,
) -> pd.DataFrame:
    """Calculate Cones."""
    estimator = pd.DataFrame()

    if lower_q > upper_q:
        lower_q, upper_q = upper_q, lower_q

    if (lower_q >= 1) or (upper_q >= 1):
        raise ValueError("Error: lower_q and upper_q must be between 0 and 1")

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
    allowed_windows = []
    data = data.sort_index(ascending=True)

    model_functions = {
        "STD": standard_deviation,
        "Parkinson": parkinson,
        "Garman-Klass": garman_klass,
        "Hodges-Tompkins": hodges_tompkins,
        "Rogers-Satchell": rogers_satchell,
        "Yang-Zhang": yang_zhang,
    }

    for window in windows:
        estimator = model_functions[model](  # type: ignore
            window=window,
            data=data,
            is_crypto=is_crypto,
            trading_periods=trading_periods,
        )

        if estimator.empty:
            continue

        min_.append(estimator.min())  # type: ignore
        max_.append(estimator.max())  # type: ignore
        median.append(estimator.median())  # type: ignore
        top_q.append(estimator.quantile(quantiles[1]))  # type: ignore
        bottom_q.append(estimator.quantile(quantiles[0]))  # type: ignore
        realized.append(estimator[-1])  # type: ignore

        allowed_windows.append(window)

    df_ = [realized, min_, bottom_q, median, top_q, max_]
    df_windows = allowed_windows
    df = pd.DataFrame(df_, columns=df_windows)
    df = df.rename(
        index={
            0: "realized",
            1: "min",
            2: f"lower_{lower_q_label}%",
            3: "median",
            4: f"upper_{upper_q_label}%",
            5: "max",
        }
    )
    cones_df = df.copy()
    return cones_df.transpose().reset_index().rename(columns={"index": "window"})


def clenow_momentum(
    values: pd.Series, window: int = 90
) -> Tuple[float, float, pd.Series]:
    """Clenow Volatility Adjusted Momentum.

    This is defined as the regression coefficient on log prices multiplied by the R^2
    value of the regression.

    Parameters
    ----------
    values: pd.Series
        Values to perform regression for
    window: int
        Length of look back period

    Returns
    -------
    float:
        R2 of fit to log data
    float:
        Coefficient of linear regression
    pd.Series:
        Values for best fit line
    """
    from sklearn.linear_model import (  # pylint: disable=import-outside-toplevel  # type: ignore
        LinearRegression,
    )

    if len(values) < window:
        raise ValueError(f"Calculation asks for at least last {window} days of data")

    values = values[-window:]

    y = np.log(values)
    X = np.arange(len(y)).reshape(-1, 1)

    lr = LinearRegression()
    lr.fit(X, y)

    r2 = lr.score(X, y)
    coef = lr.coef_[0]
    annualized_coef = (np.exp(coef) ** 252) - 1

    return r2, annualized_coef, pd.Series(lr.predict(X))


def calculate_fib_levels(
    data: pd.DataFrame,
    close_col: str,
    limit: int = 120,
    start_date: Optional[Any] = None,
    end_date: Optional[Any] = None,
) -> Tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp, float, float, str]:
    """Calculate Fibonacci levels.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of prices
    close_col : str
        Column name of close prices
    limit : int
        Days to look back for retracement
    start_date : Any
        Custom start date for retracement
    end_date : Any
        Custom end date for retracement

    Returns
    -------
    df : pd.DataFrame
        Dataframe of fib levels
    min_date: pd.Timestamp
        Date of min point
    max_date: pd.Timestamp:
        Date of max point
    min_pr: float
        Price at min point
    max_pr: float
        Price at max point
    """
    if close_col not in data.columns:
        raise ValueError(f"Column {close_col} not in data")

    if start_date and end_date:
        if start_date not in data.index:
            date0 = data.index[data.index.get_indexer([end_date], method="nearest")[0]]
            _warn(f"Start date not in data.  Using nearest: {date0}")
        else:
            date0 = start_date
        if end_date not in data.index:
            date1 = data.index[data.index.get_indexer([end_date], method="nearest")[0]]
            _warn(f"End date not in data.  Using nearest: {date1}")
        else:
            date1 = end_date

        data0 = data.loc[date0, close_col]
        data1 = data.loc[date1, close_col]

        min_pr = min(data0, data1)
        max_pr = max(data0, data1)

        if min_pr == data0:
            min_date = date0
            max_date = date1
        else:
            min_date = date1
            max_date = date0
    else:
        data_to_use = data.iloc[-limit:, :][close_col]

        min_pr = data_to_use.min()
        min_date = data_to_use.idxmin()
        max_pr = data_to_use.max()
        max_date = data_to_use.idxmax()

    fib_levels = [0, 0.235, 0.382, 0.5, 0.618, 0.65, 1]

    lvl_text: str = "left" if min_date < max_date else "right"
    if min_date > max_date:
        min_date, max_date = max_date, min_date
        min_pr, max_pr = max_pr, min_pr

    price_dif = max_pr - min_pr

    levels = [
        round(max_pr - price_dif * f_lev, (2 if f_lev > 1 else 4))
        for f_lev in fib_levels
    ]

    df = pd.DataFrame()
    df["Level"] = fib_levels
    df["Level"] = df["Level"].apply(lambda x: str(x * 100) + "%")
    df["Price"] = levels

    return df, min_date, max_date, min_pr, max_pr, lvl_text
