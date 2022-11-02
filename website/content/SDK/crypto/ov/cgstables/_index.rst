.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns top stable coins [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgstables(
    limit: int = 20,
    sortby: str = 'rank',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        How many rows to show
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending

    
* **Returns**

    pandas.DataFrame
        Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d, Url
   