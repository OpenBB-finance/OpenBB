"""Quantitative rolling-statistics commands."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt

router = Router(
    prefix="/rolling", description="Quantitative rolling-statistics commands."
)


class RollingSkewQueryParams(QueryParams):
    """Query parameters for the rolling skew endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "skew")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingSkewData(Data):
    """One rolling skew observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    skew: float = Field(description="Rolling skew value.")


class RollingVarianceQueryParams(QueryParams):
    """Query parameters for the rolling variance endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "variance")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingVarianceData(Data):
    """One rolling variance observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    variance: float = Field(description="Rolling variance value.")


class RollingStdevQueryParams(QueryParams):
    """Query parameters for the rolling standard deviation endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "stdev")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingStdevData(Data):
    """One rolling standard deviation observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    stdev: float = Field(description="Rolling standard deviation value.")


class RollingKurtosisQueryParams(QueryParams):
    """Query parameters for the rolling kurtosis endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "kurtosis")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingKurtosisData(Data):
    """One rolling kurtosis observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    kurtosis: float = Field(description="Rolling kurtosis value.")


class RollingMeanQueryParams(QueryParams):
    """Query parameters for the rolling mean endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "mean")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingMeanData(Data):
    """One rolling mean observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    mean: float = Field(description="Rolling mean value.")


class RollingQuantileQueryParams(QueryParams):
    """Query parameters for the rolling quantile endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "median", "quantile")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    window: PositiveInt = Field(
        default=21, description="Number of observations in each rolling window."
    )
    quantile_pct: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Quantile to compute, between 0 and 1.",
    )
    index: str = Field(default="date", description="Name of the index column.")


class RollingQuantileData(Data):
    """One rolling quantile observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    median: float = Field(description="Rolling median value.")
    quantile: float = Field(description="Rolling quantile value.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def skew(params: RollingSkewQueryParams) -> OBBject[list[RollingSkewData]]:
    """Calculate the rolling skew of a target column over a moving window.

    Skew measures the asymmetry of a distribution about its mean. Positive skew
    indicates a longer right tail, while negative skew indicates a longer left tail.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import skew_

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    rolled = series.rolling(params.window).apply(skew_).dropna()
    frame = DataFrame({"date": rolled.index, "skew": rolled.to_numpy()})
    out = [
        RollingSkewData(date=record["date"], skew=float(record["skew"]))
        for record in frame.to_dict(orient="records")
    ]
    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def variance(
    params: RollingVarianceQueryParams,
) -> OBBject[list[RollingVarianceData]]:
    """Calculate the rolling variance of a target column over a moving window.

    Variance measures the dispersion of a set of data points around their mean. It is
    a key metric for assessing the volatility and stability of a time series.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import var_

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    rolled = series.rolling(params.window).apply(var_).dropna()
    frame = DataFrame({"date": rolled.index, "variance": rolled.to_numpy()})
    out = [
        RollingVarianceData(date=record["date"], variance=float(record["variance"]))
        for record in frame.to_dict(orient="records")
    ]
    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def stdev(params: RollingStdevQueryParams) -> OBBject[list[RollingStdevData]]:
    """Calculate the rolling standard deviation of a target column over a moving window.

    Standard deviation measures the amount of variation or dispersion of a set of
    values. It is the square root of the variance and is widely used to assess risk.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import std_dev_

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    rolled = series.rolling(params.window).apply(std_dev_).dropna()
    frame = DataFrame({"date": rolled.index, "stdev": rolled.to_numpy()})
    out = [
        RollingStdevData(date=record["date"], stdev=float(record["stdev"]))
        for record in frame.to_dict(orient="records")
    ]
    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def kurtosis(
    params: RollingKurtosisQueryParams,
) -> OBBject[list[RollingKurtosisData]]:
    """Calculate the rolling kurtosis of a target column over a moving window.

    Kurtosis measures the tailedness of a distribution. High kurtosis indicates heavy
    tails and a higher risk of extreme outcomes, while low kurtosis indicates the
    opposite.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import kurtosis_

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    rolled = series.rolling(params.window).apply(kurtosis_).dropna()
    frame = DataFrame({"date": rolled.index, "kurtosis": rolled.to_numpy()})
    out = [
        RollingKurtosisData(date=record["date"], kurtosis=float(record["kurtosis"]))
        for record in frame.to_dict(orient="records")
    ]
    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def mean(params: RollingMeanQueryParams) -> OBBject[list[RollingMeanData]]:
    """Calculate the rolling mean of a target column over a moving window.

    The rolling mean is a simple moving average that smooths short-term fluctuations
    and highlights longer-term trends or cycles in a time series.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window
    from openbb_quantitative.statistics import mean_

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    rolled = series.rolling(params.window).apply(mean_).dropna()
    frame = DataFrame({"date": rolled.index, "mean": rolled.to_numpy()})
    out = [
        RollingMeanData(date=record["date"], mean=float(record["mean"]))
        for record in frame.to_dict(orient="records")
    ]
    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "window": 20,
                "data": APIEx.mock_data("timeseries", 60),
            }
        )
    ],
)
def quantile(
    params: RollingQuantileQueryParams,
) -> OBBject[list[RollingQuantileData]]:
    """Calculate the rolling quantile of a target column over a moving window.

    Quantiles divide the range of a distribution into intervals with equal
    probabilities. This command returns the rolling median alongside the requested
    quantile for analyzing trends, outliers, and risk.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import concat

    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    roll = series.rolling(params.window)
    result = (
        concat(
            [
                roll.median().rename("median"),
                roll.quantile(params.quantile_pct).rename("quantile"),
            ],
            axis=1,
        )
        .dropna()
        .reset_index()
    )
    out = [
        RollingQuantileData(
            date=r["date"], median=float(r["median"]), quantile=float(r["quantile"])
        )
        for r in result.to_dict(orient="records")
    ]
    return OBBject(results=out)
