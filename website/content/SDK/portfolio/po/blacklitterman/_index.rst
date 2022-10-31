.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Builds a maximal diversification portfolio
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.po.blacklitterman(
    symbols: List[str],
    benchmark: Dict,
    p\_views: List,
    q\_views: List,
    interval: str = '3y',
    start\_date: str = '',
    end\_date: str = '',
    log\_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    objective: str = 'Sharpe',
    risk\_free\_rate: float = 0,
    risk\_aversion: float = 1,
    delta: float = None,
    equilibrium: bool = True,
    optimize: bool = True,
    value: float = 1.0,
    value\_short: float = 0,
    chart: bool = False,
    ) -> Tuple
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of portfolio stocks
    benchmark : *Dict*
        Dict of portfolio weights
    p_views: *List*
        Matrix P of views that shows relationships among assets and returns.
        Default value to None.
    q_views: *List*
        Matrix Q of expected returns of views. Default value is None.
    interval : str, optional
        interval to get stock data, by default "3mo"
    start_date: *str*
        If not using interval, start date string (YYYY-MM-DD)
    end_date: *str*
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: *bool*
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: *str*
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:

        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: *float*
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: *float*
        Value used to replace outliers that are higher to threshold.
    method: *str*
        Method used to fill nan values. Default value is 'time'. For more information see
        `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`_.
    objective: *str*
        Objective function of the optimization model.
        The default is 'Sharpe'. Possible values are:

        - 'MinRisk': *Minimize the selected risk measure.*
        - 'Utility': *Maximize the risk averse utility function.*
        - 'Sharpe': *Maximize the risk adjusted return ratio based on the selected risk measure.*
        - 'MaxRet': *Maximize the expected return of the portfolio.*

    risk_free_rate: float, optional
        Risk free rate, must be in annual frequency. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    delta: float, optional
        Risk aversion factor of Black Litterman model. Default value is None.
    equilibrium: bool, optional
        If True excess returns are based on equilibrium market portfolio, if False
        excess returns are calculated as historical returns minus risk free rate.
        Default value is True.
    optimize: bool, optional
        If True Black Litterman estimates are used as inputs of mean variance model,
        if False returns equilibrium weights from Black Litterman model
        Default value is True.
    value : float, optional
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.

    
* **Returns**

    Tuple
        Dictionary of portfolio weights and DataFrame of stock returns
    