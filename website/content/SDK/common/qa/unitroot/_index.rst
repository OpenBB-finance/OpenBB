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
common.qa.unitroot(
    data: pandas.core.frame.DataFrame,
    fuller_reg: str = 'c',
    kpss_reg: str = 'c',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        DataFrame of target variable
    fuller_reg : *str*
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : *str*
        Type of regression for KPSS test.  Can be ‘c’,’ct'
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        Dataframe with results of ADF test and KPSS test
