.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.candles(
    symbol: str,
    interval: str = '24h',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get candles for chosen trading pair and time interval. [Source: Coinbase]
    </p>

* **Parameters**

    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Candles for chosen trading pair.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.candles(
    symbol: str,
    interval: str = '24h',
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get candles for chosen trading pair and time interval. [Source: Coinbase]
    </p>

* **Parameters**

    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

