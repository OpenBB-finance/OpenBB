.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Show historical cases and deaths by country
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
alt.covid.stat(
    country, stat: str = 'cases',
    limit: int = 10,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    country: *str*
        Country to get data for
    stat: *str*
        Statistic to get.  Either "cases", "deaths" or "rates"
    limit: *int*
        Number of raw data to show
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot
