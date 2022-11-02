.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Print summary statistics
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.qa.summary(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Dataframe to get summary statistics for
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    summary : *pd.DataFrame*
        Summary statistics
