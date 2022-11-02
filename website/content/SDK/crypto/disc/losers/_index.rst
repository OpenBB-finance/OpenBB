.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.disc.losers(
    interval: str = '1h',
    limit: int = 50,
    sortby: str = 'market_cap_rank',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    interval: *str*
        Time interval by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    limit: *int*
        Number of records to display
    sortby: *str*
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Top Losers  - coins which lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url
