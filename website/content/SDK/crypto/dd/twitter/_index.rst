.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.twitter(
    symbol: str = 'eth-ethereum',
    sortby: str = 'date',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    sortby: *str*
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: *bool*
        Flag to sort data descending
    
* **Returns**

    pandas.DataFrame
        Twitter timeline for given coin.
        Columns: date, user_name, status, retweet_count, like_count
    