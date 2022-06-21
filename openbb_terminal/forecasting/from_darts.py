from typing import Tuple, Optional

import numpy as np
from statsmodels.tsa.stattools import acf
import matplotlib.pyplot as plt
from darts import TimeSeries
from darts.logging import raise_if


def plot_acf(
    ts: TimeSeries,
    m: Optional[int] = None,
    max_lag: int = 24,
    alpha: float = 0.05,
    bartlett_confint: bool = True,
    fig_size: Tuple[int, int] = (10, 5),
    axis: Optional[plt.axis] = None,
) -> None:
    """
    Plots the ACF of `ts`, highlighting it at lag `m`, with corresponding significance interval.
    Uses :func:`statsmodels.tsa.stattools.acf` [1]_

    Parameters
    ----------
    ts
        The TimeSeries whose ACF should be plotted.
    m
        Optionally, a time lag to highlight on the plot.
    max_lag
        The maximal lag order to consider.
    alpha
        The confidence interval to display.
    bartlett_confint
        The boolean value indicating whether the confidence interval should be
        calculated using Bartlett's formula. If set to True, the confidence interval
        can be used in the model identification stage for fitting ARIMA models.
        If set to False, the confidence interval can be used to test for randomness
        (i.e. there is no time dependence in the data) of the data.
    fig_size
        The size of the figure to be displayed.
    axis
        Optionally, an axis object to plot the ACF on.

    References
    ----------
    .. [1] https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.acf.html
    """

    ts._assert_univariate()
    raise_if(
        max_lag is None or not (1 <= max_lag < len(ts)),
        "max_lag must be greater than or equal to 1 and less than len(ts).",
    )
    raise_if(
        m is not None and not (0 <= m <= max_lag),
        "m must be greater than or equal to 0 and less than or equal to max_lag.",
    )
    raise_if(
        alpha is None or not (0 < alpha < 1),
        "alpha must be greater than 0 and less than 1.",
    )

    r, confint = acf(
        ts.values(),
        nlags=max_lag,
        fft=False,
        alpha=alpha,
        bartlett_confint=bartlett_confint,
    )

    if axis is None:
        plt.figure(figsize=fig_size)
        axis = plt

    for i in range(len(r)):
        axis.plot(
            (i, i),
            (0, r[i]),
            color=("#b512b8" if m is not None and i == m else "black"),
            lw=(1 if m is not None and i == m else 0.5),
        )

    # Adjusts the upper band of the confidence interval to center it on the x axis.
    upp_band = [confint[lag][1] - r[lag] for lag in range(1, max_lag + 1)]

    axis.fill_between(
        np.arange(1, max_lag + 1),
        upp_band,
        [-x for x in upp_band],
        color="#003DFD",
        alpha=0.25,
    )
    axis.plot((0, max_lag + 1), (0, 0), color="black")
