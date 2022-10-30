.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get correlation sentiments across similar companies. [Source: FinBrain]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ca.scorr(
    similar: List[str],
    chart: bool = False,
    )
{{< /highlight >}}

* **Parameters**

    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    