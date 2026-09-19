"""Econometrics time-series commands - stationarity, cointegration, causality, GARCH."""

from datetime import (
    date as dateType,
    datetime,
)
from itertools import combinations
from typing import Literal

from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

router = Router(prefix="", description="Econometrics time-series commands.")


class UnitRootQueryParams(QueryParams):
    """Query parameters for the Augmented Dickey-Fuller unit root endpoint."""

    __category__ = "time_series"
    __output_columns__ = ("adf_stat", "p_value", "used_lag", "nobs", "ic_best")

    data: list[Data] = Field(description="Input dataset.")
    column: str = Field(description="Column to test for a unit root.")
    regression: Literal["c", "ct", "ctt"] = Field(
        default="c",
        description="Deterministic terms: 'c' constant, 'ct' constant and trend,"
        + " 'ctt' constant, trend, and quadratic trend.",
    )
    maxlag: NonNegativeInt | None = Field(
        default=None,
        description="Maximum lag to include. If None, a data-dependent default is used.",
    )
    autolag: Literal["AIC", "BIC", "t-stat"] | None = Field(
        default="AIC",
        description="Lag-selection method: 'AIC', 'BIC', or 't-stat'; None uses"
        + " maxlag directly without selection.",
    )


class UnitRootData(Data):
    """Augmented Dickey-Fuller unit root test result."""

    adf_stat: float = Field(
        description="Test statistic (more negative favours stationarity)."
    )
    p_value: float = Field(description="MacKinnon p-value.")
    used_lag: int = Field(description="Number of lags used.")
    nobs: int = Field(description="Number of observations used.")
    ic_best: float | None = Field(
        default=None,
        description="Maximised information criterion (None when autolag is disabled).",
    )
    critical_values: dict = Field(
        description="Critical values at the 1%, 5%, and 10% levels."
    )


class KpssQueryParams(QueryParams):
    """Query parameters for the KPSS stationarity endpoint."""

    __category__ = "time_series"
    __output_columns__ = ("kpss_stat", "p_value", "p_value_interpolated", "lags")

    data: list[Data] = Field(description="Input dataset.")
    column: str = Field(description="Column to test.")
    regression: Literal["c", "ct"] = Field(
        default="c",
        description="Null hypothesis: 'c' level-stationary, 'ct' trend-stationary.",
    )
    nlags: Literal["auto", "legacy"] | NonNegativeInt = Field(
        default="auto",
        description="Lags for the variance estimator: 'auto', 'legacy', or an"
        + " explicit non-negative integer.",
    )


class KpssData(Data):
    """KPSS stationarity test result."""

    kpss_stat: float = Field(description="Test statistic.")
    p_value: float = Field(description="p-value of the test statistic.")
    p_value_interpolated: bool = Field(
        description="False when p_value is a clamped table boundary"
        + " (the true p-value is more extreme than reported)."
    )
    lags: int = Field(description="Number of lags used in the test.")
    critical_values: dict = Field(
        description="Critical values at the 10%, 5%, 2.5%, and 1% levels."
    )


class CointegrationQueryParams(QueryParams):
    """Query parameters for the Engle-Granger cointegration endpoint."""

    __category__ = "time_series"
    __output_columns__ = ("pair", "c", "gamma", "alpha", "adf_stat", "p_value")

    data: list[Data] = Field(description="Input dataset.")
    columns: list[str] = Field(
        description="Columns to test pairwise for cointegration."
    )


class CointegrationData(Data):
    """Engle-Granger two-step cointegration result for one column pair."""

    pair: str = Field(description="The tested column pair, formatted as 'x/y'.")
    c: float = Field(description="Constant of the long-run relationship.")
    gamma: float = Field(description="Slope of the long-run relationship.")
    alpha: float = Field(description="Error-correction speed of adjustment.")
    adf_stat: float = Field(description="Dickey-Fuller statistic on the residuals.")
    p_value: float = Field(description="p-value of the Dickey-Fuller statistic.")


class CointegrationJohansenQueryParams(QueryParams):
    """Query parameters for the Johansen cointegration endpoint."""

    __category__ = "time_series"
    __output_columns__ = (
        "rank",
        "eigenvalue",
        "trace_statistic",
        "max_eig_statistic",
    )

    data: list[Data] = Field(description="Input dataset.")
    columns: list[str] = Field(
        description="Columns (time series) to test jointly for cointegration."
    )
    deterministic_order: Literal[-1, 0, 1] = Field(
        default=0,
        description="Deterministic trend: -1 none, 0 constant, 1 constant and trend.",
    )
    k_ar_diff: PositiveInt = Field(
        default=1, description="Number of lagged differences in the model."
    )


class CointegrationJohansenData(Data):
    """Johansen cointegration result for one cointegration rank hypothesis."""

    rank: int = Field(description="Cointegration rank hypothesis (r <= rank).")
    eigenvalue: float = Field(description="Eigenvalue associated with the rank.")
    trace_statistic: float = Field(description="Trace test statistic.")
    trace_crit_90: float = Field(description="Trace critical value at the 90% level.")
    trace_crit_95: float = Field(description="Trace critical value at the 95% level.")
    trace_crit_99: float = Field(description="Trace critical value at the 99% level.")
    max_eig_statistic: float = Field(description="Maximum-eigenvalue test statistic.")
    max_eig_crit_90: float = Field(
        description="Maximum-eigenvalue critical value at the 90% level."
    )
    max_eig_crit_95: float = Field(
        description="Maximum-eigenvalue critical value at the 95% level."
    )
    max_eig_crit_99: float = Field(
        description="Maximum-eigenvalue critical value at the 99% level."
    )


class CausalityQueryParams(QueryParams):
    """Query parameters for the Granger causality endpoint."""

    __category__ = "time_series"
    __output_columns__ = ("test", "statistic", "p_value", "lag")

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Target column.")
    x_column: str = Field(description="Candidate causal column.")
    lag: PositiveInt = Field(default=3, description="Number of lags to test.")


class CausalityData(Data):
    """One sub-test of the Granger causality result."""

    test: str = Field(description="Name of the Granger sub-test.")
    statistic: float = Field(description="Test statistic.")
    p_value: float = Field(description="p-value of the test statistic.")
    lag: int = Field(description="Number of lags tested.")


class GarchQueryParams(QueryParams):
    """Query parameters for the GARCH volatility endpoint."""

    __category__ = "time_series"
    __output_columns__ = ("date", "conditional_volatility")

    data: list[Data] = Field(description="Input dataset.")
    column: str = Field(description="Column to model. Best applied to a return series.")
    x_columns: list[str] | None = Field(
        default=None,
        description="Exogenous regressor columns for the mean model"
        + " (used by the 'LS', 'ARX', and 'HARX' mean models).",
    )
    mean: Literal["Constant", "Zero", "LS", "AR", "ARX", "HAR", "HARX"] = Field(
        default="Constant",
        description="Mean model: 'Constant' (constant mean), 'Zero' (zero mean),"
        + " 'LS' (least squares), 'AR'/'ARX' (autoregressive, 'ARX' adds exogenous"
        + " regressors), 'HAR'/'HARX' (heterogeneous autoregressive).",
    )
    lags: NonNegativeInt = Field(
        default=0,
        description="Lag order of the 'AR', 'ARX', 'HAR', and 'HARX' mean models.",
    )
    vol: Literal["GARCH", "ARCH", "EGARCH", "FIGARCH", "APARCH", "HARCH"] = Field(
        default="GARCH",
        description="Volatility process: 'GARCH', 'ARCH', 'EGARCH' (exponential GARCH,"
        + " captures leverage), 'FIGARCH' (fractionally integrated, long memory),"
        + " 'APARCH' (asymmetric power ARCH), 'HARCH' (heterogeneous ARCH).",
    )
    p: PositiveInt = Field(
        default=1, description="Order of the symmetric ARCH (innovation) term."
    )
    o: NonNegativeInt = Field(
        default=0, description="Order of the asymmetric (leverage) term."
    )
    q: NonNegativeInt = Field(
        default=1, description="Order of the lagged volatility (GARCH) term."
    )
    power: PositiveFloat = Field(
        default=2.0,
        description="Power applied to the conditional volatility (2.0 is standard"
        + " GARCH; other values give power-GARCH and APARCH variants).",
    )
    distribution: Literal["normal", "t", "skewt", "ged"] = Field(
        default="normal",
        description="Distribution of the model innovations: 'normal' (Gaussian),"
        + " 't' (Student's t, fat tails), 'skewt' (skewed Student's t),"
        + " or 'ged' (generalized error distribution).",
    )


class GarchData(Data):
    """One observation of the GARCH conditional volatility series."""

    date: datetime | dateType | str | int = Field(
        description="Observation date (integer position when the input has no date)."
    )
    conditional_volatility: float = Field(
        description="Estimated conditional volatility at the observation."
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"column": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def unit_root(params: UnitRootQueryParams) -> OBBject[UnitRootData]:
    """Perform the Augmented Dickey-Fuller (ADF) unit root test.

    The ADF test checks whether a series has a unit root - a sign of non-stationarity.
    Rejecting the null hypothesis indicates the series is stationary.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from statsmodels.tsa.stattools import adfuller

    series = get_target_column(basemodel_to_df(params.data), params.column)
    result = adfuller(
        series,
        maxlag=params.maxlag,
        regression=params.regression,
        autolag=params.autolag,
    )
    adf_stat, p_value, used_lag, nobs, critical_values = result[:5]
    ic_best = result[5] if len(result) > 5 else None
    return OBBject(
        results=UnitRootData(
            adf_stat=float(adf_stat),
            p_value=float(p_value),
            used_lag=int(used_lag),
            nobs=int(nobs),
            ic_best=float(ic_best) if ic_best is not None else None,
            critical_values=dict(critical_values),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"column": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def kpss(params: KpssQueryParams) -> OBBject[KpssData]:
    """Perform the KPSS test for stationarity.

    The KPSS null hypothesis is that the series IS stationary - the opposite of the ADF
    test - so running both tests gives a more robust read on stationarity.
    """
    import warnings

    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from statsmodels.tools.sm_exceptions import InterpolationWarning
    from statsmodels.tsa.stattools import kpss as _kpss

    series = get_target_column(basemodel_to_df(params.data), params.column)
    # Capture statsmodels' off-table InterpolationWarning as a typed result field.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        statistic, p_value, lags, critical_values = _kpss(
            series, regression=params.regression, nlags=params.nlags
        )
    p_value_interpolated = not any(
        issubclass(w.category, InterpolationWarning) for w in caught
    )
    return OBBject(
        results=KpssData(
            kpss_stat=float(statistic),
            p_value=float(p_value),
            p_value_interpolated=p_value_interpolated,
            lags=int(lags),
            critical_values=dict(critical_values),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "columns": ["open", "close"],
                "data": APIEx.mock_data("timeseries"),
            }
        )
    ],
)
def cointegration(params: CointegrationQueryParams) -> OBBject[list[CointegrationData]]:
    """Test pairs of time series for cointegration via the Engle-Granger two-step test.

    Cointegration means two non-stationary series share a long-run equilibrium. The
    Engle-Granger test regresses one series on the other and checks the residuals for
    stationarity.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_columns

    from openbb_econometrics.utils import (
        get_engle_granger_two_step_cointegration_test,
    )

    dataset = get_target_columns(basemodel_to_df(params.data), params.columns)
    out = []
    for x_col, y_col in combinations(params.columns, 2):
        c, gamma, alpha, _, adf_stat, p_value = (
            get_engle_granger_two_step_cointegration_test(
                dataset[x_col], dataset[y_col]
            )
        )
        out.append(
            CointegrationData(
                pair=f"{x_col}/{y_col}",
                c=float(c),
                gamma=float(gamma),
                alpha=float(alpha),
                adf_stat=float(adf_stat),
                p_value=float(p_value),
            )
        )

    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "columns": ["open", "close"],
                "data": APIEx.mock_data("timeseries"),
            }
        )
    ],
)
def cointegration_johansen(
    params: CointegrationJohansenQueryParams,
) -> OBBject[list[CointegrationJohansenData]]:
    """Perform the Johansen cointegration test on multiple time series.

    The Johansen test detects cointegrating relationships among two or more series
    simultaneously, reporting the number of cointegrating vectors via the trace and
    maximum-eigenvalue statistics.
    """
    from openbb_core.app.utils import basemodel_to_df, get_target_columns
    from statsmodels.tsa.vector_ar.vecm import coint_johansen

    dataset = get_target_columns(basemodel_to_df(params.data), params.columns)
    result = coint_johansen(
        dataset, det_order=params.deterministic_order, k_ar_diff=params.k_ar_diff
    )
    out = [
        CointegrationJohansenData(
            rank=rank,
            eigenvalue=float(result.eig[rank]),
            trace_statistic=float(result.lr1[rank]),
            trace_crit_90=float(result.cvt[rank][0]),
            trace_crit_95=float(result.cvt[rank][1]),
            trace_crit_99=float(result.cvt[rank][2]),
            max_eig_statistic=float(result.lr2[rank]),
            max_eig_crit_90=float(result.cvm[rank][0]),
            max_eig_crit_95=float(result.cvm[rank][1]),
            max_eig_crit_99=float(result.cvm[rank][2]),
        )
        for rank in range(len(result.lr1))
    ]

    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            description="Granger causality test with mock data.",
            parameters={
                "y_column": "close",
                "x_column": "open",
                "lag": 1,
                "data": APIEx.mock_data("timeseries"),
            },
        )
    ],
)
def causality(params: CausalityQueryParams) -> OBBject[list[CausalityData]]:
    """Perform the Granger causality test to assess whether X helps predict y.

    Granger causality tests whether past values of one series improve the forecast of
    another. It is a predictive, not a structural, notion of causality.
    """
    from contextlib import redirect_stdout
    from io import StringIO

    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import concat
    from statsmodels.tsa.stattools import grangercausalitytests

    df = basemodel_to_df(params.data)
    x_series = get_target_column(df, params.x_column)
    y_series = get_target_column(df, params.y_column)

    with redirect_stdout(StringIO()):
        granger = grangercausalitytests(
            concat([y_series, x_series], axis=1), [params.lag]
        )
    out = [
        CausalityData(
            test=str(test),
            statistic=float(values[0]),
            p_value=float(values[1]),
            lag=params.lag,
        )
        for test, values in granger[params.lag][0].items()
    ]

    return OBBject(results=out)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(parameters={"column": "close", "data": APIEx.mock_data("timeseries")})
    ],
)
def garch(params: GarchQueryParams) -> OBBject[list[GarchData]]:
    """Fit a configurable volatility model from the GARCH family to a series.

    The mean model, volatility process, lag orders, power, and innovation distribution
    are all configurable. The estimated conditional volatility series is returned; the
    fitted parameters and information criteria are attached to ``OBBject.extra``. Best
    applied to a return series.
    """
    from arch import arch_model
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )
    from pandas import DataFrame, Series

    df = basemodel_to_df(params.data, index="date")
    series = get_target_column(df, params.column).astype(float)
    exog = None
    if params.x_columns:
        combined = (
            get_target_columns(df, params.x_columns)
            .astype(float)
            .join(series.rename("_endog_"))
            .dropna()
        )
        series = combined["_endog_"]
        exog = combined.drop(columns="_endog_")
    else:
        series = series.dropna()

    results = arch_model(
        series,
        x=exog,
        mean=params.mean,
        lags=params.lags,
        vol=params.vol,
        p=params.p,
        o=params.o,
        q=params.q,
        power=params.power,
        dist=params.distribution,
    ).fit(disp="off")

    volatility = Series(results.conditional_volatility).dropna()
    frame = DataFrame(
        {
            "date": volatility.index,
            "conditional_volatility": volatility.to_numpy(),
        }
    )
    out = [
        GarchData(
            date=record["date"],
            conditional_volatility=float(record["conditional_volatility"]),
        )
        for record in frame.to_dict(orient="records")
    ]

    return OBBject(
        results=out,
        extra={
            "results_metadata": {
                "params": results.params.to_dict(),
                "aic": float(results.aic),
                "bic": float(results.bic),
                "log_likelihood": float(results.loglikelihood),
            }
        },
    )
