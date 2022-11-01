.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get most traded crypto pairs on given decentralized exchange in chosen time period.
    [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.ttcp(
    network: str = 'ethereum',
    exchange: str = 'Uniswap',
    limit: int = 90,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    network: *str*
        EVM network. One from list: bsc (binance smart chain), ethereum or matic
    exchange:
        Decentralized exchange name
    limit:
        Number of days taken into calculation account.
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**


    