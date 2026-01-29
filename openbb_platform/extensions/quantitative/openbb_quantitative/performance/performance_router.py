"""OpenBB 绩效扩展路由器。"""

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
            description="获取欧米茄比率。",
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
    """计算欧米茄比率。

    欧米茄比率通过考虑实现高于给定阈值的回报的概率，
    提供了一种超越传统绩效衡量标准的复杂指标。它提供了风险和回报的更细致视图，
    专注于成功的可能性，而不仅仅是平均结果。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。
    threshold_start : float, optional
        起始阈值，默认为 0.0
    threshold_end : float, optional
        结束阈值，默认为 1.5

    Returns
    -------
    OBBject[list[OmegaModel]]
        欧米茄比率。
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
            description="获取滚动夏普比率。",
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
    """获取滚动夏普比率。

    此函数计算夏普比率，这是用于评估投资回报与其风险的一个指标。
    通过计入无风险利率，它有助于您了解通过持有风险较高的资产所承受的额外波动
    获得了多少额外回报。夏普比率对于希望比较不同投资效率的投资者至关重要，
    能够在指定时期内清晰地展示潜在回报与其风险的关系。
    它是评估投资策略有效性的理想选择，提供了优化投资组合以获得最大风险回报的见解。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。
    rfr : float, optional
        无风险利率，默认为 0.0
    window : PositiveInt, optional
        窗口大小，默认为 252
    index : str, optional
        索引列名。

    Returns
    -------
    OBBject[list[Data]]
        夏普比率。
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
            description="获取滚动索提诺比率。",
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
    """获取滚动索提诺比率。

    索提诺比率通过区分有害波动性和总波动性来增强对投资回报的评估。
    与其他将所有波动性视为风险的指标不同，此命令专门评估相对于目标或预期回报的
    负回报的波动性。
    它对于更关注下行风险而不是整体波动的投资者特别有用。
    通过计算索提诺比率，投资者可以更好地了解其投资的风险调整回报，
    重点关注负回报的可能性和影响。
    这种方法为投资组合优化提供了更细致的工具，尤其是在旨在最小化下行的策略中。

    For method & terminology see:
    http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。
    target_return : float, optional
        目标回报，默认为 0.0
    window : PositiveInt, optional
        窗口大小，默认为 252
    adjusted : bool, optional
        调整索提诺比率以将其与夏普比率进行比较，默认为 False
    index:str
        输入数据的索引列
    Returns
    -------
    OBBject[list[Data]]
        索提诺比率。
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
        results = results.map(lambda x: x / sqrt(2) if isinstance(x, float) else x)
    results_ = df_to_basemodel(results)

    return OBBject(results=results_)
