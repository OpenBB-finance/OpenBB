"""Econometrics panel-data regression commands."""

from typing import Literal

from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

router = Router(prefix="", description="Econometrics panel-data regression commands.")


class PanelRegressionQueryParams(QueryParams):
    """Query parameters shared by every panel-data regression endpoint."""

    __category__ = "panel"
    __output_columns__ = (
        "variable",
        "coefficient",
        "standard_error",
        "t_statistic",
        "p_value",
        "conf_int_lower",
        "conf_int_upper",
    )

    data: list[Data] = Field(
        description="Input panel dataset, indexed by entity and time."
    )
    y_column: str = Field(description="Name of the dependent (target) column.")
    x_columns: list[str] = Field(
        description="Names of the independent (exogenous) columns."
    )
    cov_type: Literal["unadjusted", "robust"] = Field(
        default="unadjusted",
        description="Covariance estimator: 'unadjusted' (homoskedastic) or 'robust'"
        + " (heteroskedasticity-robust standard errors).",
    )


class PanelFixedQueryParams(PanelRegressionQueryParams):
    """Query parameters for the fixed-effects panel regression endpoint."""

    entity_effects: bool = Field(
        default=True, description="Include entity-specific fixed effects."
    )
    time_effects: bool = Field(
        default=False, description="Include time-specific fixed effects."
    )


class PanelRegressionData(Data):
    """One estimated coefficient of a panel-data regression."""

    variable: str = Field(description="Name of the regressor.")
    coefficient: float = Field(description="Estimated coefficient.")
    standard_error: float = Field(description="Standard error of the coefficient.")
    t_statistic: float = Field(
        description="t-statistic for the null hypothesis that the coefficient is zero."
    )
    p_value: float = Field(description="p-value of the t-statistic.")
    conf_int_lower: float = Field(
        description="Lower bound of the 95% confidence interval."
    )
    conf_int_upper: float = Field(
        description="Upper bound of the 95% confidence interval."
    )


def _fit_panel(estimator, params, *, add_constant=True, min_observations=0):
    """Fit a linearmodels panel estimator and return its results object."""
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    df = basemodel_to_df(params.data)
    exog = get_target_columns(df, params.x_columns)
    if min_observations and len(exog) < min_observations:
        raise ValueError(
            f"This analysis requires at least {min_observations} items in the dataset."
        )
    endog = get_target_column(df, params.y_column)
    if add_constant:
        exog = sm.add_constant(exog)
    model_kwargs: dict = {}
    if hasattr(params, "entity_effects"):
        model_kwargs["entity_effects"] = params.entity_effects
        model_kwargs["time_effects"] = params.time_effects
    return estimator(endog, exog, **model_kwargs).fit(cov_type=params.cov_type)


def _to_rows(results) -> list[PanelRegressionData]:
    """Convert a linearmodels results object into PanelRegressionData rows."""
    conf_int = results.conf_int()
    return [
        PanelRegressionData(
            variable=str(variable),
            coefficient=float(results.params[variable]),
            standard_error=float(results.std_errors[variable]),
            t_statistic=float(results.tstats[variable]),
            p_value=float(results.pvalues[variable]),
            conf_int_lower=float(conf_int.loc[variable, "lower"]),
            conf_int_upper=float(conf_int.loc[variable, "upper"]),
        )
        for variable in results.params.index
    ]


_PANEL_EXAMPLE = APIEx(
    parameters={
        "y_column": "portfolio_value",
        "x_columns": ["risk_free_rate"],
        "data": APIEx.mock_data("panel"),
    }
)


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_random_effects(
    params: PanelRegressionQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a one-way Random Effects model for panel data.

    The Random Effects model treats entity-specific deviations as random draws,
    capturing variation across entities while pooling information for efficient
    estimation. Requires at least three observations.
    """
    from linearmodels.panel import RandomEffects

    results = _fit_panel(RandomEffects, params, min_observations=3)
    return OBBject(results=_to_rows(results))


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_between(
    params: PanelRegressionQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a Between regression on panel data.

    The Between estimator regresses the entity-level means, summarising the long-run
    cross-sectional relationship between the regressors and the target.
    """
    from linearmodels.panel import BetweenOLS

    results = _fit_panel(BetweenOLS, params)
    return OBBject(results=_to_rows(results))


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_pooled(
    params: PanelRegressionQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a Pooled OLS regression on panel data.

    The Pooled estimator treats the panel as one large cross-section, assuming the
    regressors have a uniform effect across all entities and time periods.
    """
    from linearmodels.panel import PooledOLS

    results = _fit_panel(PooledOLS, params)
    return OBBject(results=_to_rows(results))


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_fixed(
    params: PanelFixedQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a Fixed Effects regression on panel data.

    The Fixed Effects estimator controls for entity- and/or time-specific effects,
    isolating the effect of the regressors from unobserved heterogeneity.
    """
    from linearmodels.panel import PanelOLS

    results = _fit_panel(PanelOLS, params, add_constant=False)
    return OBBject(results=_to_rows(results))


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_first_difference(
    params: PanelRegressionQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a First-Difference regression on panel data.

    Differencing consecutive observations removes time-invariant entity effects, so the
    estimator measures how changes in the regressors relate to changes in the target.
    """
    from linearmodels.panel import FirstDifferenceOLS

    results = _fit_panel(FirstDifferenceOLS, params, add_constant=False)
    return OBBject(results=_to_rows(results))


@router.command(methods=["POST"], examples=[_PANEL_EXAMPLE])
def panel_fmac(
    params: PanelRegressionQueryParams,
) -> OBBject[list[PanelRegressionData]]:
    """Estimate a Fama-MacBeth regression on panel data.

    The Fama-MacBeth procedure runs a cross-sectional regression each period and
    averages the coefficients over time - widely used to estimate risk premia.
    """
    from linearmodels.panel import FamaMacBeth

    results = _fit_panel(FamaMacBeth, params)
    return OBBject(results=_to_rows(results))
