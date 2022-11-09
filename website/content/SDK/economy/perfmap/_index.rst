.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
economy.perfmap(
    period: str = '1d',
    map_filter: str = 'sp500',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Opens Finviz map website in a browser. [Source: Finviz]
    </p>

* **Parameters**

    period : str
        Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y.
    scope : str
        Map filter. Available map filters are sp500, world, full, etf.
