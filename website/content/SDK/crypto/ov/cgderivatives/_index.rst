.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cgderivatives(
    sortby: str = 'Rank',
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pandas.DataFrame
        Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread,
        Funding_Rate, Volume_24h,
