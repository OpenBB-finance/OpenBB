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
stocks.ca.income(
    similar: List[str],
    timeframe: str = '2021',
    quarter: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get income data. [Source: Marketwatch]
    </p>

* **Parameters**

    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ca.income(
    symbols: List[str],
    timeframe: str = '2021',
    quarter: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display income data. [Source: Marketwatch]
    </p>

* **Parameters**

    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
        You can also get a list of comparable peers with
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        What year to look at
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
    chart: bool
       Flag to display chart

