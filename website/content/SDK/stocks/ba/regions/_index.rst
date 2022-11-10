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
stocks.ba.regions(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get interest by region from google api [Source: google]
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to look at
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of interest by region

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.regions(
    symbol: str,
    limit: int = 5,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot bars of regions based on stock's interest. [Source: Google]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

