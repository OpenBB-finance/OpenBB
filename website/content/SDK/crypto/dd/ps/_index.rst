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
            "circulating_supply": 17007062,
            "total_supply": 17007062,
            "max_supply": 21000000,
            "beta_value": 0.735327,
            "first_data_at": "2010-11-14T07:20:41Z",
            "last_updated": "2018-11-14T07:20:41Z",
            "quotes": {
                "USD": {
                    "price": 5162.15941296,
                    "volume_24h": 7304207651.1585,
                    "volume_24h_change_24h": -2.5,
                    "market_cap": 91094433242,
                    "market_cap_change_24h": 1.6,
                    "percent_change_15m": 0,
                    "percent_change_30m": 0,
                    "percent_change_1h": 0,
                    "percent_change_6h": 0,
                    "percent_change_12h": -0.09,
                    "percent_change_24h": 1.59,
                    "percent_change_7d": 0.28,
                    "percent_change_30d": 27.39,
                    "percent_change_1y": -37.99,
                    "ath_price": 20089,
                    "ath_date": "2017-12-17T12:19:00Z",
                    "percent_from_price_ath": -74.3
                }
            }
        }
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.ps(
    symbol: str = 'btc-bitcoin',
    quotes: str = 'USD',
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
   