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
    start\_date: 'datetime' = datetime.datetime(
    2019, 10, 26, 23, 20, 37, 254438, ), interval: 'str' = '1440',
    exchange: 'str' = 'binance',
    vs\_currency: 'str' = 'usdt',
    end\_date: 'datetime' = datetime.datetime(
    2022, 10, 30, 23, 20, 37, 254450, ), source: 'str' = 'CCXT',
    ) -> 'pd.DataFrame'
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Coin to get
    start\_date: *datetime*
        The datetime to start at
    interval: *str*
        The interval between data points in minutes.
        Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200
    exchange: str:
        The exchange to get data from.
    vs\_currency: *str*
        Quote Currency (Defaults to usdt)
    end\_date: *datetime*
       The datetime to end at
    source: *str*
        The source of the data
        Choose from: CCXT, CoinGecko, YahooFinance

    
* **Returns**

    pd.DataFrame
        Dataframe consisting of price and volume data
    