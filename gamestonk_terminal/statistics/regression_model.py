from typing import List, Tuple, Dict, Any

import pandas as pd
from pandas import DataFrame
from statsmodels.formula.api import ols
from statsmodels.stats.stattools import durbin_watson

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.statistics.statistics_model import logger


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
    ols_regression_string = (
        f"{dependent_variable} ~ {' + '.join(independent_variables)}"
    )

    model = ols(ols_regression_string, data=regression_df).fit()

    return regression_df, dependent_variable, independent_variables, model


@log_start_end(log=logger)
def get_autocorrelation(residual: pd.DataFrame) -> pd.DataFrame:
    """Calculate test statistics for autocorrelation

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
