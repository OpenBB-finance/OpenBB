.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Kurtosis Indicator
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.qa.kurtosis(
    data: pandas.core.frame.DataFrame,
    window: int = 14,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of targeted data
    window: *int*
        Length of window
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df_kurt : *pd.DataFrame*
        Dataframe of rolling kurtosis
