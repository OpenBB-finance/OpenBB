.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > All markets for given coin and currency [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.mkt(
    symbol: str = 'eth-ethereum', quotes: str = 'USD',
    sortby: str = 'pct_volume_share',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Coin Parpika identifier of coin e.g. eth-ethereum
    quotes: *str*
        Comma separated list of quotes to return.
        Example: quotes=USD,BTC
        Allowed values:
        BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN,
        PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR,
        VND, BOB, COP, PEN, ARS, ISK
    sortby: *str*
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pandas.DataFrame
        All markets for given coin and currency
    