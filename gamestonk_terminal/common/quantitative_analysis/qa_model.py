"""Quantitative Analysis Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import Any, Tuple

import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss

from gamestonk_terminal.decorators import log_start_end

# TODO : Since these are common/ they should be independent of 'stock' info.
# df_stock should be replaced with a generic df and a column variable


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Print summary statistics

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to get summary statistics for
    """

    df_stats = df.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    df_stats.loc["var"] = df_stats.loc["std"] ** 2

    return df_stats


@log_start_end(log=logger)
def get_seasonal_decomposition(
    df: pd.DataFrame, multiplicative: bool
) -> Tuple[Any, pd.DataFrame, pd.DataFrame]:
    """Perform seasonal decomposition

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of targeted data
    multiplicative : bool
        Boolean to indicate multiplication instead of addition

    Returns
    -------
    result: Any
        Result of statsmodels seasonal_decompose
    cycle: pd.DataFrame
        Filtered cycle
    trend: pd.DataFrame
        Filtered Trend
    """
    seasonal_periods = 5
    # Hodrick-Prescott filter
    # See Ravn and Uhlig: http://home.uchicago.edu/~huhlig/papers/uhlig.ravn.res.2002.pdf
    lamb = 107360000000

    model = ["additive", "multiplicative"][multiplicative]

    result = seasonal_decompose(df, model=model, period=seasonal_periods)
    cycle, trend = sm.tsa.filters.hpfilter(
        result.trend[result.trend.notna().values], lamb=lamb
    )

    return result, pd.DataFrame(cycle), pd.DataFrame(trend)


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
    # Kurtosis
    # Measures height and sharpness of the central peak relative to that of a standard bell curve
    k, kpval = stats.kurtosistest(data)

    # Skewness
    # Measure of the asymmetry of the probability distribution of a random variable about its mean
    s, spval = stats.skewtest(data)

    # Jarque-Bera goodness of fit test on sample data
    # Tests if the sample data has the skewness and kurtosis matching a normal distribution
    jb, jbpval = stats.jarque_bera(data)

    # Shapiro
    # The Shapiro-Wilk test tests the null hypothesis that the data was drawn from a normal distribution.
    sh, shpval = stats.shapiro(data)

    # Kolmogorov-Smirnov
    # The one-sample test compares the underlying distribution F(x) of a sample against a given distribution G(x).
    # Comparing to normal here.
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
    # The Augmented Dickey-Fuller test
    # Used to test for a unit root in a univariate process in the presence of serial correlation.
    result = adfuller(df, regression=fuller_reg)
    cols = ["Test Statistic", "P-Value", "NLags", "Nobs", "ICBest"]
    vals = [result[0], result[1], result[2], result[3], result[5]]
    data = pd.DataFrame(data=vals, index=cols, columns=["ADF"])

    # Kwiatkowski-Phillips-Schmidt-Shin test
    # Test for level or trend stationarity
    # This test seems to produce an Interpolation Error which says
    # The test statistic is outside of the range of p-values available in the
    # look-up table. The actual p-value is greater than the p-value returned.
    # Wrap this in catch_warnings to prevent
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res2 = kpss(df, regression=kpss_reg, nlags="auto")
    vals2 = [res2[0], res2[1], res2[2], "", ""]
    data["KPSS"] = vals2
    return data
