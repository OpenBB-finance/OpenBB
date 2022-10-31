.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all exchanges for given coin id. [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.ex(
    symbol: str = 'eth-ethereum', sortby: str = 'adjusted\_volume\_24h\_share', ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Identifier of Coin from CoinPaprika
    sortby: *str*
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pandas.DataFrame
        All exchanges for given coin
        Columns: id, name, adjusted_volume_24h_share, fiats
    