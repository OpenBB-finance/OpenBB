from typing import List, Literal

import numpy as np
import pandas as pd
import pandas_ta as ta
import statsmodels.api as sm
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    get_target_column,
    get_target_columns,
)
from openbb_provider.abstract.data import Data
from pydantic import NonNegativeFloat, PositiveInt
from scipy import stats
from statsmodels.tsa import stattools

from openbb_qa.qa_helpers import get_fama_raw
from openbb_qa.qa_models import (
    ADFTestModel,
    CAPMModel,
    KPSSTestModel,
    NormalityModel,
    OmegaModel,
    SummaryModel,
    TestModel,
    UnitRootModel,
)

router = Router(prefix="")


@router.command(methods=["POST"])
def normality(data: List[Data], target: str) -> Obbject[NormalityModel]:
    """
    Normality Statistics.

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
    Obbject[NormalityModel]
        Normality tests summary. See qa_models.NormalityModel for details.
    """

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

    return Obbject(results=norm_summary)


@router.command(methods=["POST"])
def capm(data: List[Data], target: str) -> Obbject[CAPMModel]:
    """Capital Asset Pricing Model."""

    df = basemodel_to_df(data)

    df_target = get_target_columns(df, ["date", target])
    df_target = df_target.set_index("date")
    df_target["return"] = df_target.pct_change()
    df_target = df_target.dropna()
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

    return Obbject(results=results)


@router.command(methods=["POST"])
def qqplot() -> Obbject[Empty]:
    """QQ Plot."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def om(
    data: List[Data],
    target: str,
    threshold_start: float = 0.0,
    threshold_end: float = 1.5,
) -> Obbject[List[OmegaModel]]:
    """Omega Ratio.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    threshold_start : float, optional
        Start threshold, by default 0.0
    threshold_end : float, optional
        End threshold, by default 1.5

    Returns
    -------
    Obbject[List[OmegaModel]]
        Omega ratios.
    """

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    def get_omega_ratio(df_target: pd.Series, threshold: float) -> float:
        """Get omega ratio."""
        daily_threshold = (threshold + 1) ** np.sqrt(1 / 252) - 1
        excess = df_target - daily_threshold
        omega = excess[excess > 0].sum() / -excess[excess < 0].sum()
        return omega

    threshold = np.linspace(threshold_start, threshold_end, 50)
    results = []
    for i in threshold:
        results.append(OmegaModel(threshold=i, omega=get_omega_ratio(series_target, i)))

    return Obbject(results=results)


@router.command(methods=["POST"])
def kurtosis(data: List[Data], target: str, window: PositiveInt) -> Obbject[List[Data]]:
    """Kurtosis.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.

    Returns
    -------
    Obbject[List[Data]]
        Kurtosis.
    """
    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = ta.kurtosis(close=series_target, length=window).dropna()
    results = df_to_basemodel(results)

    return Obbject(results=results)


@router.command(methods=["POST"])
def pick() -> Obbject[Empty]:
    """Pick."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def spread() -> Obbject[Empty]:
    """Spread."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def rolling() -> Obbject[Empty]:
    """Rolling."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def var() -> Obbject[Empty]:
    """Value at Risk."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def line() -> Obbject[Empty]:
    """Line."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def hist() -> Obbject[Empty]:
    """Histogram."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def unitroot(
    data: List[Data],
    target: str,
    fuller_reg: Literal["c", "ct", "ctt", "nc", "c"] = "c",
    kpss_reg: Literal["c", "ct"] = "c",
) -> Obbject[UnitRootModel]:
    """Unit Root Test.

    Augmented Dickey-Fuller test for unit root.
    Kwiatkowski-Phillips-Schmidt-Shin test for unit root.

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
    Obbject[UnitRootModel]
        Unit root tests summary.
    """

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
    return Obbject(results=unitroot_summary)


@router.command(methods=["POST"])
def beta() -> Obbject[Empty]:
    """Beta."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def sh(
    data: List[Data], target: str, rfr: float = 0.0, window: PositiveInt = 252
) -> Obbject[List[Data]]:
    """Sharpe Ratio.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    rfr : float, optional
        Risk-free rate, by default 0.0
    window : PositiveInt, optional
        Window size, by default 252

    Returns
    -------
    Obbject[List[Data]]
        Sharpe ratio.
    """

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    returns = series_target.pct_change().dropna().rolling(window).sum()
    std = series_target.rolling(window).std() / np.sqrt(window)
    results = ((returns - rfr) / std).dropna()

    results = df_to_basemodel(results)

    return Obbject(results=results)


@router.command(methods=["POST"])
def so(
    data: List[Data],
    target: str,
    target_return: float = 0.0,
    window: PositiveInt = 252,
    adjusted: bool = False,
) -> Obbject[List[Data]]:
    """Sortino Ratio.

    For method & terminology see: http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    target_return : float, optional
        Target return, by default 0.0
    window : PositiveInt, optional
        Window size, by default 252
    adjusted : bool, optional
        Adjust sortino ratio to compare it to sharpe ratio, by default False

    Returns
    -------
    Obbject[List[Data]]
        Sortino ratio.
    """

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    returns = series_target.pct_change().dropna().rolling(window).sum()
    downside_deviation = returns.rolling(window).apply(
        lambda x: (x.values[x.values < 0]).std() / np.sqrt(252) * 100
    )
    results = ((returns - target_return) / downside_deviation).dropna()

    if adjusted:
        results = results / np.sqrt(2)

    results = df_to_basemodel(results)

    return Obbject(results=results)


@router.command(methods=["POST"])
def cusum() -> Obbject[Empty]:
    """Cumulative Sum."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def raw() -> Obbject[Empty]:
    """Raw."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def cdf() -> Obbject[Empty]:
    """Cumulative Distribution Function."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def decompose() -> Obbject[Empty]:
    """Decompose."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def skew(data: List[Data], target: str, window: PositiveInt) -> Obbject[List[Data]]:
    """Skewness.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.

    Returns
    -------
    Obbject[List[Data]]
        Skewness.
    """
    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)
    results = ta.skew(close=series_target, length=window).dropna()
    results = df_to_basemodel(results)

    return Obbject(results=results)


@router.command(methods=["POST"])
def quantile(
    data: List[Data],
    target: str,
    window: PositiveInt,
    quantile_pct: NonNegativeFloat = 0.5,
) -> Obbject[List[Data]]:
    """Quantile."""

    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    df_median = ta.median(close=series_target, length=window).to_frame()
    df_quantile = ta.quantile(series_target, length=window, q=quantile_pct).to_frame()
    results = pd.concat([df_median, df_quantile], axis=1).dropna()

    results = df_to_basemodel(results)

    return Obbject(results=results)


@router.command(methods=["POST"])
def bw() -> Obbject[Empty]:
    """Bandwidth."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def es() -> Obbject[Empty]:
    """Expected Shortfall."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def acf() -> Obbject[Empty]:
    """Autocorrelation Function."""
    return Obbject(results=Empty())


@router.command(methods=["POST"])
def summary(data: List[Data], target: str) -> Obbject[SummaryModel]:
    """Summary.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.

    Returns
    -------
    Obbject[SummaryModel]
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

    return Obbject(results=results)
