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

    from openbb_quantitative._stats_helpers import skew_
    from openbb_quantitative.helpers import validate_window

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

    from openbb_quantitative._stats_helpers import var_
    from openbb_quantitative.helpers import validate_window

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

    from openbb_quantitative._stats_helpers import std_dev_
    from openbb_quantitative.helpers import validate_window

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

    from openbb_quantitative._stats_helpers import kurtosis_
    from openbb_quantitative.helpers import validate_window

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

    from openbb_quantitative._stats_helpers import mean_
    from openbb_quantitative.helpers import validate_window

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


class RollingFactorsQueryParams(QueryParams):
    """Query parameters for the rolling factors endpoint."""

    __category__ = "rolling"
    __output_columns__ = ("date", "factor", "coefficient", "t_statistic")

    data: list[Data] = Field(
        description="Target time series (index column plus the target column)."
    )
    factors_data: list[Data] = Field(
        description="Factor matrix (index column plus one column per factor)."
    )
    target: str = Field(
        default="close",
        description="Name of the column in `data` to regress on the factor matrix.",
    )
    index: str = Field(
        default="date",
        description="Name of the index column shared by `data` and `factors_data`.",
    )
    risk_free_column: str | None = Field(
        default=None,
        description="Optional name of the risk-free rate column in `factors_data`."
        " When provided, the target is regressed in excess form and the column is"
        " dropped from the regressors.",
    )
    window: PositiveInt = Field(
        default=252,
        description="Number of observations in each rolling regression window.",
    )
    step: PositiveInt = Field(
        default=21,
        description="Stride between successive windows in observations. A value of"
        " 1 refits at every observation; larger values reduce cost on long histories.",
    )


class RollingFactorsData(Data):
    """One rolling factor coefficient observation."""

    date: datetime | dateType | str = Field(
        description="End date of the rolling window."
    )
    factor: str = Field(
        description="Factor name (or 'const' for the regression intercept)."
    )
    coefficient: float = Field(
        description="OLS coefficient estimate for the factor at this window end."
    )
    t_statistic: float = Field(
        description="t-statistic for the coefficient at this window end."
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            description="Roll a 1-year window stepping monthly across a multi-factor"
            " regression of `close` on the supplied factor matrix.",
            parameters={
                "target": "close",
                "window": 252,
                "step": 21,
                "data": APIEx.mock_data("timeseries", 800),
                "factors_data": APIEx.mock_data("timeseries", 800),
            },
        )
    ],
)
def factors(
    params: RollingFactorsQueryParams,
) -> OBBject[list[RollingFactorsData]]:
    """Refit factor OLS on a rolling window and emit per-factor betas through time.

    For each window end at stride `step`, runs OLS of the target on the factor
    matrix using the trailing `window` observations and records each factor's
    coefficient and t-statistic. Suitable for visualizing time-varying factor
    exposures and detecting regime shifts that named-window decompositions hide.
    """
    import statsmodels.api as sm

    from openbb_quantitative._factor_helpers import align_inputs

    factor_matrix, target_series, factor_cols = align_inputs(
        params.data,
        params.factors_data,
        target=params.target,
        index=params.index,
        risk_free_column=params.risk_free_column,
    )
    aligned = factor_matrix.assign(**{params.target: target_series})

    if len(aligned) < params.window:
        raise ValueError(
            f"Rolling window '{params.window}' exceeds the aligned data length"
            f" '{len(aligned)}'."
        )

    min_obs = len(factor_cols) + 1
    if params.window <= min_obs:
        raise ValueError(
            f"Rolling window '{params.window}' must exceed the number of regressors"
            f" plus the intercept ({min_obs})."
        )

    out: list[RollingFactorsData] = []
    end_positions = range(params.window, len(aligned) + 1, params.step)
    for end in end_positions:
        slice_ = aligned.iloc[end - params.window : end]
        x = sm.add_constant(slice_[factor_cols])
        model = sm.OLS(slice_[params.target], x).fit()
        window_end = slice_.index[-1]
        for name in model.params.index:
            out.append(
                RollingFactorsData(
                    date=window_end,
                    factor=str(name),
                    coefficient=float(model.params[name]),
                    t_statistic=float(model.tvalues[name]),
                )
            )

    return OBBject(results=out)
