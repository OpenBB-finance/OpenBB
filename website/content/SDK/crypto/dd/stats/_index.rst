.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.stats(
    symbol: str,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    
* **Returns**

    pd.DataFrame
        24h stats for chosen trading pair
    