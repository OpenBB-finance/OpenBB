.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.price(
    symbol: str,
    chart: bool = False,
) -> float
{{< /highlight >}}

.. raw:: html

    <p>
    Get current price for a given ticker
    </p>

* **Parameters**

    symbol : str
        The ticker symbol to get the price for

* **Returns**

    price : float
        The price of the ticker
