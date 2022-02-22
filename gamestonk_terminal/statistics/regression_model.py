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

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.statistics.statistics_model import logger


def get_regression_data(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any]]:
    """Calculate test statistics for autocorrelation

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

    for variable in regression_variables:
        column, dataset = datasets[variable].keys()
        regression[column] = data[dataset][column]

        if variable == regression_variables[0]:
            dependent_variable = column
        elif variable == regression_variables[1]:
            independent_variables = [column]
        else:
            independent_variables.append(column)

    regression_df = pd.DataFrame(regression)

    return regression_df, dependent_variable, independent_variables


@log_start_end(log=logger)
def get_ols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    ols_regression_string = (
        f"{dependent_variable} ~ {' + '.join(independent_variables)}"
    )

    model = ols(ols_regression_string, data=regression_df).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_pols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    exogenous = add_constant(regression_df[independent_variables])
    model = PooledOLS(regression_df[dependent_variable], exogenous).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_bols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    exogenous = add_constant(regression_df[independent_variables])
    model = BetweenOLS(regression_df[dependent_variable], exogenous).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_fdols(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    model = FirstDifferenceOLS(
        regression_df[dependent_variable], regression_df[independent_variables]
    ).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_re(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    exogenous = add_constant(regression_df[independent_variables])
    model = RandomEffects(regression_df[dependent_variable], exogenous).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_fe(
    regression_variables: List[Tuple],
    data: Dict[pd.DataFrame, Any],
    datasets: Dict[pd.DataFrame, Any],
) -> Tuple[DataFrame, Any, List[Any], Any]:
    """Calculate test statistics for autocorrelation

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

    exogenous = add_constant(regression_df[independent_variables])
    model = PanelOLS(
        regression_df[dependent_variable], exogenous, entity_effects=True
    ).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_comparison(regressions: Dict[Dict, Any]) -> PanelModelComparison:
    """Calculate test statistics for autocorrelation

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

    t_stat, p_value, f_stat, fp_value = acorr_breusch_godfrey(model, nlags=lags)

    return t_stat, p_value, f_stat, fp_value
