"""Regression Model"""
__docformat__ = "numpy"

import os
import warnings
import logging
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
from pandas import DataFrame
from statsmodels.api import add_constant
import statsmodels.api as sm
from statsmodels.stats.api import het_breuschpagan
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from statsmodels.stats.stattools import durbin_watson

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def get_regressions_results(
    regression_type: str,
    regression_variables: List[Tuple],
    data: Dict[str, pd.DataFrame],
    datasets: Dict[pd.DataFrame, Any],
    entity_effects: bool = False,
    time_effects: bool = False,
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
    entity_effects: bool
        Whether to apply Fixed Effects on entities.
    time_effects: bool
        Whether to apply Fixed Effects on time.

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the regression model.
    """
    if regression_type == "OLS":
        return get_ols(regression_variables, data, datasets, False)
    if regression_type == "POLS":
        return get_pols(regression_variables, data, datasets)
    if regression_type == "RE":
        return get_re(regression_variables, data, datasets)
    if regression_type == "BOLS":
        return get_bols(regression_variables, data, datasets)
    if regression_type == "FE":
        return get_fe(
            regression_variables, data, datasets, entity_effects, time_effects
        )
    if regression_type == "FDOLS":
        return get_fdols(regression_variables, data, datasets)

    return console.print(f"{regression_type} is not an option.")


def get_regression_data(
    regression_variables: List[tuple],
    data: Dict[str, pd.DataFrame],
    datasets: Dict[pd.DataFrame, Any],
    regression_type: str = "",
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
    regression_type: str
        The type of regression that is executed.

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
        regression[f"{column}_{dataset}"] = data[dataset][column]

        if variable == regression_variables[0]:
            dependent_variable = f"{column}_{dataset}"
        elif variable in regression_variables[1:]:
            independent_variables.append(f"{column}_{dataset}")

    regression_df = pd.DataFrame(regression)
    nan_values = regression_df.isnull().sum().sum()

    if nan_values > 0:
        regression_df = regression_df.dropna(how="any", axis="index")

        if regression_df.empty:
            console.print(
                f"The resulting DataFrame only consists of NaN values. This is usually due to an index "
                f"mismatch. Therefore, no {regression_type} regression can be performed. Consider revisiting your "
                "dataset(s) and adjust accordingly."
            )
        else:
            console.print(
                f"The resulting DataFrame has {nan_values} NaN values. This is usually due to "
                f"an index mismatch. Rows that contain NaNs are dropped to be able to perform the {regression_type} "
                f"regression. Consider revisiting your dataset(s) and adjust accordingly."
            )

    return regression_df, dependent_variable, independent_variables


@log_start_end(log=logger)
def get_ols(
    regression_variables: List[Tuple],
    data: Dict[str, pd.DataFrame],
    datasets: Dict[pd.DataFrame, Any],
    show_regression: bool = True,
    export: str = "",
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
    show_regression: bool
        Whether to show the regression results table.
    export: str
        Format to export data

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets, "OLS"
    )

    if regression_df.empty:
        model = None
    else:
        with warnings.catch_warnings(record=True) as warning_messages:
            model = sm.OLS(
                regression_df[dependent_variable], regression_df[independent_variables]
            ).fit()

            if show_regression:
                console.print(model.summary())
                console.print("")
            if len(warning_messages) > 0:
                console.print("Warnings:")
                for warning in warning_messages:
                    console.print(f"[red]{warning.message}[/red]".replace("\n", ""))

        if export:
            results_as_html = model.summary().tables[1].as_html()
            df = pd.read_html(results_as_html, header=0, index_col=0)[0]

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{dependent_variable}_ols_regression",
                df,
            )
        else:
            console.print("")

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_pols(
    regression_variables: List[Tuple],
    data: Dict[str, pd.DataFrame],
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
        regression_variables, data, datasets, "POLS"
    )

    if regression_df.empty:
        model = None
    else:
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
    data: Dict[str, pd.DataFrame],
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
        regression_variables, data, datasets, "RE"
    )

    if regression_df.empty:
        model = None
    else:
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
    data: Dict[str, pd.DataFrame],
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
        regression_variables, data, datasets, "BOLS"
    )

    if regression_df.empty:
        model = None
    else:
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
    data: Dict[str, pd.DataFrame],
    datasets: Dict[pd.DataFrame, Any],
    entity_effects: bool = False,
    time_effects: bool = False,
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
    entity_effects : bool
        Whether to include entity effects
    time_effects : bool
        Whether to include time effects

    Returns
    -------
    The dataset used, the dependent variable, the independent variable and
    the OLS model.
    """

    regression_df, dependent_variable, independent_variables = get_regression_data(
        regression_variables, data, datasets, "FE"
    )

    if regression_df.empty:
        model = None
    else:
        with warnings.catch_warnings(record=True) as warning_messages:
            exogenous = add_constant(regression_df[independent_variables])
            model = PanelOLS(
                regression_df[dependent_variable],
                exogenous,
                entity_effects=entity_effects,
                time_effects=time_effects,
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
    data: Dict[str, pd.DataFrame],
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
        regression_variables, data, datasets, "FDOLS"
    )

    if regression_df.empty:
        model = None
    else:
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
def get_comparison(regressions, export: str = ""):
    """Compare regression results between Panel Data regressions.

    Parameters
    ----------
    regressions : Dict
        Dictionary with regression results.
    export : str
        Format to export data

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

    if not comparison:
        # When the dictionary is empty, it means no Panel regression
        # estimates are available and thus the function will have no output
        return console.print(
            "No Panel regression estimates available. Please use the "
            "command 'panel' before using this command."
        )

    comparison_result = compare(comparison)
    console.print(comparison_result)

    if export:
        results_as_html = comparison_result.summary.tables[0].as_html()
        df = pd.read_html(results_as_html, header=0, index_col=0)[0]

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "regressions_compare",
            df,
        )

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
def get_bgod(model: pd.DataFrame, lags: int) -> tuple:
    """Calculate test statistics for autocorrelation

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags.

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
