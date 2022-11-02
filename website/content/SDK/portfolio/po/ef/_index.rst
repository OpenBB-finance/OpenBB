.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get efficient frontier
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
portfolio.po.ef(
    symbols: List[str],
    interval: str = '3y',
    start_date: str = '',
    end_date: str = '',
    log_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    risk_measure: str = 'MV',
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    value: float = 1.0,
    value_short: float = 0.0,
    n_portfolios: int = 100,
    seed: int = 123,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of portfolio tickers
    interval : str, optional
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:

        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: *str*
        Method used to fill nan values. Default value is 'time'. For more information see
        `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`_.
    risk_measure: str, optional
        The risk measure used to optimize the portfolio.
        The default is 'MV'. Possible values are:

        - 'MV': *Standard Deviation.*
        - 'MAD': *Mean Absolute Deviation.*
        - 'MSV': *Semi Standard Deviation.*
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'CVaR': *Conditional Value at Risk.*
        - 'EVaR': *Entropic Value at Risk.*
        - 'WR': *Worst Realization.*
        - 'ADD': *Average Drawdown of uncompounded cumulative returns.*
        - 'UCI': *Ulcer Index of uncompounded cumulative returns.*
        - 'CDaR': *Conditional Drawdown at Risk of uncompounded cumulative returns.*
        - 'EDaR': *Entropic Drawdown at Risk of uncompounded cumulative returns.*
        - 'MDD': *Maximum Drawdown of uncompounded cumulative returns.*

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns. Used for
        'FLPM' and 'SLPM' and Sharpe objective function. The default is 0.
    alpha: float, optional
        Significance level of CVaR, EVaR, CDaR and EDaR
        The default is 0.05.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    n_portfolios: int, optional
        "Number of portfolios to simulate. The default value is 100.
    seed: int, optional
        Seed used to generate random portfolios. The default value is 123.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Tuple
        Parameters to create efficient frontier: frontier, mu, cov, stock_returns, weights, X1, Y1, port
