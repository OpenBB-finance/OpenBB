.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info for a given ticker
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.info(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        The ticker symbol to get the price for

    
* **Returns**

    price : *float*
        The info for a given ticker
    