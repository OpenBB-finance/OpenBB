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
crypto.dd.ex(
    symbol: str = 'eth-ethereum',
    sortby: str = 'adjusted_volume_24h_share',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get all exchanges for given coin id. [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Identifier of Coin from CoinPaprika
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        All exchanges for given coin
        Columns: id, name, adjusted_volume_24h_share, fiats

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.ex(
    symbol: str = 'btc',
    limit: int = 10,
    sortby: str = 'adjusted_volume_24h_share',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get all exchanges for given coin id. [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

