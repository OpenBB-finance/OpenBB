"""Quantitative Analysis Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import Any, Tuple, Union, List
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import MissingDataError
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from scipy import stats
import numpy as np

from openbb_terminal.decorators import log_start_end

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
    try:
        result = adfuller(df, regression=fuller_reg)
    except MissingDataError:
        df = df.dropna(axis=0)
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


def calculate_adjusted_var(
    kurtosis: float, skew: float, ndp: float, std: float, mean: float
):
    """Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)

    Parameters
    ----------
    kurtosis: float
        kurtosis of data
    skew: float
        skew of data
    ndp: float
        normal distribution percentage number (99% -> -2.326)
    std: float
        standard deviation of data
    mean: float
        mean of data

    Returns
    -------
    float
        Real adjusted VaR
    """

    # Derived from Cornish-Fisher-Expansion
    # Formula for quantile from "Finance Compact Plus" by Zimmerman; Part 1, page 130-131
    # More material/resources:
    #     - "Numerical Methods and Optimization in Finance" by Gilli, Maringer & Schumann;
    #     - https://www.value-at-risk.net/the-cornish-fisher-expansion/;
    #     - https://www.diva-portal.org/smash/get/diva2:442078/FULLTEXT01.pdf, Section 2.4.2, p.18;
    #     - "Risk Management and Financial Institutions" by John C. Hull

    skew_component = skew / 6 * (ndp**2 - 1) ** 2 - skew**2 / 36 * ndp * (
        2 * ndp**2 - 5
    )
    kurtosis_component = (kurtosis - 3) / 24 * ndp * (ndp**2 - 3)
    quantile = ndp + skew_component + kurtosis_component
    log_return = mean + quantile * std
    real_return = 2.7182818**log_return - 1
    return real_return


def get_var(
    data: pd.DataFrame,
    use_mean: bool,
    adjusted_var: bool,
    student_t: bool,
    percentile: Union[int, float],
    portfolio: bool,
):
    """Gets value at risk for specified stock dataframe

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of a stock/portfolio
    use_mean: bool
        If one should use the stocks mean for calculation
    adjusted_var: bool
        If one should return VaR adjusted for skew and kurtosis
    student_t: bool
        If one should use the student-t distribution
    percentile: Union[int,float]
        VaR percentile
    portfolio: bool
        If the data is a portfolio

    Returns
    -------
    list
        list of VaR
    list
        list of historical VaR
    """
    if not portfolio:
        data = data[["adjclose"]].copy()
        data.loc[:, "return"] = data.adjclose.pct_change()
        data_return = data["return"]
    else:
        data = data[1:].copy()
        data_return = data

    # Distribution percentages
    percentile_90 = -1.282
    percentile_95 = -1.645
    percentile_99 = -2.326
    percentile_custom = stats.norm.ppf(1 - percentile)

    # Mean
    if use_mean:
        mean = data_return.mean()
    else:
        mean = 0

    # Standard Deviation
    std = data_return.std(axis=0)

    if adjusted_var:

        # Kurtosis
        # Measures height and sharpness of the central peak relative to that of a standard bell curve
        k = data_return.kurtosis(axis=0)

        # Skewness
        # Measure of the asymmetry of the probability distribution of a random variable about its mean
        s = data_return.skew(axis=0)

        # Adjusted VaR
        var_90 = calculate_adjusted_var(k, s, percentile_90, std, mean)
        var_95 = calculate_adjusted_var(k, s, percentile_95, std, mean)
        var_99 = calculate_adjusted_var(k, s, percentile_99, std, mean)
        var_custom = calculate_adjusted_var(k, s, percentile_custom, std, mean)

    elif student_t:
        # Calculating VaR based on the Student-t distribution

        # Fitting student-t parameters to the data
        v, _, _ = stats.t.fit(data_return.fillna(0))
        if not use_mean:
            mean = 0
        var_90 = np.sqrt((v - 2) / v) * stats.t.ppf(0.1, v) * std + mean
        var_95 = np.sqrt((v - 2) / v) * stats.t.ppf(0.05, v) * std + mean
        var_99 = np.sqrt((v - 2) / v) * stats.t.ppf(0.01, v) * std + mean
        var_custom = np.sqrt((v - 2) / v) * stats.t.ppf(1 - percentile, v) * std + mean

    else:
        # Regular Var
        var_90 = np.exp(mean + percentile_90 * std) - 1
        var_95 = np.exp(mean + percentile_95 * std) - 1
        var_99 = np.exp(mean + percentile_99 * std) - 1
        var_custom = np.exp(mean + percentile_custom * std) - 1

    if not portfolio:
        data.sort_values("return", inplace=True, ascending=True)
        data_return = data["return"]
    else:
        data.sort_values(inplace=True, ascending=True)
        data_return = data

    # Historical VaR
    hist_var_90 = data_return.quantile(0.1)
    hist_var_95 = data_return.quantile(0.05)
    hist_var_99 = data_return.quantile(0.01)
    hist_var_custom = data_return.quantile(1 - percentile)

    var_list = [var_90, var_95, var_99, var_custom]
    hist_var_list = [hist_var_90, hist_var_95, hist_var_99, hist_var_custom]
    return var_list, hist_var_list


def get_es(
    data: pd.DataFrame,
    use_mean: bool,
    distribution: str,
    percentile: Union[float, int],
    portfolio: bool,
) -> Tuple[List[float], List[float]]:
    """Gets Expected Shortfall for specified stock dataframe

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of a stock
    use_mean: bool
        If one should use the stocks mean for calculation
    distribution: str
        Type of distribution, options: laplace, student_t, normal
    percentile: Union[float,int]
        VaR percentile
    portfolio: bool
        If the data is a portfolio

    Returns
    -------
    list
        list of ES
    list
        list of historical ES
    """
    if not portfolio:
        data = data[["adjclose"]].copy()
        data.loc[:, "return"] = data.adjclose.pct_change()
        data_return = data["return"]
    else:
        data = data[1:].copy()
        data_return = data

    # Distribution percentages
    percentile_90 = -1.282
    percentile_95 = -1.645
    percentile_99 = -2.326
    percentile_custom = stats.norm.ppf(1 - percentile)

    # Mean
    if use_mean:
        mean = data_return.mean()
    else:
        mean = 0

    # Standard Deviation
    std = data_return.std(axis=0)

    if distribution == "laplace":
        # Calculating ES based on Laplace distribution
        # For formula see: https://en.wikipedia.org/wiki/Expected_shortfall#Laplace_distribution

        # Fitting b (scale parameter) to the variance of the data
        # Since variance of the Laplace dist.: var = 2*b**2
        # Thus:
        b = np.sqrt(std**2 / 2)

        # Calculation
        es_90 = -b * (1 - np.log(2 * 0.1)) + mean
        es_95 = -b * (1 - np.log(2 * 0.05)) + mean
        es_99 = -b * (1 - np.log(2 * 0.01)) + mean

        if (1 - percentile) < 0.5:
            es_custom = -b * (1 - np.log(2 * (1 - percentile))) + mean
        else:
            es_custom = 0

    elif distribution == "student_t":
        # Calculating ES based on the Student-t distribution

        # Fitting student-t parameters to the data
        v, _, scale = stats.t.fit(data_return.fillna(0))
        if not use_mean:
            mean = 0

        # Student T Distribution percentages
        percentile_90 = stats.t.ppf(0.1, v)
        percentile_95 = stats.t.ppf(0.05, v)
        percentile_99 = stats.t.ppf(0.01, v)
        percentile_custom = stats.t.ppf(1 - percentile, v)

        # Calculation
        es_90 = (
            -scale
            * (v + percentile_90**2)
            / (v - 1)
            * stats.t.pdf(percentile_90, v)
            / 0.1
            + mean
        )
        es_95 = (
            -scale
            * (v + percentile_95**2)
            / (v - 1)
            * stats.t.pdf(percentile_95, v)
            / 0.05
            + mean
        )
        es_99 = (
            -scale
            * (v + percentile_99**2)
            / (v - 1)
            * stats.t.pdf(percentile_99, v)
            / 0.01
            + mean
        )
        es_custom = (
            -scale
            * (v + percentile_custom**2)
            / (v - 1)
            * stats.t.pdf(percentile_custom, v)
            / (1 - percentile)
            + mean
        )

    elif distribution == "logistic":
        # Logistic distribution
        # For formula see: https://en.wikipedia.org/wiki/Expected_shortfall#Logistic_distribution

        # Fitting s (scale parameter) to the variance of the data
        # Since variance of the Logistic dist.: var = s**2*pi**2/3
        # Thus:
        s = np.sqrt(3 * std**2 / np.pi**2)

        # Calculation
        a = 1 - percentile
        es_90 = -s * np.log((0.9 ** (1 - 1 / 0.1)) / 0.1) + mean
        es_95 = -s * np.log((0.95 ** (1 - 1 / 0.05)) / 0.05) + mean
        es_99 = -s * np.log((0.99 ** (1 - 1 / 0.01)) / 0.01) + mean
        es_custom = -s * np.log((percentile ** (1 - 1 / a)) / a) + mean

    else:
        # Regular Expected Shortfall
        es_90 = std * -stats.norm.pdf(percentile_90) / 0.1 + mean
        es_95 = std * -stats.norm.pdf(percentile_95) / 0.05 + mean
        es_99 = std * -stats.norm.pdf(percentile_99) / 0.01 + mean
        es_custom = std * -stats.norm.pdf(percentile_custom) / (1 - percentile) + mean

    # Historical Expected Shortfall
    _, hist_var_list = get_var(data, use_mean, False, False, percentile, portfolio)
    hist_es_90 = data_return[data_return <= hist_var_list[0]].mean()
    hist_es_95 = data_return[data_return <= hist_var_list[1]].mean()
    hist_es_99 = data_return[data_return <= hist_var_list[2]].mean()
    hist_es_custom = data_return[data_return <= hist_var_list[3]].mean()

    es_list = [es_90, es_95, es_99, es_custom]
    hist_es_list = [hist_es_90, hist_es_95, hist_es_99, hist_es_custom]
    return es_list, hist_es_list
