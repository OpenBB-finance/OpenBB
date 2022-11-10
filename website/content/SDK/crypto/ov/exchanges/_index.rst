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
crypto.ov.exchanges(
    sortby: str = 'Rank',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get list of top exchanges from CoinGecko API [Source: CoinGecko]
    </p>

* **Parameters**

    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC, Url

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.exchanges(
    sortby: str = 'Rank',
    ascend: bool = False,
    limit: int = 15,
    links: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows list of top exchanges from CoinGecko. [Source: CoinGecko]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

