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
forecast.plot(
    data: pandas.core.frame.DataFrame,
    columns: List[str],
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot data from a dataset
    </p>

* **Parameters**

    data: pd.DataFrame
        The dataframe to plot
    columns: List[str]
        The columns to show
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.plot(
    data: pandas.core.frame.DataFrame,
    columns: List[str],
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot data from a dataset
    </p>

* **Parameters**

    data: pd.DataFrame
        The dataframe to plot
    columns: List[str]
        The columns to show
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart

