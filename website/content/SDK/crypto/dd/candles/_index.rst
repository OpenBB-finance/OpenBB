.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get candles for chosen trading pair and time interval. [Source: Coinbase]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.candles(
    symbol: str,
    interval: str = '24h',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: *str*
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour

    
* **Returns**

    pd.DataFrame
        Candles for chosen trading pair.
    