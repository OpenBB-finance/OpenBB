"""Rolling submenu of quantitative models for rolling statistics."""

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from pydantic import NonNegativeFloat

router = Router(prefix="/stats")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Skewness.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.skew(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def skew(
    data: list[Data],
    target: str,
) -> OBBject[list[Data]]:
    """Get the skew of the data set.

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
    from openbb_quantitative.statistics import skew_
    from pandas import DataFrame

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = DataFrame([skew_(series_target)], columns=["skew"])
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Variance.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.variance(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def variance(data: list[Data], target: str) -> OBBject[list[Data]]:
    """Calculate the  variance of a target column.

    Variance measures the dispersion of a set of data points around their mean. It is a key metric for
    assessing the volatility and stability of financial returns or other time series data.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate variance.

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
    from openbb_quantitative.statistics import var_
    from pandas import DataFrame

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = DataFrame([var_(series_target)], columns=["variance"])
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Standard Deviation.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.stdev(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def stdev(data: list[Data], target: str) -> OBBject[list[Data]]:
    """Calculate the rolling standard deviation of a target column.

    Standard deviation is a measure of the amount of variation or dispersion of a set of values.
    It is widely used to assess the risk and volatility of financial returns or other time series data
    It is the square root of the variance.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate standard deviation.

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
    from openbb_quantitative.statistics import std_dev_
    from pandas import DataFrame

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = DataFrame([std_dev_(series_target)], columns=["stdev"])
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Kurtosis.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.kurtosis(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def kurtosis(data: list[Data], target: str) -> OBBject[list[Data]]:
    """Calculate the rolling kurtosis of a target column.

    Kurtosis measures the "tailedness" of the probability distribution of a real-valued random variable.
    High kurtosis indicates a distribution with heavy tails (outliers), suggesting a higher risk of extreme outcomes.
    Low kurtosis indicates a distribution with lighter tails (less outliers), suggesting less risk of extreme outcomes.
    This function helps in assessing the risk of outliers in financial returns or other time series data.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate kurtosis.

    Returns
    -------
    OBBject[list[Data]]
        An object containing the kurtosis value
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.statistics import kurtosis_
    from pandas import DataFrame

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = DataFrame([kurtosis_(series_target)], columns=["kurtosis"])
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Quantile.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.quantile(data=returns, target="close", quantile_pct=0.75)',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
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
    quantile_pct: NonNegativeFloat = 0.5,
) -> OBBject[list[Data]]:
    """Calculate the quantile of a target column at a specified quantile percentage.

    Quantiles are points dividing the range of a probability distribution into  intervals with equal probabilities,
    or dividing the  sample in the same way.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate the quantile.
    quantile_pct: NonNegativeFloat, optional
        The quantile percentage to calculate (e.g., 0.5 for median), default is 0.5.

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
    from pandas import DataFrame

    df = basemodel_to_df(
        data,
    )
    series_target = get_target_column(df, target)
    results = DataFrame(
        [series_target.quantile(quantile_pct)], columns=[f"{quantile_pct}_quantile"]
    )
    results = df_to_basemodel(results)
    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Mean.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.stats.mean(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            }
        ),
    ],
)
def mean(
    data: list[Data],
    target: str,
) -> OBBject[list[Data]]:
    """Calculate the average of a target column.

    The rolling mean is a simple moving average that calculates the average of a target variable.
    This function is widely used in financial analysis to smooth short-term fluctuations and highlight longer-term trends
    or cycles in time series data.

    Parameters
    ----------
    data: list[Data]
        The time series data as a list of data points.
    target: str
        The name of the column for which to calculate the mean.

    Returns
    -------
        OBBject[list[Data]]
            An object containing the mean value.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.statistics import mean_
    from pandas import DataFrame

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = DataFrame([mean_(series_target)], columns=["mean"])
    results = df_to_basemodel(results)

    return OBBject(results=results)
