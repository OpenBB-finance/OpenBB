"""Quantitative analysis metrics commands."""

from typing import Literal

from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeInt

router = Router(prefix="", description="Quantitative analysis commands.")


class NormalityQueryParams(QueryParams):
    """Query parameters for the normality endpoint."""

    __category__ = "quantitative"
    __output_columns__ = (
        "kurtosis_statistic",
        "kurtosis_p_value",
        "skewness_statistic",
        "skewness_p_value",
        "jarque_bera_statistic",
        "jarque_bera_p_value",
        "shapiro_wilk_statistic",
        "shapiro_wilk_p_value",
        "kolmogorov_smirnov_statistic",
        "kolmogorov_smirnov_p_value",
    )

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class NormalityData(Data):
    """Normality test statistics for a data series."""

    kurtosis_statistic: float = Field(description="Kurtosis test statistic.")
    kurtosis_p_value: float = Field(description="p-value of the kurtosis test.")
    skewness_statistic: float = Field(description="Skewness test statistic.")
    skewness_p_value: float = Field(description="p-value of the skewness test.")
    jarque_bera_statistic: float = Field(description="Jarque-Bera test statistic.")
    jarque_bera_p_value: float = Field(description="p-value of the Jarque-Bera test.")
    shapiro_wilk_statistic: float = Field(description="Shapiro-Wilk test statistic.")
    shapiro_wilk_p_value: float = Field(description="p-value of the Shapiro-Wilk test.")
    kolmogorov_smirnov_statistic: float = Field(
        description="Kolmogorov-Smirnov test statistic."
    )
    kolmogorov_smirnov_p_value: float = Field(
        description="p-value of the Kolmogorov-Smirnov test."
    )


class CapmQueryParams(QueryParams):
    """Query parameters for the CAPM endpoint."""

    __category__ = "quantitative"
    __output_columns__ = ("market_risk", "systematic_risk", "idiosyncratic_risk")

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class CapmData(Data):
    """Capital Asset Pricing Model risk measures for an asset."""

    market_risk: float = Field(
        description="Beta - the asset's sensitivity to market returns."
    )
    systematic_risk: float = Field(
        description="Share of variance explained by the market (R-squared)."
    )
    idiosyncratic_risk: float = Field(
        description="Share of variance not explained by the market (1 - R-squared)."
    )


class UnitRootTestQueryParams(QueryParams):
    """Query parameters for the unit root test endpoint."""

    __category__ = "quantitative"
    __output_columns__ = (
        "adf_statistic",
        "adf_p_value",
        "adf_nlags",
        "adf_nobs",
        "adf_icbest",
        "kpss_statistic",
        "kpss_p_value",
        "kpss_nlags",
        "kpss_p_value_interpolated",
    )

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")
    fuller_reg: Literal["c", "ct", "ctt", "n"] = Field(
        default="c",
        description="Constant/trend terms for the ADF test: 'c' constant, 'ct'"
        + " constant and trend, 'ctt' constant, linear and quadratic trend, 'n' no"
        + " constant or trend.",
    )
    kpss_reg: Literal["c", "ct"] = Field(
        default="c",
        description="Null hypothesis for the KPSS test: 'c' level-stationary, 'ct'"
        + " trend-stationary.",
    )
    maxlag: NonNegativeInt | None = Field(
        default=None,
        description="Maximum lag for the ADF test. If None, a data-dependent"
        + " default is used.",
    )
    autolag: Literal["AIC", "BIC", "t-stat"] | None = Field(
        default="AIC",
        description="Lag-selection method for the ADF test: 'AIC', 'BIC', or"
        + " 't-stat'; None uses maxlag directly without selection.",
    )
    nlags: Literal["auto", "legacy"] | NonNegativeInt = Field(
        default="auto",
        description="Lags for the KPSS variance estimator: 'auto', 'legacy', or an"
        + " explicit non-negative integer.",
    )


class UnitRootData(Data):
    """Augmented Dickey-Fuller and KPSS unit root test results."""

    adf_statistic: float = Field(description="Augmented Dickey-Fuller test statistic.")
    adf_p_value: float = Field(description="p-value of the ADF test.")
    adf_nlags: int = Field(description="Number of lags used in the ADF test.")
    adf_nobs: int = Field(description="Number of observations used in the ADF test.")
    adf_icbest: float | None = Field(
        default=None,
        description="Best information criterion value of the ADF test"
        + " (None when autolag is disabled).",
    )
    kpss_statistic: float = Field(description="KPSS test statistic.")
    kpss_p_value: float = Field(description="p-value of the KPSS test.")
    kpss_nlags: int = Field(description="Number of lags used in the KPSS test.")
    kpss_p_value_interpolated: bool = Field(
        description="False when the KPSS p-value is clamped to a table boundary"
        + " (the true p-value is more extreme than reported)."
    )


class SummaryQueryParams(QueryParams):
    """Query parameters for the summary endpoint."""

    __category__ = "quantitative"
    __output_columns__ = (
        "count",
        "mean",
        "std",
        "var",
        "min",
        "p25",
        "p50",
        "p75",
        "max",
    )

    data: list[Data] = Field(description="Input dataset.")
    target: str = Field(description="Name of the column to analyze.")


class SummaryData(Data):
    """Descriptive summary statistics for a data series."""

    count: int = Field(description="Number of observations.")
    mean: float = Field(description="Arithmetic mean.")
    std: float = Field(description="Standard deviation.")
    var: float = Field(description="Variance.")
    min: float = Field(description="Minimum value.")
    p25: float = Field(description="25th percentile.")
    p50: float = Field(description="50th percentile (median).")
    p75: float = Field(description="75th percentile.")
    max: float = Field(description="Maximum value.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def normality(params: NormalityQueryParams) -> OBBject[NormalityData]:
    """Get normality statistics for a data series.

    Runs the kurtosis, skewness, Jarque-Bera, Shapiro-Wilk, and Kolmogorov-Smirnov
    tests, each assessing whether the sample is drawn from a normal distribution.
    Returns the test statistic and p-value for every test.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from scipy import stats

    series = get_target_column(basemodel_to_df(params.data), params.target)
    try:
        series = series.astype(float)
    except ValueError as exc:
        raise ValueError("The target column must be numeric.") from exc

    kurtosis_statistic, kurtosis_p_value = stats.kurtosistest(series)
    skewness_statistic, skewness_p_value = stats.skewtest(series)
    jarque_bera_statistic, jarque_bera_p_value = stats.jarque_bera(series)
    shapiro_wilk_statistic, shapiro_wilk_p_value = stats.shapiro(series)
    kolmogorov_smirnov_statistic, kolmogorov_smirnov_p_value = stats.kstest(
        series, "norm"
    )

    return OBBject(
        results=NormalityData(
            kurtosis_statistic=float(kurtosis_statistic),
            kurtosis_p_value=float(kurtosis_p_value),
            skewness_statistic=float(skewness_statistic),
            skewness_p_value=float(skewness_p_value),
            jarque_bera_statistic=float(jarque_bera_statistic),
            jarque_bera_p_value=float(jarque_bera_p_value),
            shapiro_wilk_statistic=float(shapiro_wilk_statistic),
            shapiro_wilk_p_value=float(shapiro_wilk_p_value),
            kolmogorov_smirnov_statistic=float(kolmogorov_smirnov_statistic),
            kolmogorov_smirnov_p_value=float(kolmogorov_smirnov_p_value),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def capm(params: CapmQueryParams) -> OBBject[CapmData]:
    """Get Capital Asset Pricing Model (CAPM) risk measures for an asset.

    Regresses the asset's excess return on the excess market return using the
    Fama-French factors. Returns the market risk (beta), the systematic risk
    (R-squared), and the idiosyncratic risk (1 - R-squared).
    """
    import statsmodels.api as sm
    from openbb_core.app.utils import basemodel_to_df, get_target_columns
    from pandas import to_datetime

    from openbb_quantitative.helpers import get_fama_raw

    prices = get_target_columns(basemodel_to_df(params.data), ["date", params.target])
    prices = prices.set_index("date")
    prices.index = to_datetime(prices.index)
    monthly_return = (
        prices[params.target]
        .resample("MS")
        .last()
        .pct_change(fill_method=None)
        .dropna()
    )
    monthly_return.name = "asset_return"
    start_date = monthly_return.index.min().strftime("%Y-%m-%d")
    end_date = monthly_return.index.max().strftime("%Y-%m-%d")
    factors = get_fama_raw(start_date, end_date)
    merged = monthly_return.to_frame().merge(factors, left_index=True, right_index=True)
    merged["excess_return"] = merged["asset_return"] - merged["rf"]
    merged = merged.dropna()
    model = sm.OLS(merged[["excess_return"]], sm.add_constant(merged["mkt_rf"])).fit()

    return OBBject(
        results=CapmData(
            market_risk=float(model.params["mkt_rf"]),
            systematic_risk=float(model.rsquared),
            idiosyncratic_risk=float(1 - model.rsquared),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def unitroot_test(params: UnitRootTestQueryParams) -> OBBject[UnitRootData]:
    """Get unit root test results for a data series.

    Applies the Augmented Dickey-Fuller (ADF) test, whose null hypothesis is the
    presence of a unit root, and the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test,
    whose null hypothesis is stationarity. Together they characterize whether the
    series is stationary.
    """
    import warnings

    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from statsmodels.tools.sm_exceptions import InterpolationWarning
    from statsmodels.tsa import stattools

    series = get_target_column(basemodel_to_df(params.data), params.target)
    adf = stattools.adfuller(
        series,
        maxlag=params.maxlag,
        regression=params.fuller_reg,
        autolag=params.autolag,
    )
    adf_icbest = adf[5] if len(adf) > 5 else None
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        kpss_result = stattools.kpss(
            series, regression=params.kpss_reg, nlags=params.nlags
        )
    kpss_p_value_interpolated = not any(
        issubclass(entry.category, InterpolationWarning) for entry in caught
    )

    return OBBject(
        results=UnitRootData(
            adf_statistic=float(adf[0]),
            adf_p_value=float(adf[1]),
            adf_nlags=int(adf[2]),
            adf_nobs=int(adf[3]),
            adf_icbest=float(adf_icbest) if adf_icbest is not None else None,
            kpss_statistic=float(kpss_result[0]),
            kpss_p_value=float(kpss_result[1]),
            kpss_nlags=int(kpss_result[2]),
            kpss_p_value_interpolated=kpss_p_value_interpolated,
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"target": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def summary(params: SummaryQueryParams) -> OBBject[SummaryData]:
    """Get descriptive summary statistics for a data series.

    Computes the count, central tendency, dispersion, and quartile distribution of
    the target column. Provides a concise profile of the data for initial
    exploration and reporting.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column

    series = get_target_column(basemodel_to_df(params.data), params.target)

    return OBBject(
        results=SummaryData(
            count=int(series.count()),
            mean=float(series.mean()),
            std=float(series.std()),
            var=float(series.var()),
            min=float(series.min()),
            p25=float(series.quantile(0.25)),
            p50=float(series.quantile(0.5)),
            p75=float(series.quantile(0.75)),
            max=float(series.max()),
        )
    )
