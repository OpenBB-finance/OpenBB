"""Econometrics Model"""
__docformat__ = "numpy"

# pylint: disable=eval-used

import logging
import warnings
from itertools import combinations
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_options(
    datasets: Dict[str, pd.DataFrame], dataset_name: str = ""
) -> Dict[Union[str, Any], pd.DataFrame]:
    """Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

    Parameters
    ----------
    datasets: dict
        The available datasets.
    dataset_name: str
        The dataset you wish to show the options for.

    Returns
    -------
    Dict[Union[str, Any], pd.DataFrame]
        A dictionary with a DataFrame for each option. With dataset_name set, only shows one
        options table.
    """
    option_tables = {}

    if dataset_name:
        columns = datasets[dataset_name].columns
        option_tables[dataset_name] = pd.DataFrame(
            {
                "column": columns,
                "option": [f"{dataset_name}.{column}" for column in columns],
            }
        )
    else:
        for dataset, data_values in datasets.items():
            columns = data_values.columns
            option_tables[dataset] = pd.DataFrame(
                {
                    "column": columns,
                    "option": [f"{dataset}.{column}" for column in columns],
                }
            )

    return option_tables


@log_start_end(log=logger)
def get_corr_df(data: pd.DataFrame) -> pd.DataFrame:
    """Returns correlation for a given df

    Parameters
    ----------
    data: pd.DataFrame
        The df to produce statistics for

    Returns
    -------
    df: pd.DataFrame
        The df with the new data
    """
    corr = data.corr(numeric_only=True)
    return corr


@log_start_end(log=logger)
def clean(
    dataset: pd.DataFrame,
    fill: str = "",
    drop: str = "",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Clean up NaNs from the dataset

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    fill : str
        The method of filling NaNs. Choose from:
        rfill, cfill, rbfill, cbfill, rffill, cffill
    drop : str
        The method of dropping NaNs. Choose from:
        rdrop, cdrop
    limit : int
        The maximum limit you wish to apply that can be forward or backward filled

    Returns
    -------
    pd.DataFrame
        Dataframe with cleaned up data
    """
    fill_dict = {
        "rfill": lambda x: x.fillna(axis="index", value=0),
        "cfill": lambda x: x.fillna(axis="columns", value=0),
        "rbfill": lambda x: x.fillna(axis="index", method="bfill", limit=limit),
        "cbfill": lambda x: x.fillna(axis="columns", method="bfill", limit=limit),
        "rffill": lambda x: x.fillna(axis="index", method="ffill", limit=limit),
        "cffill": lambda x: x.fillna(axis="columns", method="ffill", limit=limit),
    }

    if fill and fill in fill_dict:
        dataset = fill_dict[fill](dataset)

    if drop:
        if drop == "rdrop":
            dataset = dataset.dropna(how="any", axis="index")
        elif drop == "cdrop":
            dataset = dataset.dropna(how="any", axis="columns")

    return dataset


@log_start_end(log=logger)
def get_normality(data: pd.Series) -> pd.DataFrame:
    """
    The distribution of returns and generate statistics on the relation to the normal curve.
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
    # Kurtosis: measures height and sharpness of the central peak relative to standard bell curve
    k, kpval = stats.kurtosistest(data)
    kpval = round(kpval, 5)

    # Skewness: measure of the asymmetry of the probability distribution of a random variable about its mean
    s, spval = stats.skewtest(data)
    spval = round(spval, 5)

    # Jarque-Bera goodness of fit test on sample data: tests if the sample data has the skewness and kurtosis
    # matching a normal distribution
    jb, jbpval = stats.jarque_bera(data)
    jbpval = round(jbpval, 5)

    # The Shapiro-Wilk test: tests the null hypothesis that the data was drawn from a normal distribution.
    sh, shpval = stats.shapiro(data)
    shpval = round(shpval, 5)

    # Kolmogorov-Smirnov: the one-sample test compares the underlying distribution F(x) of a sample
    # against a given distribution G(x). Comparing to normal here.
    ks, kspval = stats.kstest(data, "norm")
    kspval = round(kspval, 5)

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
def get_root(
    data: pd.Series, fuller_reg: str = "c", kpss_reg: str = "c"
) -> pd.DataFrame:
    """Calculate test statistics for unit roots

    Parameters
    ----------
    data : pd.Series
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
    result = adfuller(data, regression=fuller_reg)
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
        res2 = kpss(data, regression=kpss_reg, nlags="auto")

    vals2 = [res2[0], res2[1], res2[2], 0, 0]
    data["KPSS"] = vals2

    return data


@log_start_end(log=logger)
def get_granger_causality(
    dependent_series: pd.Series, independent_series: pd.Series, lags: int = 3
) -> dict:
    """Calculate granger tests

    Parameters
    ----------
    dependent_series: Series
        The series you want to test Granger Causality for.
    independent_series: Series
        The series that you want to test whether it Granger-causes time_series_y
    lags : int
        The amount of lags for the Granger test. By default, this is set to 3.

    Returns
    -------
    dict
        Dictionary containing results of Granger test
    """
    granger_set = pd.concat([dependent_series, independent_series], axis=1)

    granger = grangercausalitytests(granger_set, [lags], verbose=False)

    for test in granger[lags][0]:
        # As ssr_chi2test and lrtest have one less value in the tuple, we fill
        # this value with a '-' to allow the conversion to a DataFrame
        if len(granger[lags][0][test]) != 4:
            pars = granger[lags][0][test]
            granger[lags][0][test] = (pars[0], pars[1], "-", pars[2])

    granger_df = pd.DataFrame(
        granger[lags][0], index=["F-test", "P-value", "Count", "Lags"]
    ).T

    return granger_df


# TODO: Maybe make a new function to return z instead of having this flag.
# TODO: Allow for numpy arrays as well
def get_coint_df(
    *datasets: pd.Series, return_z: bool = False
) -> Union[pd.DataFrame, Dict]:
    """Calculate cointegration tests between variable number of input series

    Parameters
    ----------
    datasets : pd.Series
        Input series to test cointegration for
    return_z : bool
        Flag to return the z data to plot

    Returns
    -------
    Union[pd.DataFrame,Dict]
        Dataframe with results of cointegration tests or a Dict of the z results
    """
    result: Dict[str, list] = {}
    z_values: Dict[str, pd.Series] = {}

    # The *datasets lets us pass in a variable number of arguments
    # Here we are getting all possible combinations of unique inputs

    pairs = list(combinations(datasets, 2))
    for x, y in pairs:
        if sum(y.isnull()) > 0:
            console.print(
                f"The Series {y} has nan-values. Please consider dropping or filling these "
                f"values with 'clean'."
            )
        elif sum(x.isnull()) > 0:
            console.print(
                f"The Series {x.name} has nan-values. Please consider dropping or filling these "
                f"values with 'clean'."
            )
        elif not y.index.equals(x.index):
            console.print(
                f"The Series {y.name} and {x.name} do not have the same index."
            )
        (
            c,
            gamma,
            alpha,
            z,
            adfstat,
            pvalue,
        ) = get_engle_granger_two_step_cointegration_test(x, y)
        result[f"{x.name}/{y.name}"] = [c, gamma, alpha, adfstat, pvalue]
        z_values[f"{x.name}/{y.name}"] = z

    if result and z_values:
        if return_z:
            return z_values
        df = pd.DataFrame.from_dict(
            result,
            orient="index",
            columns=["Constant", "Gamma", "Alpha", "Dickey-Fuller", "P Value"],
        )
        return df
    return pd.DataFrame()


def get_engle_granger_two_step_cointegration_test(
    dependent_series: pd.Series, independent_series: pd.Series
) -> Tuple[float, float, float, pd.Series, float, float]:
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
    dependent_series : pd.Series
        The first time series of the pair to analyse.
    independent_series : pd.Series
        The second time series of the pair to analyse.

    Returns
    -------
    Tuple[float, float, float, pd.Series, float, float]
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
    long_run_ols = sm.OLS(dependent_series, sm.add_constant(independent_series))
    warnings.simplefilter(action="default", category=FutureWarning)

    long_run_ols_fit = long_run_ols.fit()

    c, gamma = long_run_ols_fit.params
    z = long_run_ols_fit.resid

    short_run_ols = sm.OLS(dependent_series.diff().iloc[1:], (z.shift().iloc[1:]))
    short_run_ols_fit = short_run_ols.fit()

    alpha = short_run_ols_fit.params[0]

    # NOTE: The p-value returned by the adfuller function assumes we do not estimate z
    # first, but test stationarity of an unestimated series directly. This assumption
    # should have limited effect for high N, however. Critical values taking this into
    # account more accurately are provided in e.g. McKinnon (1990) and Engle & Yoo (1987).

    adfstat, pvalue, _, _, _ = adfuller(z, maxlag=1, autolag=None)

    return c, gamma, alpha, z, adfstat, pvalue
