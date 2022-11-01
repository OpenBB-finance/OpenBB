.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get finviz image for given ticker
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ta.view(
    symbol: str,
    chart: bool = False
) -> bytes
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol

    
* **Returns**

    bytes
        Image in byte format
    