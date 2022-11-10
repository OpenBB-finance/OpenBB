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
crypto.defi.tokens(
    skip: int = 0,
    limit: int = 100,
    sortby: str = 'index',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    skip: int
        Skip n number of records.
    limit: int
        Show n number of records.
    sortby: str
        The column to sort by
    ascend: bool
        Whether to sort in ascending order
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Uniswap tokens with trading volume, transaction count, liquidity.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.tokens(
    skip: int = 0,
    limit: int = 20,
    sortby: str = 'index',
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays tokens trade-able on Uniswap DEX.
    [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    skip: int
        Number of records to skip
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

