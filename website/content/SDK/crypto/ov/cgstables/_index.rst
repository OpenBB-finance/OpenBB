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
crypto.ov.cgstables(
    limit: int = 20,
    sortby: str = 'rank',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns top stable coins [Source: CoinGecko]
    </p>

* **Parameters**

    limit: int
        How many rows to show
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d, Url

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cgstables(
    limit: int = 15,
    export: str = '',
    sortby: str = 'rank',
    ascend: bool = False,
    pie: bool = False,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows stablecoins data [Source: CoinGecko]
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
    pie : bool
        Whether to show a pie chart
    chart: bool
       Flag to display chart

