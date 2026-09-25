"""Utility functions for the econometrics extension of the OpenBB platform."""

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import Series


def get_engle_granger_two_step_cointegration_test(
    dependent_series: "Series", independent_series: "Series"
) -> tuple[float, float, float, "Series", float, float]:
    """Run the Engle-Granger two-step cointegration test on a series pair."""
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import adfuller

    warnings.simplefilter(action="ignore", category=FutureWarning)
    long_run_ols = sm.OLS(dependent_series, sm.add_constant(independent_series))
    warnings.simplefilter(action="default", category=FutureWarning)

    long_run_ols_fit = long_run_ols.fit()

    c, gamma = long_run_ols_fit.params
    z = long_run_ols_fit.resid

    short_run_ols = sm.OLS(dependent_series.diff().iloc[1:], (z.shift().iloc[1:]))
    short_run_ols_fit = short_run_ols.fit()

    alpha = short_run_ols_fit.params.iloc[0]

    # adfuller's p-value assumes z is not pre-estimated; limited effect for high N.
    adfstat, pvalue, _, _, _ = adfuller(z, maxlag=1, autolag=None)

    return c, gamma, alpha, z, adfstat, pvalue


def mock_multi_index_data():
    """Create a mock multi-index dataframe for testing purposes."""
    from numpy import random
    from pandas import DataFrame, MultiIndex

    arrays = [
        ["individual_" + str(i) for i in range(1, 11) for _ in range(5)],
        list(range(1, 6)) * 10,
    ]
    index = MultiIndex.from_arrays(arrays, names=("individual", "time"))

    df = DataFrame(
        {
            "income": random.randint(20000, 80000, size=50),
            "age": random.randint(25, 60, size=50),
            "education": random.randint(12, 21, size=50),
        },
        index=index,
    )

    return df
