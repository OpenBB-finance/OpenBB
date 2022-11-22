.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
alt.oss.ross() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get startups from ROSS index [Source: https://runacap.com/]
    </p>

* **Returns**

    pandas.DataFrame:
        list of startups

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.oss.ross(
    limit: int = 10,
    sortby: str = 'Stars AGR [%]', ascend: bool = False,
    show_chart: bool = False,
    show_growth: bool = True,
    chart_type: str = 'stars',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display list of startups from ross index [Source: https://runacap.com/]
    </p>

* **Parameters**

    limit: int
        Number of startups to search
    sortby: str
        Key by which to sort data. Default: Stars AGR [%]
    ascend: bool
        Flag to sort data descending
    show_chart: bool
        Flag to show chart with startups
    show_growth: bool
        Flag to show growth line chart
    chart_type: str
        Chart type {stars,forks}
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

