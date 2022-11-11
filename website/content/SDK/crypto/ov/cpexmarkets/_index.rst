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
crypto.ov.cpexmarkets(
    exchange_id: str = 'binance',
    symbols: str = 'USD',
    sortby: str = 'pair',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    List markets by exchange ID [Source: CoinPaprika]
    </p>

* **Parameters**

    exchange_id: str
        identifier of exchange e.g for Binance Exchange -> binance
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cpexmarkets(
    exchange: str = 'binance',
    sortby: str = 'pair',
    ascend: bool = True,
    limit: int = 15,
    links: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get all markets for given exchange [Source: CoinPaprika]
    </p>

* **Parameters**

    exchange: str
        Exchange identifier e.g Binance
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

