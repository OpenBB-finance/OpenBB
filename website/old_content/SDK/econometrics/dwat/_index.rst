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
econometrics.dwat(
    residual: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate test statistics for Durbing Watson autocorrelation
    </p>

* **Parameters**

    residual : OLS Model
        Model containing residual values.
    chart: bool
       Flag to display chart


* **Returns**

    Test statistic of the Durbin Watson test.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.dwat(
    dependent_variable: pandas.core.series.Series,
    residual: pandas.core.frame.DataFrame,
    plot: bool = False,
    export: str = '',
    external_axes: Optional[List[axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show Durbin-Watson autocorrelation tests
    </p>

* **Parameters**

    dependent_variable : pd.Series
        The dependent variable.
    residual : OLS Model
        The residual of an OLS model.
    plot : bool
        Whether to plot the residuals
    export : str
        Format to export data
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    chart: bool
       Flag to display chart

