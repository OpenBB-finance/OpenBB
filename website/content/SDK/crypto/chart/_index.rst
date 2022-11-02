.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load data for Technical Analysis
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.chart(
    prices_df: 'pd.DataFrame',
    to_symbol: 'str' = '',
    from_symbol: 'str' = '',
    source: 'str' = '',
    exchange: 'str' = '',
    interval: 'str' = '',
    external_axes: 'list[plt.Axes] | None' = None, yscale: 'str' = 'linear',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> 'None'
{{< /highlight >}}

* **Parameters**

    prices_df: *pd.DataFrame*
        Cryptocurrency
    to_symbol: *str*
        Coin (only used for chart title), by default ""
    from_symbol: *str*
        Currency (only used for chart title), by default ""
    yscale: *str*
        Scale for y axis of plot Either linear or log
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot
