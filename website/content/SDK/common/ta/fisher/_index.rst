.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Fisher Transform
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.fisher(
    high_vals: pandas.core.series.Series,
    low_vals: pandas.core.series.Series,
    window: int = 14,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    high_vals: *pd.Series*
        High values
    low_vals: *pd.Series*
        Low values
    window: *int*
        Length for indicator window
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df_ta: *pd.DataFrame*
        Dataframe of technical indicator
