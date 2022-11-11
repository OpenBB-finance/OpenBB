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
crypto.onchain.tv(
    symbol: str = 'UNI',
    trade_amount_currency: str = 'USD',
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    symbol: str
        ERC20 token symbol.
    trade_amount_currency: str
        Currency to display trade amount in.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Token volume on Decentralized Exchanges

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.tv(
    symbol: str = 'WBTC',
    trade_amount_currency: str = 'USD',
    limit: int = 10,
    sortby: str = 'tradeAmount',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display token volume on different Decentralized Exchanges.
    [Source: https://graphql.bitquery.io/]
    </p>

* **Parameters**

    symbol: str
        ERC20 token symbol or address
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
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
