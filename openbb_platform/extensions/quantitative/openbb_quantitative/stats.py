"""Quantitative statistics commands - summary statistics of a single series."""

from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

router = Router(prefix="/stats", description="Quantitative statistics commands.")


class StatsSkewQueryParams(QueryParams):
    """Query parameters for the skew endpoint."""

    __category__ = "stats"
    __output_columns__ = ("skew",)

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class StatsSkewData(Data):
    """Skewness of the analyzed series."""

    skew: float = Field(description="Skewness of the distribution.")


class StatsVarianceQueryParams(QueryParams):
    """Query parameters for the variance endpoint."""

    __category__ = "stats"
    __output_columns__ = ("variance",)

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class StatsVarianceData(Data):
    """Variance of the analyzed series."""

    variance: float = Field(description="Variance of the distribution.")


class StatsStdevQueryParams(QueryParams):
    """Query parameters for the stdev endpoint."""

    __category__ = "stats"
    __output_columns__ = ("stdev",)

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class StatsStdevData(Data):
    """Standard deviation of the analyzed series."""

    stdev: float = Field(description="Standard deviation of the distribution.")


class StatsKurtosisQueryParams(QueryParams):
    """Query parameters for the kurtosis endpoint."""

    __category__ = "stats"
    __output_columns__ = ("kurtosis",)

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class StatsKurtosisData(Data):
    """Kurtosis of the analyzed series."""

    kurtosis: float = Field(description="Kurtosis of the distribution.")


class StatsMeanQueryParams(QueryParams):
    """Query parameters for the mean endpoint."""

    __category__ = "stats"
    __output_columns__ = ("mean",)

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class StatsMeanData(Data):
    """Arithmetic mean of the analyzed series."""

    mean: float = Field(description="Arithmetic mean of the distribution.")


class StatsQuantileQueryParams(QueryParams):
    """Query parameters for the quantile endpoint."""

    __category__ = "stats"
    __output_columns__ = ("median", "quantile")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    quantile_pct: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Quantile to compute, between 0 and 1.",
    )


class StatsQuantileData(Data):
    """Quantile of the analyzed series."""

    median: float = Field(description="Median (0.5 quantile) of the distribution.")
    quantile: float = Field(description="Value at the requested quantile.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def skew(params: StatsSkewQueryParams) -> OBBject[StatsSkewData]:
    """Compute the skewness of a target column.

    Skewness measures the degree of asymmetry of a distribution around its mean.
    Positive skewness indicates a longer right tail, while negative skewness indicates
    a longer left tail.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    from openbb_quantitative._stats_helpers import skew_

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(results=StatsSkewData(skew=float(skew_(series))))


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def variance(params: StatsVarianceQueryParams) -> OBBject[StatsVarianceData]:
    """Compute the variance of a target column.

    Variance measures the dispersion of a set of data points around their mean. It is a
    key metric for assessing the volatility and stability of a time series.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    from openbb_quantitative._stats_helpers import var_

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(results=StatsVarianceData(variance=float(var_(series))))


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def stdev(params: StatsStdevQueryParams) -> OBBject[StatsStdevData]:
    """Compute the standard deviation of a target column.

    Standard deviation measures the amount of variation or dispersion of a set of
    values and is the square root of the variance. It is widely used to assess risk
    and volatility.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    from openbb_quantitative._stats_helpers import std_dev_

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(results=StatsStdevData(stdev=float(std_dev_(series))))


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def kurtosis(params: StatsKurtosisQueryParams) -> OBBject[StatsKurtosisData]:
    """Compute the kurtosis of a target column.

    Kurtosis measures the tailedness of a distribution. High kurtosis indicates heavy
    tails and a higher risk of extreme outcomes, while low kurtosis indicates lighter
    tails.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    from openbb_quantitative._stats_helpers import kurtosis_

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(results=StatsKurtosisData(kurtosis=float(kurtosis_(series))))


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def mean(params: StatsMeanQueryParams) -> OBBject[StatsMeanData]:
    """Compute the arithmetic mean of a target column.

    The mean is the average of a set of values and is widely used to summarize the
    central tendency of a time series.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    from openbb_quantitative._stats_helpers import mean_

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(results=StatsMeanData(mean=float(mean_(series))))


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def quantile(params: StatsQuantileQueryParams) -> OBBject[StatsQuantileData]:
    """Compute the quantile of a target column at a specified percentage.

    Quantiles are points dividing the range of a distribution into intervals with equal
    probabilities. The median (0.5 quantile) is returned alongside the requested
    quantile.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    series = get_target_column(basemodel_to_df(params.data), params.target)
    median = float(series.median())
    quantile = float(series.quantile(params.quantile_pct))

    return OBBject(results=StatsQuantileData(median=median, quantile=quantile))
