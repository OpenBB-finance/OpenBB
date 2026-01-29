"""滚动统计量化模型子菜单。"""

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
            description="获取滚动偏度。",
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
    """获取滚动偏度。

    偏度是一种统计指标，揭示了分布围绕其均值的不对称程度。
    正偏度表示分布具有向右延伸的尾部，而负偏度显示
    向左延伸的尾部。理解偏度可以提供有关数据中潜在偏差的见解，并有助于预测
    未来数据点的性质。它对于识别金融回报中极端结果的可能性特别有用，
    从而根据指定时期内的分布形状做出更明智的决策。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。
    window : PositiveInt
        窗口大小。
    index : str, optional
        索引列名，默认为 "date"

    Returns
    -------
    OBBject[list[Data]]
        滚动偏度。

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
            description="获取滚动方差。",
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
    """计算给定窗口大小内目标列的滚动方差。

    方差衡量一组数据点围绕其均值的离散程度。它是
    评估金融回报或其他时间序列数据在指定滚动窗口上的波动性和稳定性的关键指标。

    Parameters
    ----------
    data: list[Data]
        作为数据点列表的时间序列数据。
    target: str
        要计算方差的列名。
    window: PositiveInt
        用于计算滚动测量的观测值数量。
    index: str, optional
        索引列的名称，默认为 "date"。

    Returns
    -------
    OBBject[list[Data]]
        包含滚动方差值的对象。
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
            description="获取滚动标准差。",
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
    """计算给定窗口大小内目标列的滚动标准差。

    标准差是一组值的变异或离散程度的度量。
    它广泛用于评估金融回报或其他时间序列数据的风险和波动性，
    在指定的滚动窗口上。它是方差的平方根。

    Parameters
    ----------
    data: list[Data]
        作为数据点列表的时间序列数据。
    target: str
        要计算标准差的列名。
    window: PositiveInt
        用于计算滚动测量的观测值数量。
    index: str, optional
        索引列的名称，默认为 "date"。

    Returns
    -------
    OBBject[list[Data]]
        包含滚动标准差值的对象。
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
            description="获取滚动峰度。",
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
    """计算给定窗口大小内目标列的滚动峰度。

    峰度衡量实值随机变量概率分布的“尾部”。
    高峰度表示分布具有重尾（异常值），表明极端结果的风险较高。
    低峰度表示分布具有轻尾（较少异常值），表明极端结果的风险较低。
    此函数有助于评估金融回报或其他时间序列数据在指定滚动窗口上的异常值风险。

    Parameters
    ----------
    data: list[Data]
        作为数据点列表的时间序列数据。
    target: str
        要计算峰度的列名。
    window: PositiveInt
        用于计算滚动测量的观测值数量。
    index: str, optional
        索引列的名称，默认为 "date"。

    Returns
    -------
    OBBject[list[Data]]
        包含滚动峰度值的对象。
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
            description="获取滚动分位数。",
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
    """计算给定窗口大小内目标列在指定分位数百分比下的滚动分位数。

    分位数是将概率分布范围划分为具有相等概率的间隔的点，
    或者以相同方式划分样本。此函数对于理解指定窗口内的数据分布很有用，
    允许分析趋势、识别异常值和评估风险。

    Parameters
    ----------
    data: list[Data]
        作为数据点列表的时间序列数据。
    target: str
        要计算分位数的列名。
    window: PositiveInt
        用于计算滚动测量的观测值数量。
    quantile_pct: NonNegativeFloat, optional
        要计算的分位数百分比（例如，0.5 表示中位数），默认为 0.5。
    index: str, optional
        索引列的名称，默认为 "date"。

    Returns
    -------
    OBBject[list[Data]]
        包含滚动分位数值和中位数的对象。
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
            description="获取滚动均值。",
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
    """计算给定窗口大小内目标列的滚动平均值。

    滚动均值是一个简单移动平均线，计算目标变量在指定窗口上的平均值。
    此函数广泛用于金融分析，以平滑短期波动并突出时间序列数据中的长期趋势
    或周期。

    Parameters
    ----------
    data: list[Data]
        作为数据点列表的时间序列数据。
    target: str
        要计算均值的列名。
    window: PositiveInt
        用于计算滚动测量的观测值数量。
    index: str, optional
        索引列的名称，默认为 "date"。

    Returns
    -------
    OBBject[list[Data]]
        包含滚动均值的对象。
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
