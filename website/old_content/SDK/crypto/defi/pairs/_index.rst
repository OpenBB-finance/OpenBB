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
crypto.defi.pairs(
    last_days: int = 14,
    min_volume: int = 100,
    min_liquidity: int = 0,
    min_tx: int = 100,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get lastly added trade-able pairs on Uniswap with parameters like:
        * number of days the pair has been active,
        * minimum trading volume,
        * minimum liquidity,
        * number of transactions.

    [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    last_days: int
        How many days back to look for added pairs.
    min_volume: int
        Minimum volume
    min_liquidity: int
        Minimum liquidity
    min_tx: int
        Minimum number of transactions done in given pool.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Lastly added pairs on Uniswap DEX.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.pairs(
    limit: int = 20,
    days: int = 7,
    min_volume: int = 20,
    min_liquidity: int = 0,
    min_tx: int = 100,
    sortby: str = 'created',
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays Lastly added pairs on Uniswap DEX.
    [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    days: int
        Number of days the pair has been active,
    min_volume: int
        Minimum trading volume,
    min_liquidity: int
        Minimum liquidity
    min_tx: int
        Minimum number of transactions
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

