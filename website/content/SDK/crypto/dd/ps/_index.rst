.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all most important ticker related information for given coin id [Source: CoinPaprika]

    .. code-block:: *json*

        {
            "id": "btc-bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "rank": 1,
            "circulating\_supply": 17007062,
            "total\_supply": 17007062,
            "max\_supply": 21000000,
            "beta\_value": 0.735327,
            "first\_data\_at": "2010-11-14T07:20:41Z",
            "last\_updated": "2018-11-14T07:20:41Z",
            "quotes": {
                "USD": {
                    "price": 5162.15941296,
                    "volume\_24h": 7304207651.1585,
                    "volume\_24h\_change\_24h": -2.5,
                    "market\_cap": 91094433242,
                    "market\_cap\_change\_24h": 1.6,
                    "percent\_change\_15m": 0,
                    "percent\_change\_30m": 0,
                    "percent\_change\_1h": 0,
                    "percent\_change\_6h": 0,
                    "percent\_change\_12h": -0.09,
                    "percent\_change\_24h": 1.59,
                    "percent\_change\_7d": 0.28,
                    "percent\_change\_30d": 27.39,
                    "percent\_change\_1y": -37.99,
                    "ath\_price": 20089,
                    "ath\_date": "2017-12-17T12:19:00Z",
                    "percent\_from\_price\_ath": -74.3
                }
            }
        }
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.ps(
    symbol: str = 'btc-bitcoin', quotes: str = 'USD',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Id of coin from CoinPaprika
    quotes: *str*
        Comma separated quotes to return e.g quotes = USD, BTC

    
* **Returns**

    pandas.DataFrame
        Most important ticker related information
        Columns: Metric, Value
    