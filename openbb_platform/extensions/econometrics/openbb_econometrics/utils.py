"""Utility functions for the econometrics extension of the OpenBB platform."""

import warnings
from typing import Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller


def get_engle_granger_two_step_cointegration_test(
    dependent_series: pd.Series, independent_series: pd.Series
) -> Tuple[float, float, float, pd.Series, float, float]:
    """Estimate long-run and short-run cointegration relationship for series y and x.

    Then apply the two-step Engle & Granger test for cointegration.

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


def mock_multi_index_data():
    """Create a mock multi-index dataframe for testing purposes."""
    arrays = [
        ["individual_" + str(i) for i in range(1, 11) for _ in range(5)],
        list(range(1, 6)) * 10,
    ]
    index = pd.MultiIndex.from_arrays(arrays, names=("individual", "time"))

    df = pd.DataFrame(
        {
            "income": np.random.randint(20000, 80000, size=50),
            "age": np.random.randint(25, 60, size=50),
            "education": np.random.randint(12, 21, size=50),
        },
        index=index,
    )

    return df
