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
stocks.ba.headlines(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get the sentiment analysis from
    chart: bool
       Flag to display chart


* **Returns**

    DataFrame()
        Empty if there was an issue with data retrieval

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.headlines(
    symbol: str,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Sentiment analysis from FinBrain
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get the sentiment analysis from
    raw: False
        Display raw table data
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

