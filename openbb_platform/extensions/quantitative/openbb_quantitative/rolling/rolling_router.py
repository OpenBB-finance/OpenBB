"""Rolling submenu of quantitative models for rolling statistics."""

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from pydantic import NonNegativeFloat, PositiveInt

router = Router(prefix="/rolling")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Mean.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.skew(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def skew(
    data: list[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[list[Data]]:
    """Get Rolling Skew.

    Skew is a statistical measure that reveals the degree of asymmetry of a distribution around its mean.
    Positive skewness indicates a distribution with an extended tail to the right, while negative skewness shows a tail
    that stretches left. Understanding skewness can provide insights into potential biases in data and help anticipate
    the nature of future data points. It's particularly useful for identifying the likelihood of extreme outcomes in
    financial returns, enabling more informed decision-making based on the distribution's shape over a specified period.

    Parameters
    ----------
    data : list[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.
    index : str, optional
        Index column name, by default "date"

    Returns
    -------
    OBBject[list[Data]]
        Rolling skew.

    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import skew_

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    series_target.name = f"rolling_skew_{window}"
    validate_window(series_target, window)
    results = (
        series_target.rolling(window).apply(skew_).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Variance.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.variance(data=returns, target="close", window=252)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def variance(
    data: list[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[list[Data]]:
    """
    Calculate the rolling variance of a target column within a given window size.

    Variance measures the dispersion of a set of data points around their mean. It is a key metric for
    assessing the volatility and stability of financial returns or other time series data over a specified rolling window.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate variance.
    window: PositiveInt
        The number of observations used for calculating the rolling measure.
    index: str, optional
        The name of the index column, default is "date".

    Returns
    -------
    OBBject[list[Data]]
        An object containing the rolling variance values.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import var_

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    series_target.name = f"rolling_var_{window}"
    validate_window(series_target, window)
    results = series_target.rolling(window).apply(var_).dropna().reset_index(drop=False)
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Standard Deviation.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.stdev(data=returns, target="close", window=252)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def stdev(
    data: list[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[list[Data]]:
    """
    Calculate the rolling standard deviation of a target column within a given window size.

    Standard deviation is a measure of the amount of variation or dispersion of a set of values.
    It is widely used to assess the risk and volatility of financial returns or other time series data
    over a specified rolling window.  It is the square root of the variance.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate standard deviation.
    window: PositiveInt
        The number of observations used for calculating the rolling measure.
    index: str, optional
        The name of the index column, default is "date".

    Returns
    -------
    OBBject[list[Data]]
        An object containing the rolling standard deviation values.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import std_dev_

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    series_target.name = f"rolling_stdev_{window}"
    validate_window(series_target, window)
    results = (
        series_target.rolling(window).apply(std_dev_).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Kurtosis.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.kurtosis(data=returns, target="close", window=252)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def kurtosis(
    data: list[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[list[Data]]:
    """
    Calculate the rolling kurtosis of a target column within a given window size.

    Kurtosis measures the "tailedness" of the probability distribution of a real-valued random variable.
    High kurtosis indicates a distribution with heavy tails (outliers), suggesting a higher risk of extreme outcomes.
    Low kurtosis indicates a distribution with lighter tails (less outliers), suggesting less risk of extreme outcomes.
    This function helps in assessing the risk of outliers in financial returns or other time series data over a specified
    rolling window.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate kurtosis.
    window: PositiveInt
        The number of observations used for calculating the rolling measure.
    index: str, optional
        The name of the index column, default is "date".

    Returns
    -------
    OBBject[list[Data]]
        An object containing the rolling kurtosis values.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import kurtosis_

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    series_target.name = f"rolling_kurtosis_{window}"
    validate_window(series_target, window)
    results = (
        series_target.rolling(window).apply(kurtosis_).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Quantile.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.quantile(data=returns, target="close", window=252, quantile_pct=0.25)',
                'obb.quantitative.rolling.quantile(data=returns, target="close", window=252, quantile_pct=0.75)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def quantile(
    data: list[Data],
    target: str,
    window: PositiveInt = 21,
    quantile_pct: NonNegativeFloat = 0.5,
    index: str = "date",
) -> OBBject[list[Data]]:
    """
    Calculate the rolling quantile of a target column within a given window size at a specified quantile percentage.

    Quantiles are points dividing the range of a probability distribution into  intervals with equal probabilities,
    or dividing the  sample in the same way. This function is useful for understanding the distribution of data
    within a specified window, allowing for analysis of trends, identification of outliers, and assessment of risk.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate the quantile.
    window: PositiveInt
        The number of observations used for calculating the rolling measure.
    quantile_pct: NonNegativeFloat, optional
        The quantile percentage to calculate (e.g., 0.5 for median), default is 0.5.
    index: str, optional
        The name of the index column, default is "date".

    Returns
    -------
    OBBject[list[Data]]
        An object containing the rolling quantile values with the median.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from pandas import concat

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    roll = series_target.rolling(window)
    df_median = roll.median()
    df_quantile = roll.quantile(quantile_pct)
    results = (
        concat(
            [df_median, df_quantile],
            axis=1,
            keys=[
                f"rolling_median_{window}",
                f"rolling_quantile_{quantile_pct}_{window}",
            ],
        )
        .dropna()
        .reset_index(drop=False)
    )

    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Mean.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.rolling.mean(data=returns, target="close", window=252)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "window": 2,
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def mean(
    data: list[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[list[Data]]:
    """Calculate the rolling average of a target column within a given window size.

    The rolling mean is a simple moving average that calculates the average of a target variable over a specified window.
    This function is widely used in financial analysis to smooth short-term fluctuations and highlight longer-term trends
    or cycles in time series data.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate the mean.
    window: PositiveInt
        The number of observations used for calculating the rolling measure.
    index: str, optional
        The name of the index column, default is "date".

    Returns
    -------
    OBBject[list[Data]]
        An object containing the rolling mean values.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import mean_

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    series_target.name = f"rolling_mean_{window}"
    validate_window(series_target, window)
    results = (
        series_target.rolling(window).apply(mean_).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

    return OBBject(results=results)
