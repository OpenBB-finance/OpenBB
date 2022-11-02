.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Plot volume and open interest
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.voi_yf(
    symbol: str,
    expiry: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Stock ticker symbol
    expiry: *str*
        Option expiration
   