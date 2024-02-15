"""Quantitative Analysis Router."""

from typing import List, Literal

import numpy as np
import pandas as pd
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    get_target_column,
    get_target_columns,
)
from openbb_core.provider.abstract.data import Data
from pydantic import NonNegativeFloat, PositiveInt

from .helpers import get_fama_raw, validate_window
from .models import (
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

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.normality(data=stock_data, target="close")
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


@router.command(methods=["POST"])
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

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").results
    >>> obb.quantitative.capm(data=stock_data, target="close")
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
def omega_ratio(
    data: List[Data],
    target: str,
    threshold_start: float = 0.0,
    threshold_end: float = 1.5,
) -> OBBject[List[OmegaModel]]:
    """Calculate the Omega Ratio.

    The Omega Ratio is a sophisticated metric that goes beyond traditional performance measures by considering the
    probability of achieving returns above a given threshold. It offers a more nuanced view of risk and reward,
    focusing on the likelihood of success rather than just average outcomes.

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
    OBBject[List[OmegaModel]]
        Omega ratios.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.omega_ratio(data=stock_data, target="close")
    """
    df = basemodel_to_df(data)
    series_target = get_target_column(df, target)

    epsilon = 1e-6  # to avoid division by zero

    def get_omega_ratio(df_target: pd.Series, threshold: float) -> float:
        """Get omega ratio."""
        daily_threshold = (threshold + 1) ** np.sqrt(1 / 252) - 1
        excess = df_target - daily_threshold
        numerator = excess[excess > 0].sum()
        denominator = -excess[excess < 0].sum() + epsilon

        return numerator / denominator

    threshold = np.linspace(threshold_start, threshold_end, 50)
    results = []
    for i in threshold:
        omega_ = get_omega_ratio(series_target, i)
        results.append(OmegaModel(threshold=i, omega=omega_))

    return OBBject(results=results)


@router.command(methods=["POST"])
def kurtosis(
    data: List[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[List[Data]]:
    """Get the rolling Kurtosis.

    Kurtosis provides insights into the shape of the data's distribution, particularly the heaviness of its tails.
    Kurtosis is a statistical measure that reveals whether the data points tend to cluster around the mean or if
    outliers are more common than a normal distribution would suggest. A higher kurtosis indicates more data points are
    found in the tails, suggesting potential volatility or risk.
    This analysis is crucial for understanding the underlying characteristics of your data, helping to anticipate
    extreme events or anomalies over a specified window of time.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.
    index : str, optional
        Index column name, by default "date"

    Returns
    -------
    OBBject[List[Data]]
        Kurtosis.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.kurtosis(data=stock_data, target="close", window=252)
    """
    import pandas_ta as ta  # pylint: disable=import-outside-toplevel # type: ignore

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    results = (
        ta.kurtosis(close=series_target, length=window).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

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

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.unitroot_test(data=stock_data, target="close")
    >>> obb.quantitative.unitroot_test(data=stock_data, target="close", fuller_reg="ct", kpss_reg="ct")
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
def sharpe_ratio(
    data: List[Data],
    target: str,
    rfr: float = 0.0,
    window: PositiveInt = 252,
    index: str = "date",
) -> OBBject[List[Data]]:
    """Get Rolling Sharpe Ratio.

    This function calculates the Sharpe Ratio, a metric used to assess the return of an investment compared to its risk.
    By factoring in the risk-free rate, it helps you understand how much extra return you're getting for the extra
    volatility that you endure by holding a riskier asset. The Sharpe Ratio is essential for investors looking to
    compare the efficiency of different investments, providing a clear picture of potential rewards in relation to their
    risks over a specified period. Ideal for gauging the effectiveness of investment strategies, it offers insights into
    optimizing your portfolio for maximum return on risk.

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
    index : str, optional

    Returns
    -------
    OBBject[List[Data]]
        Sharpe ratio.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.sharpe_ratio(data=stock_data, target="close")
    >>> obb.quantitative.sharpe_ratio(data=stock_data, target="close", rfr=0.01, window=126)
    """
    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    series_target.name = f"sharpe_{window}"
    returns = series_target.pct_change().dropna().rolling(window).sum()
    std = series_target.rolling(window).std() / np.sqrt(window)
    results = ((returns - rfr) / std).dropna().reset_index(drop=False)

    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(methods=["POST"])
def sortino_ratio(
    data: List[Data],
    target: str,
    target_return: float = 0.0,
    window: PositiveInt = 252,
    adjusted: bool = False,
    index: str = "date",
) -> OBBject[List[Data]]:
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
    index:str
        Index column for input data
    Returns
    -------
    OBBject[List[Data]]
        Sortino ratio.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.sortino_ratio(data=stock_data, target="close")
    >>> obb.quantitative.sortino_ratio(data=stock_data, target="close", target_return=0.01, window=126, adjusted=True)
    """
    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    returns = series_target.pct_change().dropna().rolling(window).sum()
    downside_deviation = returns.rolling(window).apply(
        lambda x: (x.values[x.values < 0]).std() / np.sqrt(252) * 100
    )
    results = (
        ((returns - target_return) / downside_deviation)
        .dropna()
        .reset_index(drop=False)
    )

    if adjusted:
        results = results / np.sqrt(2)

    results_ = df_to_basemodel(results)

    return OBBject(results=results_)


@router.command(methods=["POST"])
def skewness(
    data: List[Data], target: str, window: PositiveInt = 21, index: str = "date"
) -> OBBject[List[Data]]:
    """Get Rolling Skewness.

    Skewness is a statistical measure that reveals the degree of asymmetry of a distribution around its mean.
    Positive skewness indicates a distribution with an extended tail to the right, while negative skewness shows a tail
    that stretches left. Understanding skewness can provide insights into potential biases in data and help anticipate
    the nature of future data points. It's particularly useful for identifying the likelihood of extreme outcomes in
    financial returns, enabling more informed decision-making based on the distribution's shape over a specified period.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.
    index : str, optional
        Index column name, by default "date"
    Returns
    -------
    OBBject[List[Data]]
        Skewness.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.skewness(data=stock_data, target="close", window=252)
    """
    import pandas_ta as ta  # pylint: disable=import-outside-toplevel # type: ignore

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    results = (
        ta.skew(close=series_target, length=window).dropna().reset_index(drop=False)
    )
    results = df_to_basemodel(results)

    return OBBject(results=results)


@router.command(methods=["POST"])
def quantile(
    data: List[Data],
    target: str,
    window: PositiveInt = 21,
    quantile_pct: NonNegativeFloat = 0.5,
    index: str = "date",
) -> OBBject[List[Data]]:
    """Get Rolling Quantile.

    Quantile is a statistical measure that identifies the value below which a given percentage of observations in a
    group of data falls. By setting the quantile percentage, you can determine any point in the distribution, not just
    the median. Whether you're interested in the median, quartiles, or any other position within your data's range,
    this tool offers a precise way to understand the distribution's characteristics.
    It's especially useful for identifying outliers, understanding dispersion, and setting thresholds for
    decision-making based on the distribution of data over a specified period.

    Parameters
    ----------
    data : List[Data]
        Time series data.
    target : str
        Target column name.
    window : PositiveInt
        Window size.
    quantile_pct : NonNegativeFloat, optional
        Quantile to get
    Returns
    -------
    OBBject[List[Data]]
        Quantile.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.quantile(data=stock_data, target="close", window=252, quantile_pct=0.25)
    >>> obb.quantitative.quantile(data=stock_data, target="close", window=252, quantile_pct=0.75)
    """
    import pandas_ta as ta  # pylint: disable=import-outside-toplevel # type: ignore

    df = basemodel_to_df(data, index=index)
    series_target = get_target_column(df, target)
    validate_window(series_target, window)
    df_median = ta.median(close=series_target, length=window).to_frame()
    df_quantile = ta.quantile(series_target, length=window, q=quantile_pct).to_frame()
    results = (
        pd.concat([df_median, df_quantile], axis=1).dropna().reset_index(drop=False)
    )

    results_ = df_to_basemodel(results)

    return OBBject(results=results_)


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

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
    >>> obb.quantitative.summary(data=stock_data, target="close")
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
