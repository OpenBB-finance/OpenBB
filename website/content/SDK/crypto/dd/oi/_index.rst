.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns open interest by exchange for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.oi(
    symbol: str,
    interval: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto Symbol to search open interest futures (e.g., BTC)
    interval : *int*
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0

    
* **Returns**

    pd.DataFrame
        open interest by exchange and price
    