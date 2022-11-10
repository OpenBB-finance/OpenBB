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
stocks.ba.mentions(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get interest over time from google api [Source: google]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of interest over time

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.mentions(
    symbol: str,
    start_date: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol
    start_date : str
        Start date as YYYY-MM-DD string
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

