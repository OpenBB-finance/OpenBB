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
crypto.ov.cpmarkets(
    symbols: str = 'USD',
    sortby: str = 'rank',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]
    </p>

* **Parameters**

    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        rank, name, symbol, price, volume_24h, mcap_change_24h,
        pct_change_1h, pct_change_24h, ath_price, pct_from_ath,

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cpmarkets(
    symbol: str,
    sortby: str = 'rank',
    ascend: bool = True,
    limit: int = 15,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Quoted currency
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

