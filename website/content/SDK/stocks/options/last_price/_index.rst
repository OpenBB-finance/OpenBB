.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Makes api request for last price
    </h3>

{{< highlight python >}}
stocks.options.last_price(
    symbol: str
)
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol

    
* **Returns**

    float:
        Last price
    