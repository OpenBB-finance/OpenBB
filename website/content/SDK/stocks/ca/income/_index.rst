.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get income data. [Source: Marketwatch]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ca.income(
    similar: List[str],
    timeframe: str = '2021',
    quarter: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : *str*
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
   