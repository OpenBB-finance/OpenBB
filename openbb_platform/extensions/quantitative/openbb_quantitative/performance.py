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

_PERIODS_PER_YEAR = 252


class OmegaRatioQueryParams(QueryParams):
    """Query parameters for the Omega ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("threshold", "omega")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the periodic return column to analyze.")
    threshold_start: float = Field(
        default=0.0,
        description="Lower bound of the annualized return-threshold range,"
        + " as a decimal fraction.",
    )
    threshold_end: float = Field(
        default=1.5,
        description="Upper bound of the annualized return-threshold range,"
        + " as a decimal fraction.",
    )
    bins: PositiveInt = Field(
        default=50, description="Number of evenly spaced thresholds to evaluate."
    )


class OmegaRatioData(Data):
    """One Omega ratio evaluated at a return threshold."""

    threshold: float = Field(
        description="Annualized return threshold the ratio is evaluated at."
    )
    omega: float = Field(description="Omega ratio at the threshold.")


class SharpeRatioQueryParams(QueryParams):
    """Query parameters for the rolling Sharpe ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("date", "sharpe_ratio")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the price column to analyze.")
    rfr: float = Field(
        default=0.0, description="Annualized risk-free rate, as a decimal fraction."
    )
    window: PositiveInt = Field(
        default=252, description="Number of observations in each rolling window."
    )
    index: str = Field(default="date", description="Name of the index column.")


class SharpeRatioData(Data):
    """One rolling Sharpe ratio observation."""

    date: datetime | dateType | str = Field(description="Observation date.")
    sharpe_ratio: float = Field(description="Rolling annualized Sharpe ratio.")


class SortinoRatioQueryParams(QueryParams):
    """Query parameters for the rolling Sortino ratio endpoint."""

    __category__ = "performance"
    __output_columns__ = ("date", "sortino_ratio")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the price column to analyze.")
    target_return: float = Field(
        default=0.0,
        description="Annualized minimum acceptable return, as a decimal fraction.",
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
    sortino_ratio: float = Field(description="Rolling annualized Sortino ratio.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "target": "return",
                "data": APIEx.mock_data(
                    "timeseries", sample={"date": "2023-01-01", "return": 0.01}
                ),
            }
        ),
    ],
)
def omega_ratio(params: OmegaRatioQueryParams) -> OBBject[list[OmegaRatioData]]:
    """Calculate the Omega ratio of a periodic return series across return thresholds.

    The Omega ratio measures the probability-weighted gains above a threshold relative
    to the losses below it. Each annualized threshold is converted to a per-period
    threshold assuming 252 periods per year. The ratio is evaluated at `bins`
    thresholds spanning the requested range, giving a profile of risk and reward
    rather than a single number.
    """
    from numpy import linspace
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    series = get_target_column(basemodel_to_df(params.data), params.target)
    epsilon = 1e-6

    def get_omega_ratio(df_target, threshold: float) -> float:
        """Get omega ratio."""
        period_threshold = (threshold + 1) ** (1 / _PERIODS_PER_YEAR) - 1
        excess = df_target - period_threshold
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
    """Calculate the rolling annualized Sharpe ratio of a price series.

    The prices are converted to periodic returns. In each rolling window, the mean
    return in excess of the risk-free rate is divided by the standard deviation of
    the returns and annualized assuming 252 periods per year.
    """
    from numpy import isfinite, sqrt
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    returns = series.pct_change(fill_method=None).dropna()
    validate_window(returns, params.window)
    period_rfr = (1 + params.rfr) ** (1 / _PERIODS_PER_YEAR) - 1
    window = returns.rolling(params.window)
    ratio = (window.mean() - period_rfr) / window.std() * sqrt(_PERIODS_PER_YEAR)
    ratio = ratio[isfinite(ratio)]

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
    """Calculate the rolling annualized Sortino ratio of a price series.

    The prices are converted to periodic returns. In each rolling window, the mean
    return in excess of the minimum acceptable return is divided by the downside
    deviation below that return and annualized assuming 252 periods per year. When
    adjusted, the ratio is scaled by 1/sqrt(2) so it can be compared directly with
    the Sharpe ratio.
    """
    from numpy import isfinite, sqrt
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame

    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(params.data, index=params.index)
    series = get_target_column(df, params.target)
    returns = series.pct_change(fill_method=None).dropna()
    validate_window(returns, params.window)
    period_target = (1 + params.target_return) ** (1 / _PERIODS_PER_YEAR) - 1
    excess = returns - period_target
    downside_deviation = (excess.clip(upper=0.0) ** 2).rolling(
        params.window
    ).mean() ** 0.5
    ratio = (
        excess.rolling(params.window).mean()
        / downside_deviation
        * sqrt(_PERIODS_PER_YEAR)
    )
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
