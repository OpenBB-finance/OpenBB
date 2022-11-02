.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get current price for a given ticker
    </h3>

{{< highlight python >}}
stocks.options.price(
    symbol: str,
) -> float
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        The ticker symbol to get the price for

* **Returns**

    price : *float*
        The price of the ticker
