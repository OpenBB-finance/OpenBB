.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.onchain.dex_trades_monthly(
    trade_amount_currency: str = 'USD',
    limit: int = 90,
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of trades on Decentralized Exchanges monthly aggregated.
    [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    ascend: bool
        Flag to sort data ascending

* **Returns**

    pd.DataFrame
        Trades on Decentralized Exchanges monthly aggregated
