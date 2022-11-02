.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load crypto currency to get data for.
    </h3>

{{< highlight python >}}
crypto.load(
    symbol: 'str',
    start_date: 'datetime' = datetime.datetime(
    2019, 10, 29, 13, 16, 1, 969236,
), interval: 'str' = '1440',
    exchange: 'str' = 'binance',
    vs_currency: 'str' = 'usdt',
    end_date: 'datetime' = datetime.datetime(
    2022, 11, 2, 13, 16, 1, 969245,
), source: 'str' = 'CCXT',
) -> 'pd.DataFrame'
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Coin to get
    start_date: *datetime*
        The datetime to start at
    interval: *str*
        The interval between data points in minutes.
        Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200
    exchange: str:
        The exchange to get data from.
    vs_currency: *str*
        Quote Currency (Defaults to usdt)
    end_date: *datetime*
       The datetime to end at
    source: *str*
        The source of the data
        Choose from: CCXT, CoinGecko, YahooFinance

    
* **Returns**

    pd.DataFrame
        Dataframe consisting of price and volume data
   