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
crypto.dd.mkt(
    symbol: str = 'eth-ethereum',
    quotes: str = 'USD',
    sortby: str = 'pct_volume_share',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    All markets for given coin and currency [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Coin Parpika identifier of coin e.g. eth-ethereum
    quotes: str
        Comma separated list of quotes to return.
        Example: quotes=USD,BTC
        Allowed values:
        BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN,
        PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR,
        VND, BOB, COP, PEN, ARS, ISK
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        All markets for given coin and currency

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.mkt(
    from_symbol: str = 'BTC',
    to_symbol: str = 'USD',
    limit: int = 20,
    sortby: str = 'pct_volume_share',
    ascend: bool = True,
    links: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get all markets for given coin id. [Source: CoinPaprika]
    </p>

* **Parameters**

    from_symbol: str
        Cryptocurrency symbol (e.g. BTC)
    to_symbol: str
        Quoted currency
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

