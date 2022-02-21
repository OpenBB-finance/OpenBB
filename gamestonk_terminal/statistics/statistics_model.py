"""Custom Controller Model"""
__docformat__ = "numpy"


import logging
import warnings
from pathlib import Path
from typing import Any, Tuple, Dict, List

import pandas as pd
from pandas import DataFrame
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(file: str, file_types: list) -> pd.DataFrame:
    """Load custom file into dataframe.

    Parameters
    ----------
    file: str
        Path to file
    file_types: list
        Supported file types

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
    """
    if not Path(file).exists():
        console.print(f"[red]Can not find the file {file}[/red]\n")
        return pd.DataFrame()

    file_type = Path(file).suffix

    if file_type == ".xlsx":
        data = pd.read_excel(file)
    elif file_type == ".csv":
        data = pd.read_csv(file)
    else:
        return console.print(
            f"The file type {file_type} is not supported. Please choose one of the following: {', '.join(file_types)}"
        )

    return data


@log_start_end(log=logger)
def get_normality(data: pd.DataFrame) -> pd.DataFrame:
    """
    Look at the distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of targeted data

    Returns
    -------
    pd.DataFrame
        Dataframe containing statistics of normality
    """
    # Kurtosis: measures height and sharpness of the central peak relative to that of a standard bell curve
    k, kpval = stats.kurtosistest(data)

    # Skewness: measure of the asymmetry of the probability distribution of a random variable about its mean
    s, spval = stats.skewtest(data)

    # Jarque-Bera goodness of fit test on sample data: tests if the sample data has the skewness and kurtosis
    # matching a normal distribution
    jb, jbpval = stats.jarque_bera(data)

    # The Shapiro-Wilk test: tests the null hypothesis that the data was drawn from a normal distribution.
    sh, shpval = stats.shapiro(data)

    # Kolmogorov-Smirnov: the one-sample test compares the underlying distribution F(x) of a sample
    # against a given distribution G(x). Comparing to normal here.
    ks, kspval = stats.kstest(data, "norm")

    l_statistic = [k, s, jb, sh, ks]
    l_pvalue = [kpval, spval, jbpval, shpval, kspval]

    return pd.DataFrame(
        [l_statistic, l_pvalue],
        columns=[
            "Kurtosis",
            "Skewness",
            "Jarque-Bera",
            "Shapiro-Wilk",
            "Kolmogorov-Smirnov",
        ],
        index=["Statistic", "p-value"],
    )


@log_start_end(log=logger)
def get_unitroot(df: pd.DataFrame, fuller_reg: str, kpss_reg: str) -> pd.DataFrame:
    """Calculate test statistics for unit roots

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of target variable
    fuller_reg : str
        Type of regression of ADF test
    kpss_reg : str
        Type of regression for KPSS test

    Returns
    -------
    pd.DataFrame
        Dataframe with results of ADF test and KPSS test
    """
    # The Augmented Dickey-Fuller test: used to test for a unit root in a univariate process in the
    # presence of serial correlation.
    result = adfuller(df, regression=fuller_reg)
    cols = ["Test Statistic", "P-Value", "NLags", "Nobs", "ICBest"]
    vals = [result[0], result[1], result[2], result[3], result[5]]
    data = pd.DataFrame(data=vals, index=cols, columns=["ADF"])

    # Kwiatkowski-Phillips-Schmidt-Shin test: test for level or trend stationarity
    # Note: this test seems to produce an Interpolation Error which says
    # The test statistic is outside the range of p-values available in the
    # look-up table. The actual p-value is greater than the p-value returned.
    # Wrap this in catch_warnings to prevent this
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res2 = kpss(df, regression=kpss_reg, nlags="auto")

    vals2 = [res2[0], res2[1], res2[2], "", ""]
    data["KPSS"] = vals2

    return data


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


@log_start_end(log=logger)
def get_granger_causality(time_series_y, time_series_x, lags):
    """Calculate granger tests

    Parameters
    ----------
    time_series_y : Series
        The series you want to test Granger Causality for.
    time_series_x : Series
        The series that you want to test whether it Granger-causes time_series_y
    lags : int
        The amoiunt of lags for the Granger test. By default, this is set to 3.
    """
    granger_set = pd.concat([time_series_y, time_series_x], axis=1)

    granger = grangercausalitytests(granger_set, [lags], verbose=False)

    return granger
