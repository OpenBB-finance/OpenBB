.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgglobal(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

ut crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]

    
* **Returns**

    pandas.DataFrame
        Market_Cap, Volume, Market_Cap_Percentage
    