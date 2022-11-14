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
stocks.dd.rot(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get rating over time data. [Source: Finnhub]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get ratings from
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Get dataframe with ratings

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dd.rot(
    symbol: str,
    limit: int = 10,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Rating over time (monthly). [Source: Finnhub]
    </p>

* **Parameters**

    ticker : str
        Ticker to get ratings from
    limit : int
        Number of last months ratings to show
    raw: bool
        Display raw data only
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

