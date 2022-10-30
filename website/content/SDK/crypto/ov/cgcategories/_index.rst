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
       Rank, Name, Change\_1h, Change\_7d, Market\_Cap, Volume\_24h,Coins, Url
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgcategories(
    sort\_filter: str = 'market\_cap\_desc', chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

ries [Source: CoinGecko]

    
* **Returns**

    pandas.DataFrame
       Rank, Name, Change\_1h, Change\_7d, Market\_Cap, Volume\_24h,Coins, Url
    