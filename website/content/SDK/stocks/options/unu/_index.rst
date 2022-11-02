.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get unusual option activity from fdscanner.com
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.options.unu(
    limit: int = 100,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number to show
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    df: *pd.DataFrame*
        Dataframe containing options information
    last_updated: *pd.Timestamp*
        Timestamp indicated when data was updated from website
