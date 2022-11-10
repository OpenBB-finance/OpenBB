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
crypto.dd.twitter(
    symbol: str = 'eth-ethereum',
    sortby: str = 'date',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: bool
        Flag to sort data descending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        Twitter timeline for given coin.
        Columns: date, user_name, status, retweet_count, like_count

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.twitter(
    symbol: str = 'BTC',
    limit: int = 10,
    sortby: str = 'date',
    ascend: bool = True,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

