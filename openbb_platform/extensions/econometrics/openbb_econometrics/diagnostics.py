"""Econometrics regression-diagnostic commands."""

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt

router = Router(prefix="", description="Econometrics regression-diagnostic commands.")


def _ols_fit(data, y_column, x_columns):
    """Fit an OLS model and return the statsmodels results object."""
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    df = basemodel_to_df(data)
    exog = sm.add_constant(get_target_columns(df, x_columns))
    endog = get_target_column(df, y_column)
    return sm.OLS(endog, exog).fit()


class AutocorrelationQueryParams(QueryParams):
    """Query parameters for the Durbin-Watson autocorrelation endpoint."""

    __category__ = "diagnostic"
    __output_columns__ = ("durbin_watson",)

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )


class AutocorrelationData(Data):
    """Durbin-Watson autocorrelation test result."""

    durbin_watson: float = Field(
        description="Durbin-Watson statistic (near 2 = no autocorrelation)."
    )


class ResidualAutocorrelationQueryParams(QueryParams):
    """Query parameters for the Breusch-Godfrey residual autocorrelation endpoint."""

    __category__ = "diagnostic"
    __output_columns__ = (
        "lm_statistic",
        "lm_p_value",
        "f_statistic",
        "f_p_value",
    )

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )
    lags: PositiveInt = Field(
        default=1, description="Number of lags to include in the test."
    )


class ResidualAutocorrelationData(Data):
    """Breusch-Godfrey residual autocorrelation test result."""

    lm_statistic: float = Field(description="Lagrange Multiplier test statistic.")
    lm_p_value: float = Field(description="p-value of the LM statistic.")
    f_statistic: float = Field(description="F-statistic of the auxiliary regression.")
    f_p_value: float = Field(description="p-value of the F-statistic.")


class HeteroskedasticityQueryParams(QueryParams):
    """Query parameters for the heteroskedasticity endpoint."""

    __category__ = "diagnostic"
    __output_columns__ = (
        "breusch_pagan_lm_statistic",
        "breusch_pagan_lm_p_value",
        "breusch_pagan_f_statistic",
        "breusch_pagan_f_p_value",
        "white_lm_statistic",
        "white_lm_p_value",
        "white_f_statistic",
        "white_f_p_value",
    )

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )
    robust: bool = Field(
        default=True,
        description="Use the robust (studentized Koenker) Breusch-Pagan variant,"
        + " which does not assume normally distributed residuals.",
    )


class HeteroskedasticityData(Data):
    """Breusch-Pagan and White heteroskedasticity test results."""

    breusch_pagan_lm_statistic: float = Field(description="Breusch-Pagan LM statistic.")
    breusch_pagan_lm_p_value: float = Field(
        description="p-value of the Breusch-Pagan LM statistic."
    )
    breusch_pagan_f_statistic: float = Field(description="Breusch-Pagan F statistic.")
    breusch_pagan_f_p_value: float = Field(
        description="p-value of the Breusch-Pagan F statistic."
    )
    white_lm_statistic: float = Field(description="White LM statistic.")
    white_lm_p_value: float = Field(description="p-value of the White LM statistic.")
    white_f_statistic: float = Field(description="White F statistic.")
    white_f_p_value: float = Field(description="p-value of the White F statistic.")


class NormalityQueryParams(QueryParams):
    """Query parameters for the Jarque-Bera normality endpoint."""

    __category__ = "diagnostic"
    __output_columns__ = ("jarque_bera", "p_value", "skew", "kurtosis")

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )


class NormalityData(Data):
    """Jarque-Bera normality test result for regression residuals."""

    jarque_bera: float = Field(description="Jarque-Bera test statistic.")
    p_value: float = Field(description="p-value of the test statistic.")
    skew: float = Field(description="Skewness of the residuals.")
    kurtosis: float = Field(description="Kurtosis of the residuals.")


class VarianceInflationFactorQueryParams(QueryParams):
    """Query parameters for the variance inflation factor endpoint."""

    __category__ = "diagnostic"
    __output_columns__ = ("variable", "vif")

    data: list[Data] = Field(description="Input dataset.")
    columns: list[str] | None = Field(
        default=None,
        description="Columns to test for collinearity. If omitted, all numeric columns.",
    )


class VarianceInflationFactorData(Data):
    """Variance inflation factor for a single variable."""

    variable: str = Field(description="Name of the variable.")
    vif: float = Field(
        description="Variance inflation factor (above 5 indicates high collinearity)."
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def autocorrelation(
    params: AutocorrelationQueryParams,
) -> OBBject[AutocorrelationData]:
    """Perform the Durbin-Watson test for autocorrelation in regression residuals.

    The Durbin-Watson statistic ranges from 0 to 4. A value near 2 suggests no
    autocorrelation; values toward 0 indicate positive autocorrelation and values
    toward 4 indicate negative autocorrelation.
    """
    from statsmodels.stats.stattools import durbin_watson

    results = _ols_fit(params.data, params.y_column, params.x_columns)
    return OBBject(
        results=AutocorrelationData(durbin_watson=float(durbin_watson(results.resid)))
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def residual_autocorrelation(
    params: ResidualAutocorrelationQueryParams,
) -> OBBject[ResidualAutocorrelationData]:
    """Perform the Breusch-Godfrey LM test for residual autocorrelation.

    The Breusch-Godfrey test detects autocorrelation in regression residuals up to a
    chosen number of lags. Significant statistics indicate the model has not captured
    some of the data's serial dependence.
    """
    from statsmodels.stats.diagnostic import acorr_breusch_godfrey

    results = _ols_fit(params.data, params.y_column, params.x_columns)
    lm_stat, lm_p_value, f_stat, f_p_value = acorr_breusch_godfrey(
        results, nlags=params.lags
    )
    return OBBject(
        results=ResidualAutocorrelationData(
            lm_statistic=float(lm_stat),
            lm_p_value=float(lm_p_value),
            f_statistic=float(f_stat),
            f_p_value=float(f_p_value),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def heteroskedasticity(
    params: HeteroskedasticityQueryParams,
) -> OBBject[HeteroskedasticityData]:
    """Perform the Breusch-Pagan and White tests for heteroskedasticity.

    Heteroskedasticity - non-constant variance of the regression residuals - violates a
    key OLS assumption and makes standard errors unreliable. The Breusch-Pagan test
    detects linear forms; the White test additionally captures non-linear forms.
    """
    from statsmodels.stats.diagnostic import het_breuschpagan, het_white

    results = _ols_fit(params.data, params.y_column, params.x_columns)
    breusch_pagan = het_breuschpagan(
        results.resid, results.model.exog, robust=params.robust
    )
    white = het_white(results.resid, results.model.exog)
    return OBBject(
        results=HeteroskedasticityData(
            breusch_pagan_lm_statistic=float(breusch_pagan[0]),
            breusch_pagan_lm_p_value=float(breusch_pagan[1]),
            breusch_pagan_f_statistic=float(breusch_pagan[2]),
            breusch_pagan_f_p_value=float(breusch_pagan[3]),
            white_lm_statistic=float(white[0]),
            white_lm_p_value=float(white[1]),
            white_f_statistic=float(white[2]),
            white_f_p_value=float(white[3]),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def normality(params: NormalityQueryParams) -> OBBject[NormalityData]:
    """Perform the Jarque-Bera normality test on regression residuals.

    The Jarque-Bera test checks whether OLS residuals are normally distributed by
    comparing their skewness and kurtosis to those of a normal distribution.
    """
    from statsmodels.stats.stattools import jarque_bera

    results = _ols_fit(params.data, params.y_column, params.x_columns)
    jb_stat, jb_p_value, skew, kurtosis = jarque_bera(results.resid)
    return OBBject(
        results=NormalityData(
            jarque_bera=float(jb_stat),
            p_value=float(jb_p_value),
            skew=float(skew),
            kurtosis=float(kurtosis),
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Calculate the variance inflation factor.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.variance_inflation_factor(data=stock_data, columns=["open", "high", "low", "close"])',  # noqa: E501
            ],
        ),
        APIEx(
            parameters={
                "columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def variance_inflation_factor(
    params: VarianceInflationFactorQueryParams,
) -> OBBject[list[VarianceInflationFactorData]]:
    """Calculate the variance inflation factor (VIF) to detect multicollinearity.

    VIF quantifies how much the variance of an estimated coefficient is inflated by
    collinearity with the other regressors. A VIF between 1 and 5 is generally
    acceptable; values above 5 indicate high collinearity.
    """
    from openbb_core.app.utils import basemodel_to_df
    from statsmodels.stats.outliers_influence import (
        variance_inflation_factor as _vif,
    )
    from statsmodels.tools.tools import add_constant

    dataset = basemodel_to_df(params.data)
    dataset = dataset if params.columns is None else dataset[params.columns]
    df = add_constant(dataset).select_dtypes(
        exclude=["object", "datetime", "timedelta"]
    )

    out = [
        VarianceInflationFactorData(
            variable=str(df.columns[i]), vif=float(_vif(df.values, i))
        )
        for i in range(1, len(df.columns))
    ]

    return OBBject(results=out)
