.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for unit roots
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
econometrics.root(
    data: pandas.core.series.Series,
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.Series*
        Series or column of DataFrame of target variable
    fuller_reg : *str*
        Type of regression of ADF test
    kpss_reg : *str*
        Type of regression for KPSS test
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with results of ADF test and KPSS test
