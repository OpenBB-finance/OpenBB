"""量化分析路由器。"""

from typing import Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data

from openbb_quantitative.models import (
    ADFTestModel,
    CAPMModel,
    KPSSTestModel,
    NormalityModel,
    SummaryModel,
    TestModel,
    UnitRootModel,
)
from openbb_quantitative.performance.performance_router import (
    router as performance_router,
)
from openbb_quantitative.rolling.rolling_router import router as rolling_router
from openbb_quantitative.stats.stats_router import router as stats_router

router = Router(prefix="", description="量化分析工具。")
router.include_router(rolling_router)
router.include_router(stats_router)
router.include_router(performance_router)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取正态性统计信息。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.quantitative.normality(data=stock_data, target='close')",
            ],
        ),
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries", 8)}),
    ],
)
def normality(data: list[Data], target: str) -> OBBject[NormalityModel]:
    """获取正态性统计信息。

    - **Kurtosis**: 样本的峰度是否不同于正态分布。
    - **Skewness**: 样本的偏度是否不同于正态分布。
    - **Jarque-Bera**: 样本数据的偏度和峰度是否与正态分布匹配。
    - **Shapiro-Wilk**: 随机样本是否来自正态分布。
    - **Kolmogorov-Smirnov**: 两个潜在的一维概率分布是否不同。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。

    Returns
    -------
    OBBject[NormalityModel]
        正态性检验摘要。详见 qa_models.NormalityModel。
    """
    # pylint: disable=import-outside-toplevel
    from scipy import stats  # noqa
    from openbb_core.app.utils import (  # noqa
        basemodel_to_df,
        get_target_column,
    )

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    kt_statistic, kt_pvalue = stats.kurtosistest(series_target)
    sk_statistic, sk_pvalue = stats.skewtest(series_target)
    jb_statistic, jb_pvalue = stats.jarque_bera(series_target)
    sh_statistic, sh_pvalue = stats.shapiro(series_target)
    ks_statistic, ks_pvalue = stats.kstest(series_target, "norm")

    norm_summary = NormalityModel(
        kurtosis=TestModel(statistic=kt_statistic, p_value=kt_pvalue),
        skewness=TestModel(statistic=sk_statistic, p_value=sk_pvalue),
        jarque_bera=TestModel(statistic=jb_statistic, p_value=jb_pvalue),
        shapiro_wilk=TestModel(statistic=sh_statistic, p_value=sh_pvalue),
        kolmogorov_smirnov=TestModel(statistic=ks_statistic, p_value=ks_pvalue),
    )

    return OBBject(results=norm_summary)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取资本资产定价模型 (CAPM)。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.quantitative.capm(data=stock_data, target='close')",
            ],
        ),
        APIEx(
            parameters={"target": "close", "data": APIEx.mock_data("timeseries", 31)}
        ),
    ],
)
def capm(data: list[Data], target: str) -> OBBject[CAPMModel]:
    """获取资本资产定价模型 (CAPM)。

    CAPM 提供了一种简化的方法来评估投资的预期回报，同时考虑其相对于
    市场的风险。它是现代金融理论的基石，帮助投资者了解风险与回报之间的
    权衡，从而指导更明智的投资选择。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。

    Returns
    -------
    OBBject[CAPMModel]
        CAPM 模型摘要。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm  # noqa
    from openbb_core.app.utils import (  # noqa``
        basemodel_to_df,
        get_target_columns,
    )
    from pandas import to_datetime  # noqa
    from openbb_quantitative.helpers import get_fama_raw  # noqa

    df = basemodel_to_df(data)

    df_target = get_target_columns(df, ["date", target])
    df_target = df_target.set_index("date")
    df_target.loc[:, "return"] = df_target.pct_change()
    df_target = df_target.dropna()
    df_target.index = to_datetime(df_target.index)
    start_date = df_target.index.min().strftime("%Y-%m-%d")
    end_date = df_target.index.max().strftime("%Y-%m-%d")
    df_fama = get_fama_raw(start_date, end_date)
    df_target = df_target.merge(df_fama, left_index=True, right_index=True)
    df_target["excess_return"] = df_target["return"] - df_target["RF"]
    df_target["excess_mkt"] = df_target["MKT-RF"] - df_target["RF"]
    df_target = df_target.dropna()

    y = df_target[["excess_return"]]
    x = df_target["excess_mkt"]
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()

    results = CAPMModel(
        market_risk=model.params["excess_mkt"],
        systematic_risk=model.rsquared,
        idiosyncratic_risk=1 - model.rsquared,
    )

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取单位根检验。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.quantitative.unitroot_test(data=stock_data, target='close')",
            ],
        ),
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries", 5)}),
    ],
)
def unitroot_test(
    data: list[Data],
    target: str,
    fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
    kpss_reg: Literal["c", "ct"] = "c",
) -> OBBject[UnitRootModel]:
    """获取单位根检验。

    此函数应用两种著名检验来评估您的数据系列是否平稳，或是否包含单位根，
    表明它可能受基于时间的趋势或季节性影响。增强迪基-福勒 (ADF) 检验
    有助于识别单位根的存在，表明该系列可能是非平稳的，并且可能
    随时间推移不可预测。另一方面，Kwiatkowski-Phillips-Schmidt-Shin (KPSS) 检验检查
    系列的平稳性，如果无法拒绝原假设，则表明是一个稳定的平稳系列。
    这些检验共同提供了您的数据时间序列属性的全面视图，对于
    准确建模和预测至关重要。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。
    fuller_reg : Literal["c", "ct", "ctt", "nc", "c"]
        ADF 检验的回归类型。
    kpss_reg : Literal["c", "ct"]
        KPSS 检验的回归类型。

    Returns
    -------
    OBBject[UnitRootModel]
        单位根检验摘要。
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (  # noqa
        basemodel_to_df,
        get_target_column,
    )
    from statsmodels.tsa import stattools  # noqa

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    adf = stattools.adfuller(series_target, regression=fuller_reg)
    kpss = stattools.kpss(series_target, regression=kpss_reg, nlags="auto")

    unitroot_summary = UnitRootModel(
        adf=ADFTestModel(
            statistic=adf[0],
            p_value=adf[1],
            nlags=adf[2] if isinstance(adf[2], int) else 0,
            nobs=adf[3] if isinstance(adf[3], int) else 0,
            icbest=adf[5] if isinstance(adf[5], float) else 0.0,  # type: ignore
        ),
        kpss=KPSSTestModel(
            statistic=kpss[0],
            p_value=kpss[1],
            nlags=kpss[2],
        ),
    )
    return OBBject(results=unitroot_summary)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取摘要统计信息。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.quantitative.summary(data=stock_data, target='close')",
            ],
        ),
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries", 5)}),
    ],
)
def summary(data: list[Data], target: str) -> OBBject[SummaryModel]:
    """获取摘要统计信息。

    提供中心趋势、变异性和分布快照的摘要。
    此命令计算基本统计数据，包括均值、标准差、方差
    和特定百分位数，从而提供目标列的详细资料。
    通过检查这些指标，您可以深入了解数据的整体行为，帮助识别模式、
    异常值或反常现象。摘要表是初始数据探索的宝贵工具，
    确保您为进一步分析或报告奠定坚实基础。

    Parameters
    ----------
    data : list[Data]
        时间序列数据。
    target : str
        目标列名。

    Returns
    -------
    OBBject[SummaryModel]
        摘要表。
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
    )

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    df_stats = series_target.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    df_stats.loc["var"] = df_stats.loc["std"] ** 2
    results = SummaryModel(
        count=df_stats.loc["count"],
        mean=df_stats.loc["mean"],
        std=df_stats.loc["std"],
        var=df_stats.loc["var"],
        min=df_stats.loc["min"],
        p_25=df_stats.loc["25%"],
        p_50=df_stats.loc["50%"],
        p_75=df_stats.loc["75%"],
        max=df_stats.loc["max"],
    )

    return OBBject(results=results)
