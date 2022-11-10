.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
econometrics.coint(
    dependent_series, independent_series, chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Estimates long-run and short-run cointegration relationship for series y and x and apply
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
    </p>

* **Parameters**

    dependent_series : pd.Series
        The first time series of the pair to analyse.

    independent_series : pd.Series
        The second time series of the pair to analyse.
    chart: bool
       Flag to display chart


* **Returns**

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

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.coint(
    datasets: Union[pandas.core.frame.DataFrame, Dict[str, pandas.core.series.Series]],
    significant: bool = False,
    plot: bool = False,
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Estimates long-run and short-run cointegration relationship for series y and x and apply
    the two-step Engle & Granger test for cointegration.

    Uses a 2-step process to first estimate coefficients for the long-run relationship
        y_t = c + gamma * x_t + z_t

    and then the short-term relationship,
        y_t - y_(t-1) = alpha * z_(t-1) + epsilon_t,

    with z the found residuals of the first equation.

    Then tests co-integration with the Dickey-Fuller phi=1 vs phi < 1 in
        z_t = phi * z_(t-1) + eta_t

    If this implies phi < 1, the z series is stationary is concluded to be
    stationary, and thus the series y and x are concluded to be cointegrated.
    </p>

* **Parameters**

    datasets: Union[pd.DataFrame, Dict[str, pd.Series]]
        All time series to perform co-integration tests on.
    significant: float
        Show only companies that have p-values lower than this percentage
    plot: bool
        Whether you wish to plot the z-values of all pairs.
    export : str
        Format to export data
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: bool
       Flag to display chart

