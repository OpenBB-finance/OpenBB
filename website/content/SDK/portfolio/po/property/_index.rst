.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate portfolio weights based on selected property
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
portfolio.po.property(
    symbols: List[str],
    interval: str = '3y',
    start_date: str = '',
    end_date: str = '',
    log_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    s_property: str = 'marketCap',
    value: float = 1.0,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
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

    maxnan: *float*
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: *float*
        Value used to replace outliers that are higher to threshold.
    method: *str*
        Method used to fill nan values. Default value is 'time'. For more information see
        `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`_.
    s_property : *str*
        Property to weight portfolio by
    value : float, optional
        Amount of money to allocate
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Dict
        Dictionary of portfolio weights or allocations
