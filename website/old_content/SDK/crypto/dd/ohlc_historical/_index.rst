.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.ohlc_historical(
    symbol: str = 'eth-ethereum',
    quotes: str = 'USD',
    days: int = 90,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Open/High/Low/Close values with volume and market_cap. [Source: CoinPaprika]
    Request example: https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start=2019-01-01&end=2019-01-20
    if the last day is current day it can an change with every request until actual close of the day at 23:59:59
    </p>

* **Parameters**

    symbol: str
        Paprika coin identifier e.g. eth-ethereum
    quotes: str
        returned data quote (available values: usd btc)
    days: int
        time range for chart in days. Maximum 365

* **Returns**

    pandas.DataFrame
        Open/High/Low/Close values with volume and market_cap.
