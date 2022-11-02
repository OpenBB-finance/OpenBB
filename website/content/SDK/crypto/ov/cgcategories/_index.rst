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

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cgcategories(
    sort_filter: str = 'market_cap_desc',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
