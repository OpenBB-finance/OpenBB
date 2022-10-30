.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > List exchanges from CoinPaprika API [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpexchanges(
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
        Flag to sort data ascend

    
* **Returns**

    pandas.DataFrame
        rank, name, currencies, markets, fiats, confidence\_score, reported\_volume\_24h,
        reported\_volume\_7d ,reported\_volume\_30d, sessions\_per\_month,
    