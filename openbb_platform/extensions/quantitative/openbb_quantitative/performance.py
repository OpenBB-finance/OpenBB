"""Quantitative performance-metric commands."""

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
    prefix="/performance",
    description="Quantitative performance-metric commands.",
)


class OmegaRatioQueryParams(QueryParams):
    """Query parameters for the Omega ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("threshold", "omega")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    threshold_start: float = Field(
        default=0.0, description="Lower bound of the return-threshold range."
    )
    threshold_end: float = Field(
        default=1.5, description="Upper bound of the return-threshold range."
    )
    bins: PositiveInt = Field(
        default=50, description="Number of evenly spaced thresholds to evaluate."
    )


class OmegaRatioData(Data):
    """One Omega ratio evaluated at a return threshold."""

    threshold: float = Field(description="Return threshold the ratio is evaluated at.")
    omega: float = Field(description="Omega ratio at the threshold.")


class SharpeRatioQueryParams(QueryParams):
    """Query parameters for the rolling Sharpe ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("date", "sharpe_ratio")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    rfr: float = Field(
        default=0.0, description="Risk-free rate, as a decimal fraction."
    )
    window: PositiveInt = Field(
        default=252, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class SharpeRatioData(Data):
    """One rolling Sharpe ratio observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    sharpe_ratio: float = Field(description="Rolling Sharpe ratio.")


class SortinoRatioQueryParams(QueryParams):
    """Query parameters for the rolling Sortino ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("date", "sortino_ratio")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    target_return: float = Field(
        default=0.0, description="Minimum acceptable return, as a decimal fraction."
    )
    window: PositiveInt = Field(
        default=252, description="Number of observations in each rolling window."
    )
    adjusted: bool = Field(
        default=False,
        description="When true, scale the ratio by 1/sqrt(2) for comparability"
        + " with the Sharpe ratio.",
    )
    index: str = Field(default="date", description="Name of the index column.")


class SortinoRatioData(Data):
    """One rolling Sortino ratio observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    sortino_ratio: float = Field(description="Rolling Sortino ratio.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def omega_ratio(params: OmegaRatioQueryParams) -> OBBject[list[OmegaRatioData]]:
    """Calculate the Omega ratio across a range of return thresholds.

    The Omega ratio measures the probability-weighted gains above a threshold relative
    to the losses below it. The ratio is evaluated at 50 thresholds spanning the
    requested range, giving a profile of risk and reward rather than a single number.
    """
    from numpy import linspace, sqrt
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    series = get_target_column(basemodel_to_df(params.data), params.target)
    epsilon = 1e-6

    def get_omega_ratio(df_target, threshold: float) -> float:
        """Get omega ratio."""
        daily_threshold = (threshold + 1) ** sqrt(1 / 252) - 1
        excess = df_target - daily_threshold
        numerator = excess[excess > 0].sum()
        denominator = -excess[excess < 0].sum() + epsilon
        return numerator / denominator

    thresholds = linspace(params.threshold_start, params.threshold_end, params.bins)
    out = [
        OmegaRatioData(threshold=float(t), omega=float(get_omega_ratio(series, t)))
        for t in thresholds
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
        ),
    ],
)
def sharpe_ratio(params: SharpeRatioQueryParams) -> OBBject[list[SharpeRatioData]]:
    """Calculate the rolling Sharpe ratio of a return series.

    The Sharpe ratio measures the excess return earned per unit of total volatility.
    It is computed over a rolling window so the result tracks how risk-adjusted
    performance evolves over time.
    """
    from numpy import sqrt
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    returns = series.pct_change(fill_method=None).dropna().rolling(params.window).sum()
    std = series.rolling(params.window).std() / sqrt(params.window)
    ratio = ((returns - params.rfr) / std).dropna()

    frame = DataFrame({"date": ratio.index, "sharpe_ratio": ratio.to_numpy()})
    out = [
        SharpeRatioData(date=record["date"], sharpe_ratio=float(record["sharpe_ratio"]))
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
        ),
    ],
)
def sortino_ratio(params: SortinoRatioQueryParams) -> OBBject[list[SortinoRatioData]]:
    """Calculate the rolling Sortino ratio of a return series.

    The Sortino ratio refines the Sharpe ratio by penalizing only downside volatility
    measured against a minimum acceptable return. When adjusted, the ratio is scaled by
    1/sqrt(2) so it can be compared directly with the Sharpe ratio.
    """
    from numpy import isfinite, nan, sqrt
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    validate_window(series, params.window)
    returns = (
        series.pct_change(fill_method=None)
        .dropna()
        .rolling(params.window)
        .sum()
        .dropna()
    )

    def downside_deviation(values) -> float:
        """Annualized standard deviation of the negative returns in a window."""
        negative = values[values < 0]
        if negative.size < 2:
            return nan
        return float(negative.std() / sqrt(252) * 100)

    deviation = returns.rolling(params.window).apply(downside_deviation, raw=True)
    ratio = (returns - params.target_return) / deviation
    ratio = ratio[isfinite(ratio)]

    if params.adjusted:
        ratio = ratio / sqrt(2)

    frame = DataFrame({"date": ratio.index, "sortino_ratio": ratio.to_numpy()})
    out = [
        SortinoRatioData(
            date=record["date"], sortino_ratio=float(record["sortino_ratio"])
        )
        for record in frame.to_dict(orient="records")
    ]

    return OBBject(results=out)
