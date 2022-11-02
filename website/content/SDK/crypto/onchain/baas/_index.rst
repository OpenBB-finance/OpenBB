.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get an average bid and ask prices, average spread for given crypto pair for chosen time period.
       [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.baas(
    symbol: str = 'WETH',
    to_symbol: str = 'USDT',
    limit: int = 30,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: * int*
        Last n days to query data
    symbol: *str*
        ERC20 token symbol
    to_symbol: *str*
        Quoted currency.
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pd.DataFrame
       Average bid and ask prices, spread for given crypto pair for chosen time period
   