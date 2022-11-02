.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get the omega series
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.qa.omega(
    data: pandas.core.frame.DataFrame,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        stock dataframe
    threshold_start: *float*
        annualized target return threshold start of plotted threshold range
    threshold_end: *float*
        annualized target return threshold end of plotted threshold range
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot
