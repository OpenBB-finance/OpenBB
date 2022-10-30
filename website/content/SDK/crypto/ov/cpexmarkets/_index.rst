.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > List markets by exchange ID [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpexmarkets(
    exchange\_id: str = 'binance',
    symbols: str = 'USD',
    sortby: str = 'pair',
    ascend: bool = True,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    exchange\_id: *str*
        identifier of exchange e.g for Binance Exchange -> binance
    symbols: *str*
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pandas.DataFrame
        pair, base\_currency\_name, quote\_currency\_name, market\_url,
        category, reported\_volume\_24h\_share, trust\_score,
    