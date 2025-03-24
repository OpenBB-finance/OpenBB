"""OpenBB Performance Extension router."""

# pylint: disable=too-many-positional-arguments

from typing import TYPE_CHECKING

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_quantitative.models import (
    OmegaModel,
)
from pydantic import PositiveInt

if TYPE_CHECKING:
    from pandas import Series

router = Router(prefix="/performance")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Omega Ratio.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.performance.omega_ratio(data=returns, target="close")',
            ],
        ),
        APIEx(
            parameters={
                "target": "close",
                "data": APIEx.mock_data(
                    "timeseries",
                    sample={"date": "2023-01-01", "close": 0.05},
                ),
            },
        ),
    ],
)
def omega_ratio(
    data: list[Data],
    target: str,
    threshold_start: float = 0.0,
    threshold_end: float = 1.5,
) -> OBBject[list[OmegaModel]]:
    """Calculate the Omega Ratio.

    The Omega Ratio is a sophisticated metric that goes beyond traditional performance measures by considering the
    probability of achieving returns above a given threshold. It offers a more nuanced view of risk and reward,
    focusing on the likelihood of success rather than just average outcomes.

    Parameters
    ----------
    data : list[Data]
        Time series data.
    target : str
        Target column name.
    threshold_start : float, optional
        Start threshold, by default 0.0
    threshold_end : float, optional
        End threshold, by default 1.5

    Returns
    -------
    OBBject[list[OmegaModel]]
        Omega ratios.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import linspace, sqrt
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
    )

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    epsilon = 1e-6  # to avoid division by zero

    def get_omega_ratio(df_target: "Series", threshold: float) -> float:
        """Get omega ratio."""
        daily_threshold = (threshold + 1) ** sqrt(1 / 252) - 1
        excess = df_target - daily_threshold
        numerator = excess[excess > 0].sum()
        denominator = -excess[excess < 0].sum() + epsilon

        return numerator / denominator

    threshold = linspace(threshold_start, threshold_end, 50)
    results = []
    for i in threshold:
        omega_ = get_omega_ratio(series_target, i)
        results.append(OmegaModel(threshold=i, omega=omega_))

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Sharpe Ratio.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501  # pylint: disable=line-too-long
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.performance.sharpe_ratio(data=returns, target="close")',
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
            },
        ),
    ],
)
def sharpe_ratio(
    data: list[Data],
    target: str,
    rfr: float = 0.0,
    window: PositiveInt = 252,
    index: str = "date",
) -> OBBject[list[Data]]:
    """Get Rolling Sharpe Ratio.

    This function calculates the Sharpe Ratio, a metric used to assess the return of an investment compared to its risk.
    By factoring in the risk-free rate, it helps you understand how much extra return you're getting for the extra
    volatility that you endure by holding a riskier asset. The Sharpe Ratio is essential for investors looking to
    compare the efficiency of different investments, providing a clear picture of potential rewards in relation to their
    risks over a specified period. Ideal for gauging the effectiveness of investment strategies, it offers insights into
    optimizing your portfolio for maximum return on risk.

    Parameters
    ----------
    data : list[Data]
        Time series data.
    target : str
        Target column name.
    rfr : float, optional
        Risk-free rate, by default 0.0
    window : PositiveInt, optional
        Window size, by default 252
    index : str, optional

    Returns
    -------
    OBBject[list[Data]]
        Sharpe ratio.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import sqrt
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    series_target.name = f"sharpe_{window}"
    returns = series_target.pct_change().dropna().rolling(window).sum()
    std = series_target.rolling(window).std() / sqrt(window)
    results = ((returns - rfr) / std).dropna().reset_index(drop=False)

    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get Rolling Sortino Ratio.",
            code=[
                'stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()',  # noqa: E501
                'returns = stock_data["close"].pct_change().dropna()',
                'obb.quantitative.performance.sortino_ratio(data=stock_data, target="close")',
                'obb.quantitative.performance.sortino_ratio(data=stock_data, target="close", target_return=0.01, window=126, adjusted=True)',  # noqa: E501  pylint: disable=line-too-long
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
            },
        ),
    ],
)
def sortino_ratio(
    data: list[Data],
    target: str,
    target_return: float = 0.0,
    window: PositiveInt = 252,
    adjusted: bool = False,
    index: str = "date",
) -> OBBject[list[Data]]:
    """Get rolling Sortino Ratio.

    The Sortino Ratio enhances the evaluation of investment returns by distinguishing harmful volatility
    from total volatility. Unlike other metrics that treat all volatility as risk, this command specifically assesses
    the volatility of negative returns relative to a target or desired return.
    It's particularly useful for investors who are more concerned with downside risk than with overall volatility.
    By calculating the Sortino Ratio, investors can better understand the risk-adjusted return of their investments,
    focusing on the likelihood and impact of negative returns.
    This approach offers a more nuanced tool for portfolio optimization, especially in strategies aiming
    to minimize the downside.

    For method & terminology see:
    http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

    Parameters
    ----------
    data : list[Data]
        Time series data.
    target : str
        Target column name.
    target_return : float, optional
        Target return, by default 0.0
    window : PositiveInt, optional
        Window size, by default 252
    adjusted : bool, optional
        Adjust sortino ratio to compare it to sharpe ratio, by default False
    index:str
        Index column for input data
    Returns
    -------
    OBBject[list[Data]]
        Sortino ratio.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import sqrt
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
        get_target_column,
    )
    from openbb_quantitative.helpers import validate_window

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    returns = series_target.pct_change().dropna().rolling(window).sum().dropna()
    downside_deviation = returns.rolling(window).apply(
        lambda x: (x.values[x.values < 0]).std() / sqrt(252) * 100
    )
    results = (
        ((returns - target_return) / downside_deviation)
        .dropna()
        .reset_index(drop=False)
    )

    if adjusted:
        results = results.applymap(lambda x: x / sqrt(2) if isinstance(x, float) else x)
    results_ = df_to_basemodel(results)

    return OBBject(results=results_)
