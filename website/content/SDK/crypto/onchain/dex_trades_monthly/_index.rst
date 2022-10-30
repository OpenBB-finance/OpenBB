.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of trades on Decentralized Exchanges monthly aggregated.
    [Source: https://graphql.bitquery.io/]
    </h3>

{{< highlight python >}}
crypto.onchain.dex_trades_monthly(
    trade\_amount\_currency: str = 'USD',
    limit: int = 90,
    ascend: bool = True,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    trade\_amount\_currency: *str*
        Currency of displayed trade amount. Default: *USD*
    limit: * int*
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pd.DataFrame
        Trades on Decentralized Exchanges monthly aggregated
    