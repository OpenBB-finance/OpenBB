.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.tv(
    symbol: str = 'UNI',
    trade_amount_currency: str = 'USD',
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        ERC20 token symbol.
    trade_amount_currency: *str*
        Currency to display trade amount in.
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pd.DataFrame
        Token volume on Decentralized Exchanges
    