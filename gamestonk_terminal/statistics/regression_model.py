import warnings
from typing import List, Tuple, Dict, Any

import pandas as pd
from linearmodels import PooledOLS
from linearmodels.panel import (
    RandomEffects,
    BetweenOLS,
    PanelOLS,
    FirstDifferenceOLS,
    compare,
)
from linearmodels.panel.results import PanelModelComparison
from pandas import DataFrame
from statsmodels.api import add_constant
from statsmodels.formula.api import ols
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.api import het_breuschpagan

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.statistics.statistics_model import logger


def get_regressions_results(
    regression_type: str,
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Based on the regression type, this function decides what regression to run.

    Parameters
    ----------
    regression_type: str
        The type of regression you wish to execute.
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the regression model.
    """
    if regression_type == "pols":
        return get_pols(regression_variables, data, datasets)
    if regression_type == "re":
        return get_re(regression_variables, data, datasets)
    if regression_type == "bols":
        return get_bols(regression_variables, data, datasets)
    if regression_type == "fe":
        return get_fe(regression_variables, data, datasets)
    if regression_type == "fdols":
        return get_fdols(regression_variables, data, datasets)

    return console.print(f"{regression_type} is not an option.")


def get_regression_data(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any]]:
    """This function creates a DataFrame with the required regression data as
    well sets up the dependent and independent variables.

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression = {}
    independent_variables = []
    dependent_variable = None

    for variable in regression_variables:
        column, dataset = datasets[variable].keys()
        regression[column] = data[dataset][column]

        if variable == regression_variables[0]:
            dependent_variable = column
        elif variable in regression_variables[1:]:
            independent_variables.append(column)

    regression_df = pd.DataFrame(regression)

    return regression_df, dependent_variable, independent_variables


@log_start_end(log=logger)
def get_ols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Performs an OLS regression on timeseries data. [Source: Statsmodels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        ols_regression_string = (
            f"{dependent_variable} ~ {' + '.join(independent_variables)}"
        )

        model = ols(ols_regression_string, data=regression_df).fit()
        console.print(model.summary())

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_pols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """PooledOLS is just plain OLS that understands that various panel data structures.
    It is useful as a base model. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the Pooled OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        exogenous = add_constant(regression_df[independent_variables])
        model = PooledOLS(regression_df[dependent_variable], exogenous).fit()
        console.print(model)

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_re(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """The random effects model is virtually identical to the pooled OLS model except that is accounts for the
    structure of the model and so is more efficient. Random effects uses a quasi-demeaning strategy which
    subtracts the time average of the within entity values to account for the common shock. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the RandomEffects model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        exogenous = add_constant(regression_df[independent_variables])
        model = RandomEffects(regression_df[dependent_variable], exogenous).fit()
        console.print(model)

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_bols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """The between estimator is an alternative, usually less efficient estimator, can can be used to
     estimate model parameters. It is particular simple since it first computes the time averages of
     y and x and then runs a simple regression using these averages. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the Between OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        exogenous = add_constant(regression_df[independent_variables])
        model = BetweenOLS(regression_df[dependent_variable], exogenous).fit()
        console.print(model)

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_fe(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """When effects are correlated with the regressors the RE and BE estimators are not consistent.
    The usual solution is to use Fixed Effects which are called entity_effects when applied to
    entities and time_effects when applied to the time dimension. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        exogenous = add_constant(regression_df[independent_variables])
        model = PanelOLS(
            regression_df[dependent_variable], exogenous, entity_effects=True
        ).fit()
        console.print(model)

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_fdols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """First differencing is an alternative to using fixed effects when there might be correlation.
    When using first differences, time-invariant variables must be excluded. Additionally,
    only one linear time-trending variable can be included since this will look like a constant.
    This variable will soak up all time-trends in the data, and so interpretations of
    these variable can be challenging. [Source: LinearModels]

    Parameters
    ----------
    regression_variables : list
        The regressions variables entered where the first variable is
        the dependent variable.
    data : dict
        A dictionary containing the datasets.
    datasets: dict
        A dictionary containing the column and dataset names of
        each column/dataset combination.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets
    )

    with warnings.catch_warnings(record=True) as warning_messages:
        model = FirstDifferenceOLS(
            regression_df[dependent_variable], regression_df[independent_variables]
        ).fit()
        console.print(model)

        if len(warning_messages) > 0:
            console.print("Warnings:")
            for warning in warning_messages:
                console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_comparison(regressions: Dict[Dict, Any]) -> PanelModelComparison:
    """Compare regression results between Panel Data regressions.

    Parameters
    ----------
    regressions : Dict
        Dictionary with regression results.

    Returns
    -------
    Returns a PanelModelComparison which shows an overview of the different regression results.
    """
    comparison = {}

    for regression_type, data in regressions.items():
        if regression_type == "OLS":
            continue
        if data["model"]:
            comparison[regression_type] = data["model"]

    comparison_result = compare(comparison)

    return comparison_result


@log_start_end(log=logger)
def get_dwat(residual: pd.DataFrame) -> pd.DataFrame:
    """Calculate test statistics for Durbing Watson autocorrelation

    Parameters
    ----------
    residual : OLS Model
        Model containing residual values.

    Returns
    -------
    Test statistic of the Durbin Watson test.
    """
    # Durbin Watson test: The test statistic is approximately equal to 2*(1-r) where r is the
    # sample autocorrelation of the residuals. Thus, for r == 0, indicating no serial correlation,
    # the test statistic equals 2. This statistic will always be between 0 and 4. The closer
    # to 0 the statistic, the more evidence for positive serial correlation. The closer to 4,
    # the more evidence for negative serial correlation.
    result = durbin_watson(residual)

    return round(result, 2)


@log_start_end(log=logger)
def get_bgod(model: pd.DataFrame, lags) -> tuple:
    """Calculate test statistics for autocorrelation

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.

    Returns
    -------
    Test results from the Breusch-Godfrey Test
    """

    lm_stat, p_value, f_stat, fp_value = acorr_breusch_godfrey(model, nlags=lags)

    return lm_stat, p_value, f_stat, fp_value


@log_start_end(log=logger)
def get_bpag(model: pd.DataFrame) -> tuple:
    """Calculate test statistics for heteroscedasticity

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.

    Returns
    -------
    Test results from the Breusch-Pagan Test
    """

    lm_stat, p_value, f_stat, fp_value = het_breuschpagan(model.resid, model.model.exog)

    return lm_stat, p_value, f_stat, fp_value
