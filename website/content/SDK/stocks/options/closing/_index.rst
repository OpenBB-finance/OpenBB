.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get closing prices for a given ticker
    </h3>

{{< highlight python >}}
stocks.options.closing(
    symbol: str,
) -> pandas.core.series.Series
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        The ticker symbol to get the price for

    
* **Returns**

    price : List[float]
        A list of closing prices for a ticker
   