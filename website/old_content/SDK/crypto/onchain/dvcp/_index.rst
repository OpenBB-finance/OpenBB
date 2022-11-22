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
crypto.onchain.dvcp(
    limit: int = 100,
    symbol: str = 'UNI',
    to_symbol: str = 'USDT',
    sortby: str = 'date',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get daily volume for given pair [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    limit:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quote currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
         Daily volume for given pair

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.dvcp(
    symbol: str = 'WBTC',
    to_symbol: str = 'USDT',
    limit: int = 20,
    sortby: str = 'date',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display daily volume for given pair
    [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    symbol: str
        ERC20 token symbol or address
    to_symbol: str
        Quote currency.
    limit: int
        Number of records to display
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
        Token volume on different decentralized exchanges
