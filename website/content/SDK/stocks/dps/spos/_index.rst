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
stocks.dps.spos(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get net short position. [Source: Stockgrid]
    </p>

* **Parameters**

    symbol: str
        Stock to get data from
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Net short position

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.spos(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot net short position. [Source: Stockgrid]
    </p>

* **Parameters**

    symbol: str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

