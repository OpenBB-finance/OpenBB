.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpinfo(
    symbols: str = 'USD',
    sortby: str = 'rank',
    ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbols: *str*
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending

    
* **Returns**

    pandas.DataFrame
        rank, name, symbol, price, volume\_24h, circulating\_supply, total\_supply,
        max\_supply, market\_cap, beta\_value, ath\_price,
    