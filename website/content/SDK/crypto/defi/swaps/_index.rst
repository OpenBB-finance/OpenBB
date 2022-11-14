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
crypto.defi.swaps(
    limit: int = 100,
    sortby: str = 'timestamp',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    limit: int
        Number of swaps to return. Maximum possible number: 1000.
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: bool
        Flag to sort data descending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Last 100 swaps on Uniswap

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.swaps(
    limit: int = 10,
    sortby: str = 'timestamp',
    ascend: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays last swaps done on Uniswap
    [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

