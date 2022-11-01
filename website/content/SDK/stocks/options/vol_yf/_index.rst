.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Plot volume
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.options.vol_yf(
    symbol: str,
    expiry: str,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol
    expiry: *str*
        expiration date for options
    