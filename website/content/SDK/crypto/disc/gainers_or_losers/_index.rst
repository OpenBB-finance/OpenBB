.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.disc.gainers_or_losers(
    limit: int = 20,
    interval: str = '1h',
    typ: str = 'gainers',
    sortby: str = 'market_cap',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns data about top gainers - coins which gain the most in given period and
    top losers - coins that lost the most in given period of time. [Source: CoinGecko]
    </p>

* **Parameters**

    limit: int
        Num of coins to get
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    interval: str
        One from {14d,1h,1y,200d,24h,30d,7d}
    typ: str
        Either "gainers" or "losers"

* **Returns**

    pandas.DataFrame
        Top Gainers / Top Losers - coins which gain/lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url
