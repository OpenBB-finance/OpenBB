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
forecast.corr(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns correlation for a given df
    </p>

* **Parameters**

    data: pd.DataFrame
        The df to produce statistics for
    chart: *bool*
       Flag to display chart


* **Returns**

    df: pd.DataFrame
        The df with the new data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forecast.corr(
    dataset: pandas.core.frame.DataFrame,
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot correlation coefficients for dataset features
    </p>

* **Parameters**

    dataset : pd.DataFrame
        The dataset fore calculating correlation coefficients
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    chart: *bool*
       Flag to display chart

