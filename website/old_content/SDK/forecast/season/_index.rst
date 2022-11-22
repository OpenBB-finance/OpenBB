.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forecast.season(
    data: pandas.core.frame.DataFrame,
    column: str = 'close',
    export: str = '',
    m: Optional[int] = None,
    max_lag: int = 24,
    alpha: float = 0.05,
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot seasonality from a dataset
    </p>

* **Parameters**

    data: pd.DataFrame
        The dataframe to plot
    column: str
        The column of the dataframe to analyze
    export: str
        Format to export image
    m: Optional[int]
        Optionally, a time lag to highlight on the plot. Default is none.
    max_lag: int
        The maximal lag order to consider. Default is 24.
    alpha: float
        The confidence interval to display. Default is 0.05.
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
