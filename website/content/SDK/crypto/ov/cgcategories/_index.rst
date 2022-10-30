.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns top crypto categories [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgcategories(
    sort_filter: str = 'market_cap_desc',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

ries [Source: CoinGecko]

    
* **Returns**

    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    