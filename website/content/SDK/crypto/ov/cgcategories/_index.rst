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
crypto.ov.cgcategories(
    sort_filter: str = 'market_cap_desc',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns top crypto categories [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    </p>

* **Returns**

    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cgcategories(
    sortby: str = 'market_cap_desc',
    limit: int = 15,
    export: str = '',
    pie: bool = False,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows top cryptocurrency categories by market capitalization

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data
    limit: int
        Number of records to display
    export: str
        Export dataframe data to csv,json,xlsx file
    pie: bool
        Whether to show the pie chart
    chart: bool
       Flag to display chart

