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
crypto.ov.platforms(
    sortby: str = 'Name',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of financial platforms from CoinGecko API [Source: CoinGecko]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        Rank, Name, Category, Centralized, Url

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.platforms(
    sortby: str = 'Name',
    ascend: bool = True,
    limit: int = 15,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows list of financial platforms. [Source: CoinGecko]
    </p>

* **Parameters**

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

