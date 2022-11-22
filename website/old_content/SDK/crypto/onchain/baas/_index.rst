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
crypto.onchain.baas(
    symbol: str = 'WETH',
    to_symbol: str = 'USDT',
    limit: int = 30,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get an average bid and ask prices, average spread for given crypto pair for chosen time period.
       [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    limit:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
       Average bid and ask prices, spread for given crypto pair for chosen time period

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.baas(
    symbol='ETH', to_symbol='USDC', days: int = 10,
    sortby: str = 'date',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display an average bid and ask prices, average spread for given crypto pair for chosen
    time period. [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    days:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Average bid and ask prices, spread for given crypto pair for chosen time period
