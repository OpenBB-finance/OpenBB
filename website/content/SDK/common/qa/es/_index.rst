.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets Expected Shortfall for specified stock dataframe
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.qa.es(
    data: pandas.core.frame.DataFrame,
    use_mean: bool = False,
    distribution: str = 'normal',
    percentile: Union[float, int] = 99.9,
    portfolio: bool = False,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data: *pd.DataFrame*
        Data dataframe
    use_mean: *bool*
        If one should use the data mean for calculation
    distribution: *str*
        Type of distribution, options: laplace, student_t, normal
    percentile: Union[float,int]
        VaR percentile
    portfolio: *bool*
        If the data is a portfolio
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    list
        list of ES
    list
        list of historical ES
