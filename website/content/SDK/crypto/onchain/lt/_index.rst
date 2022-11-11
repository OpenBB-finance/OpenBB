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
crypto.onchain.lt(
    trade_amount_currency: str = 'USD',
    limit: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Trades on Decentralized Exchanges aggregated by DEX

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.lt(
    trade_amount_currency: str = 'USD',
    kind: str = 'dex',
    limit: int = 20,
    days: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Trades on Decentralized Exchanges aggregated by DEX or Month
    [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    kind: str
        Aggregate trades by dex or time
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    days:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

