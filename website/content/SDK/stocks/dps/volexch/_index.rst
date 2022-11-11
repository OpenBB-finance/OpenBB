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
stocks.dps.volexch(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021
    </p>

* **Parameters**

    symbol : str
        Ticker to get data for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of short data by exchange

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.volexch(
    symbol: str,
    raw: bool = False,
    sortby: str = '',
    ascend: bool = False,
    mpl: bool = True,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display short data by exchange
    </p>

* **Parameters**

    symbol : str
        Stock ticker
    raw : bool
        Flag to display raw data
    sortby: str
        Column to sort by
    ascend: bool
        Sort in ascending order
    mpl: bool
        Display using matplotlib
    export : str, optional
        Format  of export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

