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
portfolio.po.maxdiv(
    symbols: List[str],
    interval: str = '3y',
    start_date: str = '',
    end_date: str = '',
    log_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    covariance: str = 'hist',
    d_ewma: float = 0.94,
    value: float = 1.0,
    value_short: float = 0,
    chart: bool = False,
    ) -> Tuple
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of portfolio stocks
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
    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': *use historical estimates.*
        - 'ewma1': use ewma with adjust=True. For more information see
        `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see
        `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ledoit': *use the Ledoit and Wolf Shrinkage method.*
        - 'oas': *use the Oracle Approximation Shrinkage method.*
        - 'shrunk': *use the basic Shrunk Covariance method.*
        - 'gl': *use the basic Graphical Lasso Covariance method.*
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`a-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`a-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`a-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`a-MLforAM`.

    d_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount of money to allocate. The default is 1.
    value_short : float, optional
        Amount to allocate to portfolio in short positions. The default is 0.

    
* **Returns**

    Tuple
        Dictionary of portfolio weights and DataFrame of stock returns
    