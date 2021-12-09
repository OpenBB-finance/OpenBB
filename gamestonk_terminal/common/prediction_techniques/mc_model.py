"""Monte Carlo Model"""
__docformat__ = "numpy"

from typing import Union
import pandas as pd
import numpy as np
from scipy.stats import norm


def get_mc_brownian(
    data: Union[pd.Series, np.ndarray], n_future: int, n_sims: int, use_log=True
) -> np.ndarray:
    """Performs monte carlo forecasting for brownian motion with drift

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    n_future : int
        Number of future steps
    n_sims : int
        Number of simulations to run
    use_log : bool, optional
        Flag to use log returns, by default True

    Returns
    -------
    np.ndarray
        Array of predictions.  Has shape (n_future, n_sims)
    """

    changes = data.pct_change().dropna()  # type: ignore

    if use_log:
        changes = np.log(1 + changes)

    dist_mean = changes.mean()
    dist_var = changes.var()
    dist_drift = dist_mean - 0.5 * dist_var
    dist_std = np.sqrt(dist_var)

    random_steps = norm.ppf(np.random.rand(n_future, n_sims))
    predicted_change = np.exp(dist_drift + dist_std * random_steps)
    possible_paths = np.zeros_like(predicted_change)
    possible_paths[0] = data.values[-1]  # type: ignore

    for t in range(1, n_future):
        possible_paths[t] = possible_paths[t - 1] * predicted_change[t]

    return possible_paths
