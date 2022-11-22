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
econometrics.norm(
    data: pandas.core.series.Series,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    The distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.
    </p>

* **Parameters**

    data : pd.Series
        A series or column of a DataFrame to test normality for
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing statistics of normality

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.norm(
    data: pandas.core.series.Series,
    dataset: str = '',
    column: str = '',
    plot: bool = False,
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Determine the normality of a timeseries.
    </p>

* **Parameters**

    data: pd.Series
        Series of custom data
    dataset: str
        Dataset name
    column: str
        Column for y data
    plot : bool
        Whether you wish to plot a histogram
    export: str
        Format to export data.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    chart: bool
       Flag to display chart

