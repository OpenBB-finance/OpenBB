.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets volume weighted average price (VWAP)
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.ta.vwap(
    data: pandas.core.frame.DataFrame,
    offset: int = 0,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Dataframe of dates and prices
    offset: *int*
        Length of offset
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df_vwap: *pd.DataFrame*
        Dataframe with VWAP data
