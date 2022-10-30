.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Estimates long-run and short-run cointegration relationship for series y and x and apply
    the two-step Engle & Granger test for cointegration.

    Uses a 2-step process to first estimate coefficients for the long-run relationship
        y\_t = c + gamma * x\_t + z\_t

    and then the short-term relationship,
        y\_t - y\_(t-1) = alpha * z\_(t-1) + epsilon\_t,

    with z the found residuals of the first equation.

    Then tests cointegration by Dickey-Fuller phi=1 vs phi < 1 in
        z\_t = phi * z\_(t-1) + eta\_t

    If this implies phi < 1, the z series is stationary is concluded to be
    stationary, and thus the series y and x are concluded to be cointegrated.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.coint(
    dependent\_series, independent\_series, chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    dependent\_series : *pd.Series*
        The first time series of the pair to analyse.

    independent\_series : *pd.Series*
        The second time series of the pair to analyse.

    
* **Returns**

    c : *float*
        The constant term in the long-run relationship y\_t = c + gamma * x\_t + z\_t. This
        describes the static shift of y with respect to gamma * x.

    gamma : *float*
        The gamma term in the long-run relationship y\_t = c + gamma * x\_t + z\_t. This
        describes the ratio between the const-shifted y and x.

    alpha : *float*
        The alpha term in the short-run relationship y\_t - y\_(t-1) = alpha * z\_(t-1) + epsilon. This
        gives an indication of the strength of the error correction toward the long-run mean.

    z : *pd.Series*
        Series of residuals z\_t from the long-run relationship y\_t = c + gamma * x\_t + z\_t, representing
        the value of the error correction term.

    dfstat : *float*
        The Dickey Fuller test-statistic for phi = 1 vs phi < 1 in the second equation. A more
        negative value implies the existence of stronger cointegration.

    pvalue : *float*
        The p-value corresponding to the Dickey Fuller test-statistic. A lower value implies
        stronger rejection of no-cointegration, thus stronger evidence of cointegration.

    