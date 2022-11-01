.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of top exchanges from CoinGecko API [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.exchanges(
    sortby: str = 'name',
    ascend: bool = False,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending

    
* **Returns**

    pandas.DataFrame
        Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC, Url
    