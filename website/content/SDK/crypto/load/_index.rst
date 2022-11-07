.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.load(
    symbol: 'str',
    start_date: 'datetime' = datetime.datetime(
    2019, 11, 3, 18, 49, 59, 655008, chart: bool = False,
), interval: 'str' = '1440',
    exchange: 'str' = 'binance',
    vs_currency: 'str' = 'usdt',
    end_date: 'datetime' = datetime.datetime(
    2022, 11, 7, 18, 49, 59, 655009, chart: bool = False,
), source: 'str' = 'CCXT',
    chart: bool = False,
) -> 'pd.DataFrame'
{{< /highlight >}}

.. raw:: html

    <p>
    Load crypto currency to get data for
    </p>

* **Parameters**

    symbol: str
        Coin to get
    start_date: datetime
        The datetime to start at
    interval: str
        The interval between data points in minutes.
        Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200
    exchange: str:
        The exchange to get data from.
    vs_currency: str
        Quote Currency (Defaults to usdt)
    end_date: datetime
       The datetime to end at
    source: str
        The source of the data
        Choose from: CCXT, CoinGecko, YahooFinance

* **Returns**

    pd.DataFrame
        Dataframe consisting of price and volume data
