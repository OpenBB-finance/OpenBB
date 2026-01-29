"""Technical Analysis Helpers."""

# pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments

from typing import TYPE_CHECKING, Any, Literal
from warnings import warn

if TYPE_CHECKING:
    from pandas import DataFrame, Series, Timestamp


def validate_data(data: list, length: int | list[int]) -> None:
    """验证数据。"""
    if isinstance(length, int):
        length = [length]
    for item in length:
        if item > len(data):
            raise ValueError(
                f"Data length is less than required by parameters: {max(length)}"
            )


def parkinson(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean=True,
) -> "DataFrame":
    """计算帕金森波动率。

    使用当天的最高价和最低价，而不仅仅是收盘价到收盘价。
    它对于捕捉当天的价格大幅波动很有用。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    DataFrame : results
        包含结果的数据框。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log

    if window < 1:
        warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    rs = (1.0 / (4.0 * log(2.0))) * ((data["high"] / data["low"]).apply(log)) ** 2.0

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def standard_deviation(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean: bool = True,
) -> "DataFrame":
    """计算标准差。

    衡量回报从平均回报分散的程度。
    它是最常见（且有偏差）的波动率估计量。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    DataFrame : results
        包含结果的数据框。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log, sqrt

    if window < 2:
        warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["close"] / data["close"].shift(1)).apply(log)

    result = log_return.rolling(window=window, center=False).std() * sqrt(
        trading_periods
    )

    if clean:
        return result.dropna()

    return result


def garman_klass(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean=True,
) -> "DataFrame":
    """计算加曼-克拉斯波动率。

    通过考虑开盘价和收盘价扩展了帕金森波动率。
    由于市场在交易时段的开盘和收盘期间最为活跃。
    它使波动率估计更加准确。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    DataFrame : results
        包含结果的数据框。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log

    if window < 1:
        warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_hl = (data["high"] / data["low"]).apply(log)
    log_co = (data["close"] / data["open"]).apply(log)

    rs = 0.5 * log_hl**2 - (2 * log(2) - 1) * log_co**2

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def hodges_tompkins(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean=True,
) -> "DataFrame":
    """计算霍奇斯-汤普金斯波动率。

    是对使用重叠数据样本进行估计的偏差校正。
    它产生无偏估计并显着提高效率。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    DataFrame : results
        包含结果的数据框。

    Example
    -------
    >>> data = obb.equity.price.historical('BTC-USD')
    >>> df = obb.technical.hodges_tompkins(data, is_crypto = True)
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log, sqrt

    if window < 2:
        warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_return = (data["close"] / data["close"].shift(1)).apply(log)

    vol = log_return.rolling(window=window, center=False).std() * sqrt(trading_periods)

    h = window
    n = (log_return.count() - h) + 1

    adj_factor = 1.0 / (1.0 - (h / n) + ((h**2 - 1) / (3 * n**2)))

    result = vol * adj_factor

    if clean:
        return result.dropna()

    return result


def rogers_satchell(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean=True,
) -> "Series":
    """计算罗杰斯-萨切尔估计量。

    是用于测量平均回报不等于零的波动率的估计量。
    与帕金森和加曼-克拉斯估计量不同，罗杰斯-萨切尔包含漂移项，
    平均回报不等于零。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    Series : results
        包含结果的熊猫系列。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log

    if window < 1:
        warn("Error: Window must be at least 1, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["high"] / data["open"]).apply(log)
    log_lo = (data["low"] / data["open"]).apply(log)
    log_co = (data["close"] / data["open"]).apply(log)

    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)

    def f(v):
        return (trading_periods * v.mean()) ** 0.5

    result = rs.rolling(window=window, center=False).apply(func=f)

    if clean:
        return result.dropna()

    return result


def yang_zhang(
    data: "DataFrame",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean=True,
) -> "DataFrame":
    """计算杨-张波动率。

    是隔夜（收盘到开盘波动率）的组合。
    它是罗杰斯-萨切尔波动率和开盘到收盘波动率的加权平均值。

    Parameters
    ----------
    data : DataFrame
        OHLC 价格数据框。
    window : int [default: 30]
        用于计算标准差的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。
    is_crypto : bool [default: False]
        如果为 True，trading_periods 定义为 365。
    clean : bool [default: True]
        由于丢弃 NaN 值，是否清理数据。

    Returns
    -------
    DataFrame : results
        包含结果的数据框。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log, sqrt

    if window < 2:
        warn("Error: Window must be at least 2, defaulting to 30.")
        window = 30

    if trading_periods and is_crypto:
        warn("is_crypto is overridden by trading_periods.")

    if not trading_periods:
        trading_periods = 365 if is_crypto else 252

    log_ho = (data["high"] / data["open"]).apply(log)
    log_lo = (data["low"] / data["open"]).apply(log)
    log_co = (data["close"] / data["open"]).apply(log)

    log_oc = (data["open"] / data["close"].shift(1)).apply(log)
    log_oc_sq = log_oc**2

    log_cc = (data["close"] / data["close"].shift(1)).apply(log)
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
    result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(sqrt) * sqrt(
        trading_periods
    )

    if clean:
        return result.dropna()

    return result


def calculate_cones(
    data: "DataFrame",
    lower_q: float,
    upper_q: float,
    is_crypto: bool,
    model: Literal[
        "std",
        "parkinson",
        "garman_klass",
        "hodges_tompkins",
        "rogers_satchell",
        "yang_zhang",
    ],
    trading_periods: int | None = None,
) -> "DataFrame":
    """计算锥体。"""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    estimator = DataFrame()

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
        "std": standard_deviation,
        "parkinson": parkinson,
        "garman_klass": garman_klass,
        "hodges_tompkins": hodges_tompkins,
        "rogers_satchell": rogers_satchell,
        "yang_zhang": yang_zhang,
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
        realized.append(estimator.iloc[-1])  # type: ignore

        allowed_windows.append(window)

    df_ = [realized, min_, bottom_q, median, top_q, max_]
    df_windows = allowed_windows
    df = DataFrame(df_, columns=df_windows)
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
    values: "Series", window: int = 90
) -> tuple[float, float, "Series"]:
    """Clenow 波动率调整动量。

    这被定义为对数价格的回归系数乘以 R^2
    回归值。

    Parameters
    ----------
    values: Series
        用于执行回归的值
    window: int
        回溯期长度

    Returns
    -------
    float:
        对数数据的 R2 拟合
    float:
        线性回归系数
    Series:
        最佳拟合线的值
    """
    # pylint: disable=import-outside-toplevel
    from numpy import arange, exp, log
    from pandas import Series
    from sklearn.linear_model import LinearRegression

    if len(values) < window:
        raise ValueError(f"Calculation asks for at least last {window} days of data")

    values = values[-window:]

    y = log(values)
    X = arange(len(y)).reshape(-1, 1)  # pylint: disable=invalid-name

    lr = LinearRegression()
    lr.fit(X, y)

    r2 = lr.score(X, y)
    coef = lr.coef_[0]
    annualized_coef = (exp(coef) ** 252) - 1

    return r2, annualized_coef, Series(lr.predict(X))


def calculate_fib_levels(
    data: "DataFrame",
    close_col: str,
    limit: int = 120,
    start_date: Any | None = None,
    end_date: Any | None = None,
) -> tuple["DataFrame", "Timestamp", "Timestamp", float, float, str]:
    """计算斐波那契水平。

    Parameters
    ----------
    data : DataFrame
        价格数据框
    close_col : str
        收盘价的列名
    limit : int
        回溯天数以进行回撤
    start_date : Any
        回撤的自定义开始日期
    end_date : Any
        回撤的自定义结束日期

    Returns
    -------
    df : DataFrame
        fib 水平的数据框
    min_date: Timestamp
        最小点的日期
    max_date: Timestamp:
        最大点的日期
    min_pr: float
        最小点的价格
    max_pr: float
        最大点的价格
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    if close_col not in data.columns:
        raise ValueError(f"Column {close_col} not in data")

    if start_date and end_date:
        if start_date not in data.index:
            date0 = data.index[data.index.get_indexer([end_date], method="nearest")[0]]
            warn(f"Start date not in data.  Using nearest: {date0}")
        else:
            date0 = start_date
        if end_date not in data.index:
            date1 = data.index[data.index.get_indexer([end_date], method="nearest")[0]]
            warn(f"End date not in data.  Using nearest: {date1}")
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

    df = DataFrame()
    df["Level"] = fib_levels
    df["Level"] = df["Level"].apply(lambda x: str(x * 100) + "%")
    df["Price"] = levels

    return df, min_date, max_date, min_pr, max_pr, lvl_text
