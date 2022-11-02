.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Screener Overview
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.screener.screener_data(
    preset_loaded: str = 'top_gainers',
    data_type: str = 'overview',
    limit: int = 10,
    ascend: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    preset_loaded : *str*
        Loaded preset filter
    data_type : *str*
        Data type between: overview, valuation, financial, ownership, performance, technical
    limit : *int*
        Limit of stocks filtered with presets to print
    ascend : *bool*
        Ascended order of stocks filtered to print
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with loaded filtered stocks
