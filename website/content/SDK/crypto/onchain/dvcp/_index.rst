.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get daily volume for given pair [Source: https://graphql.bitquery.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.dvcp(
    limit: int = 100,
    symbol: str = 'UNI',
    to_symbol: str = 'USDT',
    sortby: str = 'date',
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
        Quote currency.
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pd.DataFrame
         Daily volume for given pair
   