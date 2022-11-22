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
crypto.disc.cmctop(
    sortby: str = 'CMC_Rank',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Shows top n coins. [Source: CoinMarketCap]
    </p>

* **Parameters**

    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Whether to sort ascending or descending
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Top coin on CoinMarketCap

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.disc.cmctop(
    limit: int = 15,
    sortby: str = 'CMC_Rank',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows top n coins. [Source: CoinMarketCap]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

