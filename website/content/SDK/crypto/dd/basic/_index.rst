.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Basic coin information [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.basic(
    symbol: str = 'btc-bitcoin', chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Coin id

    
* **Returns**

    pd.DataFrame
        Metric, Value
    