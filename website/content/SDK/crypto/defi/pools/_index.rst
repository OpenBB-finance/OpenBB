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
crypto.defi.pools() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get uniswap pools by volume. [Source: https://thegraph.com/en/]
    </p>

* **Returns**

    pd.DataFrame
        Trade-able pairs listed on Uniswap by top volume.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.pools(
    limit: int = 20,
    sortby: str = 'volumeUSD',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays uniswap pools by volume.
    [Source: https://thegraph.com/en/]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://bit.ly/3ORagr1 then press ctrl-enter or execute the query).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

