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
common.ta.cg(
    values: pandas.core.series.Series,
    window: int,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Center of gravity
    </p>

* **Parameters**

    values: pd.DataFrame
        Data to use with close being titled values
    window: int
        Length for indicator window
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe of technical indicator

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.ta.cg(
    data: pandas.core.series.Series,
    window: int = 14,
    symbol: str = '',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display center of gravity Indicator
    </p>

* **Parameters**

    data : pd.Series
        Series of values
    window : int
        Length of window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

