.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets value at risk for specified stock dataframe
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
common.qa.var(
    data: pandas.core.frame.DataFrame,
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: Union[int, float] = 99.9,
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
    adjusted_var: *bool*
        If one should return VaR adjusted for skew and kurtosis
    student_t: *bool*
        If one should use the student-t distribution
    percentile: Union[int,float]
        VaR percentile
    portfolio: *bool*
        If the data is a portfolio
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    list
        list of VaR
    list
        list of historical VaR
