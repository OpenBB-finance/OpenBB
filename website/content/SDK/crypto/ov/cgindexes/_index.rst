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
crypto.ov.cgindexes(
    sortby: str = 'Name',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    </p>

* **Returns**

    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cgindexes(
    sortby: str = 'Name',
    ascend: bool = True,
    limit: int = 15,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows list of crypto indexes. [Source: CoinGecko]
    </p>

* **Parameters**

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

