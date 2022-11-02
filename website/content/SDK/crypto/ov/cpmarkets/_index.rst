.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cpmarkets(
    symbols: str = 'USD',
    sortby: str = 'rank',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbols: *str*
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascend
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pandas.DataFrame
        rank, name, symbol, price, volume_24h, mcap_change_24h,
        pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
