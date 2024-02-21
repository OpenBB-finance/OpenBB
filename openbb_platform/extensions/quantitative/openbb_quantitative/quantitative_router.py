"""Quantitative Analysis Router."""

from typing import List, Literal

import pandas as pd
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    get_target_column,
    get_target_columns,
)
from openbb_core.provider.abstract.data import Data

from openbb_quantitative.performance.performance_router import (
    router as performance_router,
)
from openbb_quantitative.rolling.rolling_router import router as rolling_router
from openbb_quantitative.stats.stats_router import router as stats_router

from .helpers import get_fama_raw
from .models import (
    ADFTestModel,
    CAPMModel,
    KPSSTestModel,
    NormalityModel,
    SummaryModel,
    TestModel,
    UnitRootModel,
)

router = Router(prefix="")
router.include_router(rolling_router)
router.include_router(stats_router)
router.include_router(performance_router)


@router.command(
    methods=["POST"],
    examples=[
        "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",
        "obb.quantitative.normality(data=stock_data, target='close')",
    ],
)
def normality(data: List[Data], target: str) -> OBBject[NormalityModel]:
    """Get Normality Statistics.

    - **Kurtosis**: whether the kurtosis of a sample differs from the normal distribution.
    - **Skewness**: whether the skewness of a sample differs from the normal distribution.
    - **Jarque-Bera**: whether the sample data has the skewness and kurtosis matching a normal distribution.
    - **Shapiro-Wilk**: whether a random sample comes from a normal distribution.
    - **Kolmogorov-Smirnov**: whether two underlying one-dimensional probability distributions differ.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.

    Returns
    -------
    OBBject[NormalityModel]
        Normality tests summary. See qa_models.NormalityModel for details.
    """
    from scipy import stats  # pylint: disable=import-outside-toplevel

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
        "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",
        "obb.quantitative.capm(data=stock_data, target='close')",
    ],
)
def capm(data: List[Data], target: str) -> OBBject[CAPMModel]:
    """Get Capital Asset Pricing Model (CAPM).

    CAPM offers a streamlined way to assess the expected return on an investment while accounting for its risk relative
    to the market. It's a cornerstone of modern financial theory that helps investors understand the trade-off between
    risk and return, guiding more informed investment choices.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.

    Returns
    -------
    OBBject[CAPMModel]
        CAPM model summary.
    """
    import statsmodels.api as sm  # pylint: disable=import-outside-toplevel # type: ignore

    df = basemodel_to_df(data)

    df_target = get_target_columns(df, ["date", target])
    df_target = df_target.set_index("date")
    df_target.loc[:, "return"] = df_target.pct_change()
    df_target = df_target.dropna()
    df_target.index = pd.to_datetime(df_target.index)
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


@router.command(methods=["POST"])
def unitroot_test(
    data: List[Data],
    target: str,
    fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
    kpss_reg: Literal["c", "ct"] = "c",
) -> OBBject[UnitRootModel]:
    """Get Unit Root Test.

    This function applies two renowned tests to assess whether your data series is stationary or if it contains a unit
    root, indicating it may be influenced by time-based trends or seasonality. The Augmented Dickey-Fuller (ADF) test
    helps identify the presence of a unit root, suggesting that the series could be non-stationary and potentially
    unpredictable over time. On the other hand, the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test checks for the
    stationarity of the series, where failing to reject the null hypothesis indicates a stable, stationary series.
    Together, these tests provide a comprehensive view of your data's time series properties, essential for
    accurate modeling and forecasting.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    fuller_reg : Literal["c", "ct", "ctt", "nc", "c"]
        Regression type for ADF test.
    kpss_reg : Literal["c", "ct"]
        Regression type for KPSS test.

    Returns
    -------
    OBBject[UnitRootModel]
        Unit root tests summary.
    """
    # pylint: disable=import-outside-toplevel
    from statsmodels.tsa import stattools  # type: ignore

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


@router.command(methods=["POST"])
def summary(data: List[Data], target: str) -> OBBject[SummaryModel]:
    """Get Summary Statistics.

    The summary that offers a snapshot of its central tendencies, variability, and distribution.
    This command calculates essential statistics, including mean, standard deviation, variance,
    and specific percentiles, to provide a detailed profile of your target column. B
    y examining these metrics, you gain insights into the data's overall behavior, helping to identify patterns,
    outliers, or anomalies. The summary table is an invaluable tool for initial data exploration,
    ensuring you have a solid foundation for further analysis or reporting.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.

    Returns
    -------
    OBBject[SummaryModel]
        Summary table.
    """
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
