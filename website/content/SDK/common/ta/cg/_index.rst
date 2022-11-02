.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Center of gravity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.cg(
    values: pandas.core.series.Series,
    window: int,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    values: *pd.DataFrame*
        Data to use with close being titled values
    window: *int*
        Length for indicator window
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe of technical indicator
