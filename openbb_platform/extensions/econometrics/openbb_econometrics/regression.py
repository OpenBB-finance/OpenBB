"""Econometrics regression commands - Ordinary Least Squares."""

from typing import Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

router = Router(prefix="", description="Econometrics regression commands.")


class OlsRegressionQueryParams(QueryParams):
    """Query parameters for the OLS regression endpoint."""

    __category__ = "regression"
    __output_columns__ = (
        "variable",
        "coefficient",
        "standard_error",
        "t_statistic",
        "p_value",
        "conf_int_lower",
        "conf_int_upper",
    )

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )
    cov_type: Literal["nonrobust", "HC0", "HC1", "HC2", "HC3"] = Field(
        default="nonrobust",
        description="Covariance estimator for the standard errors: 'nonrobust', or"
        + " heteroskedasticity-robust 'HC0', 'HC1', 'HC2', or 'HC3'.",
    )


class OlsRegressionData(Data):
    """One estimated coefficient of an OLS regression."""

    variable: str = Field(
        description="Name of the regressor ('const' is the intercept)."
    )
    coefficient: float = Field(description="Estimated coefficient.")
    standard_error: float = Field(description="Standard error of the coefficient.")
    t_statistic: float = Field(
        description="t-statistic for the null hypothesis that the coefficient is zero."
    )
    p_value: float = Field(description="Two-sided p-value of the t-statistic.")
    conf_int_lower: float = Field(
        description="Lower bound of the 95% confidence interval."
    )
    conf_int_upper: float = Field(
        description="Upper bound of the 95% confidence interval."
    )


class OlsRegressionSummaryQueryParams(QueryParams):
    """Query parameters for the OLS regression summary endpoint."""

    __category__ = "regression"
    __output_columns__ = (
        "r_squared",
        "adjusted_r_squared",
        "f_statistic",
        "f_p_value",
        "aic",
        "bic",
        "log_likelihood",
        "nobs",
        "df_model",
        "df_residuals",
    )

    data: list[Data] = Field(description="Input dataset.")
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )
    cov_type: Literal["nonrobust", "HC0", "HC1", "HC2", "HC3"] = Field(
        default="nonrobust",
        description="Covariance estimator for the standard errors: 'nonrobust', or"
        + " heteroskedasticity-robust 'HC0', 'HC1', 'HC2', or 'HC3'.",
    )


class OlsRegressionSummaryData(Data):
    """Goodness-of-fit summary of an OLS regression."""

    r_squared: float = Field(description="Coefficient of determination.")
    adjusted_r_squared: float = Field(
        description="R-squared adjusted for the number of regressors."
    )
    f_statistic: float | None = Field(
        default=None, description="F-statistic of the overall regression."
    )
    f_p_value: float | None = Field(
        default=None, description="p-value of the F-statistic."
    )
    aic: float = Field(description="Akaike Information Criterion.")
    bic: float = Field(description="Bayesian Information Criterion.")
    log_likelihood: float = Field(description="Log-likelihood of the fitted model.")
    nobs: int = Field(description="Number of observations.")
    df_model: float = Field(description="Model degrees of freedom.")
    df_residuals: float = Field(description="Residual degrees of freedom.")
    summary: str = Field(description="Full statsmodels text summary.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Ordinary Least Squares (OLS) regression.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.ols_regression(data=stock_data, y_column="close", x_columns=["open", "high", "low"])',  # noqa: E501
            ],
        ),
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def ols_regression(
    params: OlsRegressionQueryParams,
) -> OBBject[list[OlsRegressionData]]:
    """Perform Ordinary Least Squares (OLS) regression.

    OLS fits the best linear relationship between a dependent variable and one or more
    independent variables. Returns the estimated coefficient table - one row per
    regressor, with standard errors, t-statistics, p-values, and confidence intervals.
    """
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    df = basemodel_to_df(params.data)
    exog = sm.add_constant(get_target_columns(df, params.x_columns))
    endog = get_target_column(df, params.y_column)
    results = sm.OLS(endog, exog).fit(cov_type=params.cov_type)
    conf_int = results.conf_int()

    out = []
    for variable in results.params.index:
        bounds = conf_int.loc[variable]
        out.append(
            OlsRegressionData(
                variable=str(variable),
                coefficient=float(results.params[variable]),
                standard_error=float(results.bse[variable]),
                t_statistic=float(results.tvalues[variable]),
                p_value=float(results.pvalues[variable]),
                conf_int_lower=float(bounds.iloc[0]),
                conf_int_upper=float(bounds.iloc[1]),
            )
        )

    return OBBject(results=out)


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
def ols_regression_summary(
    params: OlsRegressionSummaryQueryParams,
) -> OBBject[OlsRegressionSummaryData]:
    """Perform Ordinary Least Squares (OLS) regression and return the fit summary.

    Returns the model-level goodness-of-fit statistics - R-squared, F-statistic,
    information criteria, log-likelihood, and degrees of freedom - along with the full
    statsmodels text summary.
    """
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    df = basemodel_to_df(params.data)
    exog = sm.add_constant(get_target_columns(df, params.x_columns))
    endog = get_target_column(df, params.y_column)

    try:
        exog = exog.astype(float)
        endog = endog.astype(float)
    except ValueError as exc:
        raise ValueError("All columns must be numeric.") from exc

    results = sm.OLS(endog, exog).fit(cov_type=params.cov_type)

    return OBBject(
        results=OlsRegressionSummaryData(
            r_squared=float(results.rsquared),
            adjusted_r_squared=float(results.rsquared_adj),
            f_statistic=(float(results.fvalue) if results.fvalue is not None else None),
            f_p_value=(
                float(results.f_pvalue) if results.f_pvalue is not None else None
            ),
            aic=float(results.aic),
            bic=float(results.bic),
            log_likelihood=float(results.llf),
            nobs=int(results.nobs),
            df_model=float(results.df_model),
            df_residuals=float(results.df_resid),
            summary=str(results.summary()),
        )
    )
