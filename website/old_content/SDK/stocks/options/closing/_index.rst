.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.closing(
    symbol: str,
    chart: bool = False,
) -> pandas.core.series.Series
{{< /highlight >}}

.. raw:: html

    <p>
    Get closing prices for a given ticker
    </p>

* **Parameters**

    symbol : str
        The ticker symbol to get the price for

* **Returns**

    price : List[float]
        A list of closing prices for a ticker
