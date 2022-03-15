"""Econometrics Model"""
__docformat__ = "numpy"

# pylint: disable=eval-used

import logging
from pathlib import Path
import warnings
from typing import Dict, Union, Any

import pandas as pd
from pandas import DataFrame
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests
from linearmodels.datasets import wage_panel

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(
    file: str,
    file_types: list,
    data_files: Dict[Any, Any],
    data_examples: Dict[Any, Any],
) -> pd.DataFrame:
    """Load custom file into dataframe.

    Parameters
    ----------
    file: str
        Path to file
    file_types: list
        Supported file types
    data_files: dict
        Contains all available data files within the Export folder
    data_examples: dict
        Contains all available examples from Statsmodels

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
    """
    if file in data_examples:
        if file == "wage_panel":
            return wage_panel.load()
        return getattr(sm.datasets, file).load_pandas().data

    if file in data_files:
        file = data_files[file]

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
            f"The file type {file_type} is not supported. Please choose one of the following: "
            f"{', '.join(file_types)}"
        )

    return data


@log_start_end(log=logger)
def get_options(
    datasets: Dict[str, pd.DataFrame], dataset_name: str = None
) -> Dict[Union[str, Any], DataFrame]:
    """Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

    Parameters
    ----------
    datasets: dict
        The available datasets.
    dataset_name: str
        The dataset you wish to show the options for.

    Returns
    -------
    option_tables: dict
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one options table.
    """
    option_tables = {}

    if dataset_name:
        columns = datasets[dataset_name].columns
        option_tables[dataset_name] = pd.DataFrame(
            {
                "dataset": [dataset_name] * len(columns),
                "column": columns,
                "option": [f"{column}-{dataset_name}" for column in columns],
            }
        )
    else:
        for dataset, data_values in datasets.items():
            columns = data_values.columns
            option_tables[dataset] = pd.DataFrame(
                {
                    "dataset": [dataset] * len(columns),
                    "column": columns,
                    "option": [f"{column}-{dataset}" for column in columns],
                }
            )

    return option_tables


@log_start_end(log=logger)
def clean(dataset: pd.DataFrame, fill: str, drop: str, limit: int) -> pd.DataFrame:
    """Clean up NaNs from the dataset

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    fill : str
        The method of filling NaNs
    drop : str
        The method of dropping NaNs
    limit : int
        The maximum limit you wish to apply that can be forward or backward filled

    Returns
    -------
    pd.DataFrame:
        Dataframe with cleaned up data
    """
    if fill:
        if fill == "rfill":
            dataset = dataset.fillna(axis="index", value=0)
        if fill == "cfill":
            dataset = dataset.fillna(axis="columns", value=0)
        elif fill == "rbfill":
            dataset = dataset.fillna(axis="index", method="bfill", limit=limit)
        elif fill == "cbfill":
            dataset = dataset.fillna(axis="columns", method="bfill", limit=limit)
        elif fill == "rffill":
            dataset = dataset.fillna(axis="index", method="ffill", limit=limit)
        elif fill == "cffill":
            dataset = dataset.fillna(axis="columns", method="ffill", limit=limit)

    if drop:
        if drop == "rdrop":
            dataset = dataset.dropna(how="any", axis="index")
        elif drop == "cdrop":
            dataset = dataset.dropna(how="any", axis="columns")

    return dataset


@log_start_end(log=logger)
def get_normality(data: pd.Series) -> pd.DataFrame:
    """
    Look at the distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.

    Parameters
    ----------
    data : pd.Series
        A series or column of a DataFrame to test normality for

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
def get_root(df: pd.Series, fuller_reg: str, kpss_reg: str) -> pd.DataFrame:
    """Calculate test statistics for unit roots

    Parameters
    ----------
    df : pd.Series
        Series or column of DataFrame of target variable
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

    vals2 = [res2[0], res2[1], res2[2], 0, 0]
    data["KPSS"] = vals2

    return data


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
        The amount of lags for the Granger test. By default, this is set to 3.
    """
    granger_set = pd.concat([time_series_y, time_series_x], axis=1)

    granger = grangercausalitytests(granger_set, [lags], verbose=False)

    return granger


def get_engle_granger_two_step_cointegration_test(y, x):
    """Estimates long-run and short-run cointegration relationship for series y and x and apply
    the two-step Engle & Granger test for cointegration.

    Uses a 2-step process to first estimate coefficients for the long-run relationship
        y_t = c + gamma * x_t + z_t

    and then the short-term relationship,
        y_t - y_(t-1) = alpha * z_(t-1) + epsilon_t,

    with z the found residuals of the first equation.

    Then tests cointegration by Dickey-Fuller phi=1 vs phi < 1 in
        z_t = phi * z_(t-1) + eta_t

    If this implies phi < 1, the z series is stationary is concluded to be
    stationary, and thus the series y and x are concluded to be cointegrated.

    Parameters
    ----------
    y : pd.Series
        The first time series of the pair to analyse.

    x : pd.Series
        The second time series of the pair to analyse.

    Returns
    -------
    c : float
        The constant term in the long-run relationship y_t = c + gamma * x_t + z_t. This
        describes the static shift of y with respect to gamma * x.

    gamma : float
        The gamma term in the long-run relationship y_t = c + gamma * x_t + z_t. This
        describes the ratio between the const-shifted y and x.

    alpha : float
        The alpha term in the short-run relationship y_t - y_(t-1) = alpha * z_(t-1) + epsilon. This
        gives an indication of the strength of the error correction toward the long-run mean.

    z : pd.Series
        Series of residuals z_t from the long-run relationship y_t = c + gamma * x_t + z_t, representing
        the value of the error correction term.

    dfstat : float
        The Dickey Fuller test-statistic for phi = 1 vs phi < 1 in the second equation. A more
        negative value implies the existence of stronger cointegration.

    pvalue : float
        The p-value corresponding to the Dickey Fuller test-statistic. A lower value implies
        stronger rejection of no-cointegration, thus stronger evidence of cointegration.

    """
    warnings.simplefilter(action="ignore", category=FutureWarning)
    long_run_ols = sm.OLS(y, sm.add_constant(x))
    warnings.simplefilter(action="default", category=FutureWarning)

    long_run_ols_fit = long_run_ols.fit()

    c, gamma = long_run_ols_fit.params
    z = long_run_ols_fit.resid

    short_run_ols = sm.OLS(y.diff().iloc[1:], (z.shift().iloc[1:]))
    short_run_ols_fit = short_run_ols.fit()

    alpha = short_run_ols_fit.params[0]

    # NOTE: The p-value returned by the adfuller function assumes we do not estimate z
    # first, but test stationarity of an unestimated series directly. This assumption
    # should have limited effect for high N, however. Critical values taking this into
    # account more accurately are provided in e.g. McKinnon (1990) and Engle & Yoo (1987).

    adfstat, pvalue, _, _, _ = adfuller(z, maxlag=1, autolag=None)

    return c, gamma, alpha, z, adfstat, pvalue
