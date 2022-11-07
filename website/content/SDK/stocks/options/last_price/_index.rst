.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.last_price(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Makes api request for last price
    </p>

* **Parameters**

    symbol: str
        Ticker symbol

* **Returns**

    float:
        Last price
